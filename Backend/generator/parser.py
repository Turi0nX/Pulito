import logging
import re
from typing import Iterable, List, Optional

logger = logging.getLogger(__name__)

# EasyList / uBlock: "||example.com^"
DOMAIN_RULE_RE = re.compile(r"^\|\|([a-z0-9.-]+)\^", re.IGNORECASE)

# Hosts file style: "0.0.0.0 example.com" o "127.0.0.1 example.com"
HOSTS_RE = re.compile(r"^(?:0\.0\.0\.0|127\.0\.0\.1)\s+([a-z0-9.-]+)$", re.IGNORECASE)


def parse_rule_line(line: str) -> Optional[str]:
    """
    Parse a single rule line into a simplified domain rule.

    - Strips whitespace
    - Ignores empty lines and comments
    - Supports:
      * EasyList/uBlock style: '||example.com^'
      * hosts style: '0.0.0.0 example.com'
    """
    if line is None:
        return None

    line = line.strip()
    if not line:
        return None

    if line.startswith("!") or line.startswith("#") or line.startswith("[Adblock"):
        return None

    # EasyList/uBlock syntax
    m = DOMAIN_RULE_RE.match(line)
    if m:
        domain = m.group(1).lower()
        return domain

    # Hosts syntax
    m = HOSTS_RE.match(line)
    if m:
        domain = m.group(1).lower()
        return domain

    
    return None


def parse_list(lines: Iterable[str]) -> List[str]:
    rules: List[str] = []
    for l in lines:
        parsed = parse_rule_line(l)
        if parsed:
            rules.append(parsed)
    return rules