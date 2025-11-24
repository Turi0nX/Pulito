from datetime import datetime, timezone
from typing import Iterable, Dict, Any, List


def _normalize_domains(domains: Iterable[str]) -> List[str]:
    unique = []
    seen: set[str] = set()
    for d in domains:
        if not d:
            continue
        d = d.strip().lower()
        if not d or d in seen:
            continue
        seen.add(d)
        unique.append(d)
    return unique


def build_base_list(domains: Iterable[str], version: str = "1.0.0") -> Dict[str, Any]:
    normalized = sorted(_normalize_domains(domains))
    return {
        "version": version,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "rule_count": len(normalized),
        "rules": normalized,
    }


def build_pro_rules(domains: Iterable[str]) -> List[Dict[str, Any]]:
    """
    Versione PRO: Safari content blocker rules (trigger/action)
    basate solo sul dominio, senza '*' davanti.
    """
    normalized = _normalize_domains(domains)
    rules: List[Dict[str, Any]] = []

    for d in normalized:
        rules.append(
            {
                "trigger": {
                    "url-filter": ".*",
                    "if-domain": [d],  # <--- niente "*" qui
                },
                "action": {
                    "type": "block",
                },
            }
        )

    return rules


def build_pro_list(domains: Iterable[str], version: str = "1.0.0") -> Dict[str, Any]:
    rules = build_pro_rules(domains)
    return {
        "version": version,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "rule_count": len(rules),
        "rules": rules,
    }