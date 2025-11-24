from typing import List, Dict, Any


def _create_block_rule(domain: str) -> Dict[str, Any]:
    """
    Crea una singola regola di blocco per Safari.
    """
    return {
        "trigger": {
            "url-filter": ".*",
            "if-domain": [domain],
        },
        "action": {
            "type": "block",
        },
    }


def build_base_list(domains: List[str], version: str = None) -> List[Dict[str, Any]]:
    """
    Genera la lista BASE.
    Restituisce una LISTA di regole (formato Safari).
    """
    rules = []
    for domain in domains:
        # Ignora domini non validi o localhost se presenti
        if domain in ["0.0.0.0", "127.0.0.1", "localhost"]:
            continue
        rules.append(_create_block_rule(domain))
    return rules


def build_pro_list(domains: List[str], version: str = None) -> List[Dict[str, Any]]:
    """
    Genera la lista PRO.
    Restituisce una LISTA di regole (formato Safari).
    """
    
    rules = []
    for domain in domains:
        if domain in ["0.0.0.0", "127.0.0.1", "localhost"]:
            continue
        rules.append(_create_block_rule(domain))
    return rules