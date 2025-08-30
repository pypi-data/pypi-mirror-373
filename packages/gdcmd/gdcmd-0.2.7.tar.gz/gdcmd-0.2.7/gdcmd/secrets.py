import base64
import json
import os
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key


def get_repository_path():
    current_path = Path(__file__).resolve()
    while current_path.parent != current_path:
        if (current_path / '.git').exists():
            return current_path
        current_path = current_path.parent
    return Path.cwd()


def rsa_generate():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_pem, public_pem


def hybrid_encrypt(public_key_pem: bytes, plaintext: bytes) -> str:
    public_key = load_pem_public_key(public_key_pem)
    aes_key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    payload = {
        "key": base64.b64encode(encrypted_key).decode('utf-8'),
        "nonce": base64.b64encode(nonce).decode('utf-8'),
        "data": base64.b64encode(ciphertext).decode('utf-8')
    }
    return json.dumps(payload)


def hybrid_decrypt(private_key_pem: bytes, encrypted_payload: str) -> bytes:
    private_key = load_pem_private_key(private_key_pem, password=None)
    payload = json.loads(encrypted_payload)
    aes_key = private_key.decrypt(
        base64.b64decode(payload["key"]),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    aesgcm = AESGCM(aes_key)
    nonce = base64.b64decode(payload["nonce"])
    ciphertext = base64.b64decode(payload["data"])
    return aesgcm.decrypt(nonce, ciphertext, None)


def decrypt_secrets(files: list[str]):
    repo_path = get_repository_path()
    print(f"🔍  Found repo at: {repo_path}")
    private_key_path = repo_path / ".secrets" / "key.pem"
    if not private_key_path.exists():
        print(f"❌ Cannot decrypt files because you don't have private key {private_key_path}, check passwork.me")
        return
    if len(files) == 0:
        files = list(repo_path.rglob('*.encrypted'))
        if len(files) == 0:
            print("❌ No .encrypted files found in the repository")
            return
    full_paths = [Path(file).resolve() for file in files]
    for file in full_paths:
        if not file.exists():
            print(f"❌ File {file} does not exist, skipping")
            continue
        private_pem = private_key_path.read_bytes()
        encrypted_content = file.read_text(encoding='utf-8')
        decrypted = hybrid_decrypt(private_pem, encrypted_content)
        secret_file_path = file.with_suffix('')
        if secret_file_path.exists():
            old_content = secret_file_path.read_bytes()
            if old_content != decrypted:
                print(f"Overwriting old content with new one")
            else:
                print(f"✅  Decrypted content is the same as existing content, skipping write to {secret_file_path}")
                continue
        secret_file_path.write_bytes(decrypted)
        print(f"✅  Generated file {secret_file_path} from {file}")


def create_new_key():
    repo_path = get_repository_path()
    print(f"🔍 Found repo at: {repo_path}")
    private_key_path = repo_path / ".secrets" / "key.pem"
    public_key_path = repo_path / "key.pub"
    if private_key_path.exists():
        print(f"❌ Cannot create new key because you already have a private key {private_key_path}")
        return
    private_key_path.parent.mkdir(parents=True, exist_ok=True)
    pem_private, pem_public = rsa_generate()
    private_key_path.write_bytes(pem_private)
    public_key_path.write_bytes(pem_public)
    print(f"✅  Generated private key: {private_key_path}")
    print(f"✅  Generated public key: {public_key_path}")


def encrypt_secrets(files: list[str]):
    repo_path = get_repository_path()
    print(f"🔍 Found repo at: {repo_path}")
    public_key_path = repo_path / "key.pub"
    if not public_key_path.exists():
        print(f"❌ Cannot encrypt secrets file because you don't have public key {public_key_path}, check passwork.me")
        return
    if len(files) == 0:
        files = list(repo_path.rglob('*.encrypted'))
        files = [str(file).replace('.encrypted', '') for file in files if file.is_file()]
        if len(files) == 0:
            print("❌ No files found in the repository")
            return
    full_paths = [Path(file).resolve() for file in files]
    for file in full_paths:
        if not file.exists():
            print(f"❌ File {file} does not exist, skipping")
            continue
        public_pem = public_key_path.read_bytes()
        content = file.read_bytes()
        encrypted = hybrid_encrypt(public_pem, content)
        encrypted_file_path = file.with_suffix(file.suffix + '.encrypted')
        encrypted_file_path.write_text(encrypted, encoding='utf-8')
        print(f"✅  Encrypted file created: {encrypted_file_path}")
