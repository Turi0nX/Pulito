import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Set

# Aggiungiamo la root del backend al path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from generator.config import (
    INPUT_LIST_FILES,
    LISTS_DIR,
    OUTPUT_DIR,
    KEYS_DIR,
    VERSION,
)
from generator.downloader import refresh_remote_lists
from generator.manifest_builder import build_manifest
from generator.parser import parse_list
from generator.rules_builder import build_base_list, build_pro_list
from generator.writer import write_json
from sign_manifest import embed_signature

logger = logging.getLogger(__name__)

# --- COSTANTI DI SICUREZZA ---
MIN_RULES_THRESHOLD_BASE = 1000  
MIN_RULES_THRESHOLD_PRO = 30000 
MAX_RULES_WARNING = 150000 

def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

def load_custom_whitelist() -> Set[str]:
    """
    Carica la whitelist locale (siti che NON vogliamo bloccare).
    """
    whitelist_path = LISTS_DIR / "custom_allow.txt"
    if not whitelist_path.exists():
        return set()
    
    with whitelist_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Riutilizziamo il parser per pulire le righe (rimuovere commenti, spazi)
    return set(parse_list(lines))

def validate_output(file_path: Path, min_rules: int) -> int:
    """
    Controlla che il file JSON esista, sia una LISTA valida e abbia regole sufficienti.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"❌ Output file missing: {file_path}")
    
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"❌ Invalid JSON in {file_path}")
            
    if not isinstance(data, list):
        raise ValueError(f"❌ Output format error: Safari requires a LIST [...], got {type(data)}")
        
    count = len(data)
    logger.info(f"📊 Validation: {file_path.name} contains {count} rules.")
    
    if count < min_rules:
        raise RuntimeError(f"❌ SAFETY STOP: Too few rules ({count} < {min_rules}). Downloads might have failed.")
    
    if count > MAX_RULES_WARNING:
        logger.warning(f"⚠️  WARNING: {file_path.name} has {count} rules. Approaching iOS limit!")
        
    return count

def main() -> None:
    configure_logging()
    logger.info("🚀 Starting Pulito Generator (Corrected Format)...")

    # 1. Carica la Whitelist Locale (Priorità Massima)
    whitelist = load_custom_whitelist()
    if whitelist:
        logger.info(f"🛡️  Loaded {len(whitelist)} whitelisted domains.")

    # 2. Download Liste Remote
    logger.info("📥 Refreshing remote public lists...")
    remote_files = refresh_remote_lists()

    # Usiamo un SET per evitare duplicati automaticamente
    all_domains_set: Set[str] = set()

    # 3. Parsing Remote
    for name, path in remote_files.items():
        if not path: 
            logger.warning(f"⚠️  Download failed for {name}, skipping.")
            continue 
        try:
            with path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
            parsed = parse_list(lines)
            all_domains_set.update(parsed) # .update aggiunge solo i nuovi
        except Exception as e:
            logger.error(f"❌ Error parsing {name}: {e}")

    # 4. Parsing Local Blocklist
    for relative_path in INPUT_LIST_FILES:
        path = LISTS_DIR / relative_path
        if not path.is_file():
            continue
        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        parsed = parse_list(lines)
        all_domains_set.update(parsed)

    # 5. OTTIMIZZAZIONE FINALE (The God-Tier Touch)
    # - Rimuovi i domini in whitelist
    # - Ordina alfabeticamente (Determinismo)
    initial_count = len(all_domains_set)
    all_domains_set = all_domains_set - whitelist
    final_domains = sorted(list(all_domains_set))
    
    logger.info(f"🧹 Optimization: {initial_count} raw -> {len(final_domains)} unique domains (sorted & whitelisted).")

    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- BASE GENERATION ---
    base_rules = build_base_list(final_domains, version=VERSION)
    
    base_filename = "blockerList_base.json"
    base_path = output_dir / base_filename
    logger.info("Writing BASE blocker list to %s", base_path)
    write_json(base_rules, base_path)
    
    validate_output(base_path, MIN_RULES_THRESHOLD_BASE)

    base_manifest = build_manifest("base", base_filename)
    base_manifest_path = output_dir / "manifest_base.json"
    write_json(base_manifest, base_manifest_path)

    # --- PRO GENERATION ---
    pro_rules = build_pro_list(final_domains, version=VERSION)
    
    pro_filename = "blockerList_pro.json"
    pro_path = output_dir / pro_filename
    logger.info("Writing PRO blocker list to %s", pro_path)
    write_json(pro_rules, pro_path)

    validate_output(pro_path, MIN_RULES_THRESHOLD_PRO)

    pro_manifest = build_manifest("pro", pro_filename)
    pro_manifest_path = output_dir / "manifest_pro.json"
    write_json(pro_manifest, pro_manifest_path)

    # --- SIGNING ---
    logger.info("🔐 Signing manifests...")
    privkey_path = KEYS_DIR / "pulito_privkey.pem"
    
    embed_signature(privkey_path, base_manifest_path)
    embed_signature(privkey_path, pro_manifest_path)

    logger.info("✅ BUILD COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"🔥 FATAL ERROR: {e}")
        sys.exit(1)