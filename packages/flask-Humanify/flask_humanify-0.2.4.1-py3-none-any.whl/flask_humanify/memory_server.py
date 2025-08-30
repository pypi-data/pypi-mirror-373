import json
import logging
import socket
import time
import threading
import os
import importlib.metadata
import importlib.resources
import urllib.request
import urllib.error
import gzip
import pickle
import random
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from netaddr import IPNetwork, IPAddress

logger = logging.getLogger(__name__)

try:
    importlib.metadata.distribution("flask-humanify")
    BASE_DIR = importlib.resources.files("flask_humanify")
except importlib.metadata.PackageNotFoundError:
    BASE_DIR = Path(__file__).parent

BASE_DIR = Path(str(BASE_DIR)) if not isinstance(BASE_DIR, Path) else BASE_DIR
DATASET_DIR = BASE_DIR / "datasets"
DATASET_DIR.mkdir(parents=True, exist_ok=True)
IPSET_DATA_PATH = str(DATASET_DIR / "ipset.json")
SECRET_KEY_FILE = BASE_DIR / "secret_key.bin"

CAPTCHA_DATASETS = {
    "image": {
        "keys": (
            "https://raw.githubusercontent.com/tn3w/Captcha_Datasets/"
            "refs/heads/master/datasets/keys.pkl"
        ),
        "animals": (
            "https://raw.githubusercontent.com/tn3w/Captcha_Datasets/"
            "refs/heads/master/datasets/animals.pkl"
        ),
        "ai_dogs": (
            "https://raw.githubusercontent.com/tn3w/Captcha_Datasets/"
            "refs/heads/master/datasets/ai-dogs.pkl"
        ),
    },
    "audio": {
        "characters": (
            "https://raw.githubusercontent.com/librecap/audiocaptcha/"
            "refs/heads/main/characters/characters.pkl"
        )
    },
}


