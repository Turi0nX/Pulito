import logging
from pathlib import Path

from generator.config import (
    INPUT_LIST_FILES,
    LISTS_DIR,
    OUTPUT_DIR,
    VERSION,
)
from generator.downloader import refresh_remote_lists
from generator.manifest_builder import build_manifest
from generator.parser import parse_list
from generator.rules_builder import build_base_list, build_pro_list
from generator.writer import write_json

logger = logging.getLogger(__name__)


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main() -> None:
    configure_logging()

    logger.info("Refreshing remote public lists...")
    remote_files = refresh_remote_lists()

    all_domains: list[str] = []

    # Remote lists
    for name, path in remote_files.items():
        logger.info("Parsing remote list %s at %s", name, path)
        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        parsed = parse_list(lines)
        logger.info("Parsed %d domains from %s", len(parsed), name)
        all_domains.extend(parsed)

    # Local custom
    for relative_path in INPUT_LIST_FILES:
        path = LISTS_DIR / relative_path
        logger.info("Reading local list file: %s", path)

        if not path.is_file():
            logger.info("Local list file not found, skipping: %s", path)
            continue

        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        parsed = parse_list(lines)
        logger.info("Parsed %d domains from local %s", len(parsed), path)
        all_domains.extend(parsed)

    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- BASE ---
    base = build_base_list(all_domains, version=VERSION)
    base_filename = "blockerList_base.json"
    base_path = output_dir / base_filename
    logger.info("Writing BASE blocker list to %s", base_path)
    write_json(base, base_path)

    base_manifest = build_manifest("base", base_filename)
    base_manifest_path = output_dir / "manifest_base.json"
    logger.info("Writing BASE manifest to %s", base_manifest_path)
    write_json(base_manifest, base_manifest_path)

    # --- PRO ---
    pro = build_pro_list(all_domains, version=VERSION)
    pro_filename = "blockerList_pro.json"
    pro_path = output_dir / pro_filename
    logger.info("Writing PRO blocker list to %s", pro_path)
    write_json(pro, pro_path)

    pro_manifest = build_manifest("pro", pro_filename)
    pro_manifest_path = output_dir / "manifest_pro.json"
    logger.info("Writing PRO manifest to %s", pro_manifest_path)
    write_json(pro_manifest, pro_manifest_path)

    logger.info(
        "Generation completed:\n  %s\n  %s\n  %s\n  %s",
        base_path,
        base_manifest_path,
        pro_path,
        pro_manifest_path,
    )


if __name__ == "__main__":
    main()