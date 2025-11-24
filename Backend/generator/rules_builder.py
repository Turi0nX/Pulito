from typing import List, Dict, Any

# --- LISTA DEI SELETTORI CSS PER I COOKIE BANNER PIÙ COMUNI ---
# Questi sono i "nomi" tecnici dei banner usati dal 90% dei siti web.
COOKIE_BANNER_SELECTORS = [
    "#onetrust-banner-sdk",       # OneTrust
    ".onetrust-pc-dark-filter",
    "#iubenda-cs-banner",         # Iubenda
    ".iubenda-cs-content",
    "#CybotCookiebotDialog",      # Cookiebot
    "#CybotCookiebotDialogBodyUnderlay",
    ".qc-cmp2-container",         # Quantcast
    "#didomi-host",               # Didomi
    ".fc-consent-root",           # Funding Choices (Google)
    "#cookie-banner",             # Generici
    ".cookie-banner",
    "#cookie-law-info-bar",
    ".cli-modal-backdrop",
    "#gdpr-cookie-message",
    ".cc-banner",                 # CookieConsent
    ".cc-window"
]


def _create_block_rule(domain: str) -> Dict[str, Any]:
    """
    Crea una regola di blocco di rete (Network Blocking).
    Impedisce al dominio di caricarsi.
    """
    return {
        "trigger": {
            "url-filter": ".*",
            "if-domain": [domain]
        },
        "action": {
            "type": "block"
        }
    }


def _create_css_hide_rule(selectors: List[str]) -> Dict[str, Any]:
    """
    Crea una regola per NASCONDERE elementi visivi (CSS Hiding).
    Ottimo per banner cookie, popup e anti-adblock.
    """
    # Uniamo tutti i selettori con una virgola (sintassi CSS standard)
    selector_string = ", ".join(selectors)

    return {
        "trigger": {
            "url-filter": ".*" # Applica su tutti i siti
        },
        "action": {
            "type": "css-display-none",
            "selector": selector_string
        }
    }


def build_base_list(domains: List[str], version: str = None) -> List[Dict[str, Any]]:
    """
    Genera la lista BASE.
    Solo blocco domini pubblicitari e traccianti.
    """
    rules = []
    for domain in domains:
        if domain in ["0.0.0.0", "127.0.0.1", "localhost"]:
            continue
        rules.append(_create_block_rule(domain))
    return rules


def build_pro_list(domains: List[str], version: str = None) -> List[Dict[str, Any]]:
    """
    Genera la lista PRO.
    Blocco domini + Rimozione visiva dei Banner Cookie.
    """
    rules = []

    # 1. Aggiungi le regole di blocco domini (come la Base)
    for domain in domains:
        if domain in ["0.0.0.0", "127.0.0.1", "localhost"]:
            continue
        rules.append(_create_block_rule(domain))

    # 2. AGGIUNTA PRO: Nascondi i banner dei cookie
    # Creiamo una regola unica che nasconde tutti i selettori definiti sopra
    if COOKIE_BANNER_SELECTORS:
        rules.append(_create_css_hide_rule(COOKIE_BANNER_SELECTORS))

    return rules