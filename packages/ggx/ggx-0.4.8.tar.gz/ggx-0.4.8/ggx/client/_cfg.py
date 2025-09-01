
## configurari de client ##
VERSION = "V 1.01"
GAME_VERSION_URL = "https://empire-html5.goodgamestudios.com/default/items/ItemsVersion.properties"
CLIENT_ORIGIN = "https://empire-html5.goodgamestudios.com"
SERVERS_DB = "https://empire-html5.goodgamestudios.com/config/network/1.xml"
LANG_DB = "https://langserv.public.ggs-ep.com/em/en"












### client headers ###
AD_HEADERS = {
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "DNT": "1",
        "Sec-GPC": "1"
}







DEFAULT_UA_LIST = [
    # — Browsere moderne (versiuni actualizate pentru HTML5/WebGL) —
    # Google Chrome pe Windows 11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36",

    # Google Chrome pe macOS Sonoma (14_0)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36",

    # Mozilla Firefox pe Windows 11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) "
    "Gecko/20100101 Firefox/120.0",

    # Mozilla Firefox pe macOS Sonoma (14_0)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0; rv:120.0) "
    "Gecko/20100101 Firefox/120.0",

    # Microsoft Edge pe Windows 11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",

    # Apple Safari pe macOS Sonoma (14_0)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.4 Safari/605.1.15",

    # Opera (Blink) pe Windows 11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36 OPR/103.0.4924.32",


    # — Intrări din DEFAULT_UA_LIST (fișier) —
    # Chrome pe Windows 10
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.5790.98 Safari/537.36",

    # Chrome pe macOS (10_15_7)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36",

    # Chrome pe Linux
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36",

    # Firefox pe Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:114.0) "
    "Gecko/20100101 Firefox/114.0",

    # Firefox pe macOS (10.15)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:112.0) "
    "Gecko/20100101 Firefox/112.0",

    # Safari pe macOS (10_15_7)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/14.0 Safari/605.1.15",

    # Edge pe Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36 Edg/114.0.0.0",

    # Opera pe Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0",
]
