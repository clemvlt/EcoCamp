import os
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64

# Configuration
PASSWORD = b"ecocamp"
FILE_TO_ENCRYPT = "config2.json"

# 1. Générer un grain de sel aléatoire de 16 octets
salt = os.urandom(16)

# 2. Configurer la dérivation de clé (KDF)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)

# 3. Générer la clé Fernet à partir du mot de passe + sel
key = base64.urlsafe_b64encode(kdf.derive(PASSWORD))
fernet = Fernet(key)

# 4. Chiffrer les données
with open(FILE_TO_ENCRYPT, "rb") as f:
    data = f.read()

encrypted_data = fernet.encrypt(data)

# 5. Sauvegarder le SEL + les DONNÉES dans le même fichier
with open("config.enc", "wb") as f:
    f.write(salt + encrypted_data)

print("Fichier config.enc salé et chiffré !")