import json
import base64
import logging
from pathlib import Path

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

logger = logging.getLogger(__name__)

def embed_signature(privkey_path: Path, manifest_path: Path) -> None:
    """
    Legge il manifest JSON, firma il campo 'blocker_list_hash' 
    e aggiunge il campo 'signature' al JSON stesso.
    """
    if not privkey_path.exists():
        logger.warning(f" Private key not found at {privkey_path}. Skipping signature.")
        return

    # 1. Carica la chiave privata
    with open(privkey_path, 'rb') as f:
        key = RSA.import_key(f.read())

    # 2. Leggi il Manifest esistente
    with open(manifest_path, 'r') as f:
        data = json.load(f)

    # 3. Prepara il payload da firmare (l'hash della lista)
    if 'blocker_list_hash' not in data:
        logger.error(f" Manifest {manifest_path.name} missing 'blocker_list_hash'. Cannot sign.")
        return
        
    payload = data['blocker_list_hash'].encode('utf-8')

    # 4. Calcola la firma
    h = SHA256.new(payload)
    signature = pkcs1_15.new(key).sign(h)
    
    # Codifica in Base64 per metterla nel JSON
    signature_b64 = base64.b64encode(signature).decode('utf-8')

    # 5. Aggiungi la firma al dizionario
    data['signature'] = signature_b64

    # 6. Sovrascrivi il file JSON
    with open(manifest_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"🔐 Signed manifest: {manifest_path.name}")