class MemoryServer:
    """A singleton memory server that manages IP sets and provides lookup functionality."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, port: int = 9876, data_path: Optional[str] = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.initialized = False
            return cls._instance

    def __init__(self, port: int = 9876, data_path: Optional[str] = None):
        if getattr(self, "initialized", False):
            return

        self.port = port
        self.data_path = data_path or IPSET_DATA_PATH
        self._data_lock = threading.Lock()
        self._socket_lock = threading.Lock()
        self.failed_attempts: Dict[str, Tuple[datetime, int]] = {}
        self.ip_to_groups: Dict[str, List[str]] = {}
        self.cidrs_to_ips: Dict[IPNetwork, List[str]] = {}
        self.last_update: Optional[datetime] = None
        self.server_socket: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = threading.Event()
        self.captcha_data = {"image": {}, "audio": {}}
        self.current_datasets: Dict[str, Optional[str]] = {"image": None, "audio": None}
        self.secret_key: bytes = self._load_or_create_secret_key()
        self.initialized = True

    def _load_or_create_secret_key(self) -> bytes:
        """Load the secret key from file or create a new one if it doesn't exist."""
        if SECRET_KEY_FILE.exists():
            with open(SECRET_KEY_FILE, "rb") as f:
                return f.read()

        secret_key = secrets.token_bytes(32)
        with open(SECRET_KEY_FILE, "wb") as f:
            f.write(secret_key)
        return secret_key

    def is_server_running(self) -> bool:
        """Check if the server is already running on the specified port."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("127.0.0.1", self.port)) == 0
        except (ConnectionRefusedError, OSError):
            return False

    def _download_data(self, force: bool = False) -> bool:
        """Download IP set data from GitHub and update the timestamp."""
        if not force and os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "_timestamp" in data:
                    timestamp = datetime.fromisoformat(data["_timestamp"])
                    if datetime.now() - timestamp < timedelta(days=7):
                        return True
            except (json.JSONDecodeError, KeyError, ValueError, OSError):
                pass

        try:
            url = "https://raw.githubusercontent.com/tn3w/IPSet/refs/heads/master/ipset.json"
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            data["_timestamp"] = datetime.now().isoformat()
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            return True
        except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
            logger.error("Error downloading IP data: %s", e)
            return False

    def _download_captcha(self, url: str, name: str) -> str:
        """Download a captcha dataset from the internet."""
        file_path = DATASET_DIR / f"{name}.pkl"
        if file_path.exists():
            return str(file_path)

        try:
            urllib.request.urlretrieve(url, file_path)
            return str(file_path)
        except (urllib.error.URLError, OSError) as e:
            logger.error("Failed to download %s: %s", name, e)
            return ""

    def _load_data(self) -> bool:
        """Load IP set data into memory."""
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            with self._data_lock:
                self.last_update = datetime.fromisoformat(
                    data.pop("_timestamp", datetime.now().isoformat())
                )

                self.ip_to_groups.clear()
                self.cidrs_to_ips.clear()

                for group, ips in data.items():
                    for ip in ips:
                        if "/" in ip:
                            try:
                                cidr = IPNetwork(ip)
                                self.cidrs_to_ips.setdefault(cidr, []).append(group)
                            except (ValueError, TypeError):
                                continue
                        else:
                            self.ip_to_groups.setdefault(ip, []).append(group)
            return True
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Error loading IP data: %s", e)
            return False

    def _load_captcha_datasets(
        self, image: Optional[str] = None, audio: Optional[str] = None
    ) -> bool:
        """Load captcha datasets into memory."""
        if (
            self.current_datasets["image"] == image
            and self.current_datasets["audio"] == audio
            and (self.captcha_data["image"] or self.captcha_data["audio"])
        ):
            return True

        success = False

        if image and image in CAPTCHA_DATASETS["image"]:
            path = self._download_captcha(CAPTCHA_DATASETS["image"][image], image)
            if path:
                try:
                    with open(path, "rb") as f:
                        data = pickle.load(f)
                    if data.get("type") == "image":
                        keys = data.get("keys", {})
                        if keys:
                            first_key = next(iter(keys))
                            if keys[first_key] and not keys[first_key][0].startswith(
                                b"\x89PNG"
                            ):
                                keys = {
                                    k: [gzip.decompress(img) for img in v]
                                    for k, v in keys.items()
                                }
                            data["keys"] = keys
                        self.captcha_data["image"] = data
                        self.current_datasets["image"] = image
                        success = True
                except (pickle.UnpicklingError, OSError, gzip.BadGzipFile) as e:
                    logger.error("Failed to load image dataset %s: %s", image, e)

        if audio and audio in CAPTCHA_DATASETS["audio"]:
            path = self._download_captcha(CAPTCHA_DATASETS["audio"][audio], audio)
            if path:
                try:
                    with open(path, "rb") as f:
                        self.captcha_data["audio"] = pickle.load(f)
                    self.current_datasets["audio"] = audio
                    success = True
                except (pickle.UnpicklingError, OSError) as e:
                    logger.error("Failed to load audio dataset %s: %s", audio, e)

        return success

    def _check_update(self) -> None:
        """Check if data needs updating and update if necessary."""
        if self.last_update is None or datetime.now() - self.last_update > timedelta(
            days=7
        ):

            def update_task():
                if self._download_data(True):
                    self._load_data()

            threading.Thread(target=update_task, daemon=True).start()

    def find_groups(self, ip: str) -> List[str]:
        """Find all groups matching the given IP."""
        self._check_update()

        with self._data_lock:
            groups = list(self.ip_to_groups.get(ip, []))

            try:
                ip_obj = IPAddress(ip)
                for cidr, cidr_groups in self.cidrs_to_ips.items():
                    if cidr.version == ip_obj.version and ip_obj in cidr:
                        groups.extend(g for g in cidr_groups if g not in groups)
            except (ValueError, TypeError):
                pass

            return groups

    def get_images(
        self,
        dataset: str = "ai_dogs",
        count: int = 9,
        correct_range: Union[int, Tuple[int, int]] = (2, 3),
        preview: bool = False,
    ) -> Tuple[List[bytes], str, str]:
        """Get captcha images for verification."""
        if not self._load_captcha_datasets(image=dataset):
            return [], "", ""

        data = self.captcha_data["image"]
        if not data or data.get("type") != "image" or not data.get("keys"):
            return [], "", ""

        keys = data["keys"]
        correct_key = (
            next(iter(keys)) if len(keys) == 2 else random.choice(list(keys.keys()))
        )
        correct_imgs = keys[correct_key]
        incorrect_imgs = [
            img for k, imgs in keys.items() for img in imgs if k != correct_key
        ]

        if not correct_imgs or not incorrect_imgs:
            return [], "", ""

        num_correct = (
            correct_range
            if isinstance(correct_range, int)
            else random.randint(*correct_range)
        )

        selected_correct = random.sample(
            correct_imgs, min(num_correct, len(correct_imgs))
        )
        selected_incorrect = random.sample(
            incorrect_imgs, min(count - len(selected_correct), len(incorrect_imgs))
        )

        combined = [(img, True) for img in selected_correct] + [
            (img, False) for img in selected_incorrect
        ]
        random.shuffle(combined)

        if combined:
            images, is_correct = zip(*combined)
        else:
            images, is_correct = (), ()

        correct_indices = "".join(
            str(i) for i, correct in enumerate(is_correct) if correct
        )

        if preview:
            images = tuple([random.choice(correct_imgs)]) + tuple(images)

        return list(images), correct_indices, correct_key

    def get_audio(
        self, dataset: str = "characters", chars: int = 6, lang: str = "en"
    ) -> Tuple[List[bytes], str]:
        """Get captcha audio for verification."""
        if not self._load_captcha_datasets(audio=dataset):
            return [], ""

        data = self.captcha_data["audio"]
        if not data or data.get("type") != "audio" or not data.get("keys"):
            return [], ""

        keys = data["keys"]
        selected = random.choices(list(keys.keys()), k=chars)
        correct_str = "".join(selected)

        try:
            audio_files = [keys[char][lang] for char in selected]
            return audio_files, correct_str
        except KeyError:
            return [], ""

    def record_failure(self, ip_hash: str) -> int:
        """Record a failed attempt for an IP hash and return total recent failures."""
        now = datetime.now()
        cutoff = now - timedelta(hours=1)

        self.failed_attempts = {
            k: v for k, v in self.failed_attempts.items() if v[0] > cutoff
        }

        if (
            ip_hash in self.failed_attempts
            and self.failed_attempts[ip_hash][0] > cutoff
        ):
            count = self.failed_attempts[ip_hash][1] + 1
        else:
            count = 1

        self.failed_attempts[ip_hash] = (now, count)
        return count

    def is_limited(self, ip_hash: str) -> bool:
        """Check if the IP hash has reached the failed attempts limit."""
        cutoff = datetime.now() - timedelta(hours=1)
        return (
            ip_hash in self.failed_attempts
            and self.failed_attempts[ip_hash][0] > cutoff
            and self.failed_attempts[ip_hash][1] >= 3
        )

    def _handle_client(self, client: socket.socket, addr: Tuple[str, int]) -> None:
        """Handle client connection and queries."""
        try:
            client.settimeout(30.0)
            while True:
                try:
                    data = client.recv(1024).decode("utf-8").strip()
                    if not data:
                        break
                except socket.timeout:
                    break

                response = ""

                if data.startswith("CHECK_LIMIT:"):
                    response = str(self.is_limited(data[12:])).lower()
                elif data.startswith("FAILED_ATTEMPT:"):
                    response = str(self.record_failure(data[15:]))
                elif data.startswith("IPSET:"):
                    response = json.dumps(self.find_groups(data[6:]))
                elif data.startswith("SECRET_KEY"):
                    response = json.dumps(self.secret_key.hex())
                elif data.startswith("IMAGE_CAPTCHA:"):
                    parts = data.split(":")
                    dataset = parts[1] if len(parts) > 1 and parts[1] else "ai_dogs"
                    count = (
                        int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 9
                    )
                    correct = (
                        int(parts[3])
                        if len(parts) > 3 and parts[3].isdigit()
                        else (2, 3)
                    )
                    preview = len(parts) > 4 and parts[4].lower() == "true"

                    images, indices, subject = self.get_images(
                        dataset, count, correct, preview
                    )
                    response = json.dumps(
                        {
                            "status": "success" if images else "error",
                            "correct_indexes": indices,
                            "subject": subject,
                            "num_images": len(images),
                        }
                    )

                    client.send(f"{response}\n".encode("utf-8"))
                    for img in images:
                        client.send(len(img).to_bytes(4, "big") + img)
                    continue

                elif data.startswith("AUDIO_CAPTCHA:"):
                    parts = data.split(":")
                    dataset = parts[1] if len(parts) > 1 and parts[1] else "characters"
                    chars = (
                        int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 6
                    )
                    lang = parts[3] if len(parts) > 3 else "en"

                    audio, correct = self.get_audio(dataset, chars, lang)
                    response = json.dumps(
                        {
                            "status": "success" if audio else "error",
                            "correct_chars": correct,
                            "num_files": len(audio),
                        }
                    )

                    client.send(f"{response}\n".encode("utf-8"))
                    for a in audio:
                        client.send(len(a).to_bytes(4, "big") + a)
                    continue
                else:
                    response = json.dumps(self.find_groups(data))

                client.send(f"{response}\n".encode("utf-8"))

        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            logger.error("Client error %s: %s", addr, e)
        finally:
            client.close()

    def run(
        self,
        image_dataset: Optional[str] = "ai_dogs",
        audio_dataset: Optional[str] = "characters",
    ) -> None:
        """Run the memory server."""
        if self.is_server_running():
            logger.info("Server already running on port %s", self.port)
            return

        if not os.path.exists(self.data_path) and not self._download_data():
            logger.error("Failed to download data")
            return

        if not self._load_data():
            logger.error("Failed to load data")
            return

        self._check_update()
        self._load_captcha_datasets(image_dataset, audio_dataset)

        try:
            with self._socket_lock:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.settimeout(60.0)
                self.server_socket.bind(("0.0.0.0", self.port))
                self.server_socket.listen(10)
                self.running.set()

            logger.info("Server started on port %s", self.port)

            while self.running.is_set():
                try:
                    client, addr = self.server_socket.accept()
                    threading.Thread(
                        target=self._handle_client, args=(client, addr), daemon=True
                    ).start()
                except socket.timeout:
                    continue
                except (ConnectionResetError, OSError) as e:
                    if self.running.is_set():
                        logger.error("Accept error: %s", e)
                    time.sleep(0.1)

        except (OSError, socket.error) as e:
            logger.error("Server error: %s", e)
        finally:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except (OSError, socket.error):
                    pass

    def start(
        self,
        image_dataset: Optional[str] = "ai_dogs",
        audio_dataset: Optional[str] = "characters",
    ) -> None:
        """Start the server in a background thread."""
        with self._socket_lock:
            if self.server_thread and self.server_thread.is_alive():
                return
            self.running.set()
            self.server_thread = threading.Thread(
                target=self.run, args=(image_dataset, audio_dataset), daemon=True
            )
            self.server_thread.start()

    def stop(self) -> None:
        """Stop the server."""
        self.running.clear()
        if self.server_socket:
            try:
                self.server_socket.close()
            except (OSError, socket.error):
                pass


class MemoryClient:
    """Client to connect to the MemoryServer."""

    def __init__(self, host: str = "127.0.0.1", port: int = 9876):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None

    def connect(self) -> bool:
        """Connect to the memory server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.host, self.port))
            return True
        except (ConnectionRefusedError, OSError) as e:
            logger.error("Connection failed: %s", e)
            return False

    def _send_recv(self, command: str) -> str:
        """Send command and receive response."""
        if not self.socket and not self.connect():
            return ""

        try:
            if self.socket:
                self.socket.send(f"{command}\n".encode("utf-8"))
                return self.socket.recv(4096).decode("utf-8").strip()
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            logger.error("Communication error: %s", e)
            try:
                if self.socket:
                    self.socket.close()
            except (OSError, socket.error):
                pass
            self.socket = None
            if self.connect():
                try:
                    if self.socket:
                        self.socket.send(f"{command}\n".encode("utf-8"))
                        return self.socket.recv(4096).decode("utf-8").strip()
                except (ConnectionResetError, BrokenPipeError, OSError):
                    pass
            return ""
        return ""

    def is_attempt_limit_reached(self, ip_hash: str) -> bool:
        """Check if the IP hash has reached the failed attempts limit."""
        return self._send_recv(f"CHECK_LIMIT:{ip_hash}") == "true"

    def record_failed_attempt(self, ip_hash: str) -> int:
        """Record a failed captcha attempt for a hashed IP."""
        try:
            return int(self._send_recv(f"FAILED_ATTEMPT:{ip_hash}"))
        except (ValueError, TypeError):
            return 0

    def lookup_ip(self, ip: str) -> List[str]:
        """Look up an IP in the memory server."""
        try:
            response = self._send_recv(f"IPSET:{ip}")
            return json.loads(response) if response else []
        except (json.JSONDecodeError, TypeError):
            return []

    def get_secret_key(self) -> bytes:
        """Get the secret key from the memory server."""
        try:
            response = self._send_recv("SECRET_KEY")
            parsed = json.loads(response) if response else ""
            return bytes.fromhex(parsed) if isinstance(parsed, str) else b""
        except (json.JSONDecodeError, ValueError, TypeError):
            return b""

    def get_captcha_images(
        self,
        dataset: Optional[str] = None,
        count: int = 9,
        correct: Union[int, Tuple[int, int]] = (2, 3),
        preview: bool = False,
    ) -> Tuple[List[bytes], str, str]:
        """Get captcha images from the memory server."""
        if not self.socket and not self.connect():
            return [], "", ""

        try:
            cmd = f"IMAGE_CAPTCHA:{dataset or ''}:{count}:{correct}:{preview}"
            if self.socket:
                self.socket.send(f"{cmd}\n".encode("utf-8"))

                json_data = b""
                while True:
                    chunk = self.socket.recv(1)
                    if not chunk or chunk == b"\n":
                        break
                    json_data += chunk

                response = json.loads(json_data.decode("utf-8"))
                if response.get("status") != "success":
                    return [], "", ""

                images = []
                for _ in range(response.get("num_images", 0)):
                    size = int.from_bytes(self.socket.recv(4), "big")
                    img_data = b""
                    while len(img_data) < size:
                        chunk = self.socket.recv(min(size - len(img_data), 4096))
                        if not chunk:
                            break
                        img_data += chunk
                    images.append(img_data)

                return (
                    images,
                    response.get("correct_indexes", ""),
                    response.get("subject", ""),
                )
            return [], "", ""
        except (json.JSONDecodeError, ConnectionResetError, OSError) as e:
            logger.error("Error getting images: %s", e)
            return [], "", ""

    def get_captcha_audio(
        self, dataset: Optional[str] = None, chars: int = 6, lang: str = "en"
    ) -> Tuple[List[bytes], str]:
        """Get captcha audio from the memory server."""
        if not self.socket and not self.connect():
            return [], ""

        try:
            cmd = f"AUDIO_CAPTCHA:{dataset or ''}:{chars}:{lang}"
            if self.socket:
                self.socket.send(f"{cmd}\n".encode("utf-8"))

                json_data = b""
                while True:
                    chunk = self.socket.recv(1)
                    if not chunk or chunk == b"\n":
                        break
                    json_data += chunk

                response = json.loads(json_data.decode("utf-8"))
                if response.get("status") != "success":
                    return [], ""

                audio_files = []
                for _ in range(response.get("num_files", 0)):
                    size = int.from_bytes(self.socket.recv(4), "big")
                    audio_data = b""
                    while len(audio_data) < size:
                        chunk = self.socket.recv(min(size - len(audio_data), 4096))
                        if not chunk:
                            break
                        audio_data += chunk
                    audio_files.append(audio_data)

                return audio_files, response.get("correct_chars", "")
            return [], ""
        except (json.JSONDecodeError, ConnectionResetError, OSError) as e:
            logger.error("Error getting audio: %s", e)
            return [], ""

    def close(self) -> None:
        """Close the connection to the memory server."""
        if self.socket:
            try:
                self.socket.close()
            except (OSError, socket.error):
                pass
            self.socket = None


def ensure_server_running(
    port: int = 9876,
    data_path: Optional[str] = None,
    image_dataset: Optional[str] = None,
    audio_dataset: Optional[str] = None,
) -> None:
    """Ensure that the memory server is running."""
    server = MemoryServer(port, data_path)
    server.start(image_dataset, audio_dataset)
    while not server.is_server_running():
        time.sleep(0.1)
