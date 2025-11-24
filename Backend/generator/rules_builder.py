from typing import List, Dict, Any

# --- 1. COOKIE BANNERS  ---
COOKIE_BANNER_SELECTORS = [
    "#onetrust-banner-sdk",       # OneTrust
    ".onetrust-pc-dark-filter",
    "#iubenda-cs-banner",         # Iubenda
    ".iubenda-cs-content",
    "#CybotCookiebotDialog",      # Cookiebot
    "#CybotCookiebotDialogBodyUnderlay",
    ".qc-cmp2-container",         # Quantcast
    "#didomi-host",               # Didomi
    "#cookie-banner",             # Generici
    ".cookie-banner",
    "#cookie-law-info-bar",
    ".cli-modal-backdrop",
    "#gdpr-cookie-message",
    ".cc-banner",                 # CookieConsent
    ".cc-window",
    ".fc-consent-root"            # Google Funding Choices 
]

# --- 2. ANTI-ADBLOCK WALLS  ---

ANTI_ADBLOCK_SELECTORS = [
    ".fc-ab-root",                # Google Funding Choices (Anti-Adblock)
    ".fc-ab-overlay",
    "#adblock-message",           # Generici
    ".adblock-message",
    "#adblock-overlay",
    ".adblock-overlay",
    "#block-adblock",
    ".block-adblock",
    ".detect-adblock",
    "#detect-adblock",
    ".adb-overlay",               # Admiral 
    "#adb-overlay",
    ".sp_message_container",      # Sourcepoint
    "div[class*='adblock']",      # Qualsiasi div che contenga "adblock" nel nome classe
    "div[id*='adblock']"          # Qualsiasi div che contenga "adblock" nell'ID
]


def _create_block_rule(domain: str) -> Dict[str, Any]:
    """
    Regola di blocco di rete (Network Blocking).
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
    Regola per NASCONDERE elementi visivi (CSS Hiding).
    """
    selector_string = ", ".join(selectors)
    
    return {
        "trigger": {
            "url-filter": ".*"
        },
        "action": {
            "type": "css-display-none",
            "selector": selector_string
        }
    }


def build_base_list(domains: List[str], version: str = None) -> List[Dict[str, Any]]:
    """
    LISTA BASE: Solo blocco pubblicità (leggera).
    """
    rules = []
    for domain in domains:
        if domain in ["0.0.0.0", "127.0.0.1", "localhost"]:
            continue
        rules.append(_create_block_rule(domain))
    return rules


def build_pro_list(domains: List[str], version: str = None) -> List[Dict[str, Any]]:
    """
    LISTA PRO: Blocco Ads + Cookie Banners + Anti-Adblock Walls.
    """
    rules = []
    
    # 1. Blocco Domini
    for domain in domains:
        if domain in ["0.0.0.0", "127.0.0.1", "localhost"]:
            continue
        rules.append(_create_block_rule(domain))
        
    # 2. Nascondi Cookie Banners
    if COOKIE_BANNER_SELECTORS:
        rules.append(_create_css_hide_rule(COOKIE_BANNER_SELECTORS))

    # 3. Nascondi Anti-Adblock Walls (NUOVO)
    if ANTI_ADBLOCK_SELECTORS:
        rules.append(_create_css_hide_rule(ANTI_ADBLOCK_SELECTORS))
        
    return rules