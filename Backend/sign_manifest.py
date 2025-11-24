from __future__ import annotations

import argparse
import sys
from pathlib import Path

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


def sign_manifest(privkey_file: Path, manifest_file: Path, signed_manifest_file: Path) -> None:
    if not privkey_file.is_file():
        raise FileNotFoundError(f"Private key not found: {privkey_file}")
    if not manifest_file.is_file():
        raise FileNotFoundError(f"Manifest file not found: {manifest_file}")

    with privkey_file.open("rb") as f:
        private_key = RSA.import_key(f.read())

    with manifest_file.open("rb") as f:
        data = f.read()

    h = SHA256.new(data)
    signature = pkcs1_15.new(private_key).sign(h)

    signed_manifest_file.parent.mkdir(parents=True, exist_ok=True)
    with signed_manifest_file.open("wb") as f:
        f.write(signature)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sign a manifest file.")
    parser.add_argument("privkey_file", type=Path, help="Path to private RSA key (PEM)")
    parser.add_argument("manifest_file", type=Path, help="Path to manifest file to sign")
    parser.add_argument("signed_manifest_file", type=Path, help="Output path for signature")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        sign_manifest(args.privkey_file, args.manifest_file, args.signed_manifest_file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error signing manifest: {exc}", file=sys.stderr)
        return 1

    print("Manifest signed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())