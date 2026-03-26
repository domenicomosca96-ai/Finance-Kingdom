"""
Default watchlist — organized by category.

Ticker formats:
- US stocks: AAPL, NVDA, etc.
- EU stocks: MC.PA (Paris), ZAL.DE (Frankfurt), TGYM.MI (Milano), etc.
- ETFs: VTI, SPY, etc. (EU ETFs may need exchange suffix)
- Crypto: BTC-USD, ETH-USD, etc.
"""

WATCHLIST = {
    "US Stocks": {
        "GOOGL": "Alphabet Inc",
        "BABA": "Alibaba Group Holdings",
        "ABNB": "Airbnb",
        "BKNG": "Booking Holdings",
        "AMZN": "Amazon.com",
        "TSLA": "Tesla",
        "JPM": "JP Morgan Chase",
        "ADBE": "Adobe",
        "BN": "Brookfield Corporation",
        "LMT": "Lockheed Martin",
        "SPCE": "Virgin Galactic",
        "VEEV": "Veeva Systems",
        "FTNT": "Fortinet",
        "TMO": "Thermo Fisher Scientific",
        "PEP": "PepsiCo",
        "PM": "Philip Morris International",
        "CRM": "Salesforce",
        "AVGO": "Broadcom",
        "PANW": "Palo Alto Networks",
        "COIN": "Coinbase Global",
        "HSY": "The Hershey Company",
        "PYPL": "PayPal Holdings",
        "PDD": "PDD Holdings",
        "ZTS": "Zoetis",
        "CSU": "Constellation Software",
        "CRWD": "CrowdStrike Holdings",
        "NVDA": "NVIDIA Corporation",
        "META": "Meta Platforms",
        "MSFT": "Microsoft",
        "V": "Visa",
        "SPGI": "S&P Global",
        "JD": "JD.com",
        "NIO": "NIO Inc",
        "AAPL": "Apple",
        "NVO": "Novo Nordisk",
        "LLY": "Eli Lilly",
        "WM": "Waste Management",
        "MELI": "MercadoLibre",
        "DIS": "Walt Disney",
        "UBER": "Uber Technologies",
        "LYFT": "Lyft",
        "DUOL": "Duolingo",
        "MBLY": "Mobileye Global",
        "HIMS": "Hims & Hers Health",
        "UNH": "UnitedHealth Group",
        "PG": "Procter & Gamble",
        "JNJ": "Johnson & Johnson",
        "BIDU": "Baidu",
        "ONON": "On Holding AG",
        "BAM": "Brookfield Asset Mgmt",
        "TER": "Teradyne",
        "ASTS": "AST SpaceMobile",
        "INTC": "Intel",
        "MU": "Micron Technology",
        "MA": "Mastercard",
        "TSM": "Taiwan Semiconductor",
    },
    "EU Stocks": {
        "MC.PA": "LVMH",
        "EL.PA": "EssilorLuxottica",
        "ZAL.DE": "Zalando",
        "TGYM.MI": "Technogym",
        "STLAM.MI": "Stellantis",
        "EXO.MI": "Exor",
        "OR.PA": "L'Oreal",
        "KER.PA": "Kering",
        "ASML.AS": "ASML Holding",
    },
    "ETFs": {
        "VUSA.L": "Vanguard S&P 500 (London)",
        "VTI": "Vanguard Total Stock Market",
        "VWO": "Vanguard FTSE Emerging Markets",
        "VYM": "Vanguard High Dividend",
        "GLD": "SPDR Gold Trust",
        "BND": "Vanguard Total Bond Market",
        "BSV": "Vanguard Short-Term Bond",
        "SMH": "VanEck Semiconductor",
        "SOXX": "iShares Semiconductor",
        "VTV": "Vanguard Value ETF",
        "VO": "Vanguard Mid-Cap ETF",
        "IWM": "iShares Russell 2000",
        "IXJ": "iShares Global Healthcare",
        "IHI": "iShares U.S. Medical Devices",
        "PPA": "Invesco Aerospace & Defense",
        "TLT": "iShares 20+ Treasury Bond",
        "IEMG": "iShares Core MSCI Emerging Markets",
        "JEPQ": "JPMorgan Nasdaq Equity Premium",
        "JEPI": "JPMorgan Equity Premium Income",
        "QYLD": "Global X NASDAQ 100 Covered Call",
        "SCHD": "Schwab US Dividend Equity",
        "PBDC": "Putnam BDC Income",
        # EU-listed ETFs (London/Frankfurt/Amsterdam)
        "VWCE.DE": "Vanguard FTSE All-World (Frankfurt)",
        "SWDA.L": "iShares Core MSCI World (London)",
        "IWDA.AS": "iShares Core MSCI World (Amsterdam)",
        "CSNDX.L": "iShares NASDAQ 100 (London)",
        "XDEQ.DE": "Xtrackers MSCI World (Frankfurt)",
        "XDEM.DE": "Xtrackers MSCI World Momentum (Frankfurt)",
        "IEMA.L": "iShares MSCI Emerging Markets (London)",
        "SLMC.L": "iShares MSCI Europe (London)",
        "IWMO.L": "iShares Edge MSCI World Momentum (London)",
        "IWQU.L": "iShares Edge MSCI World Quality (London)",
        "GGRE.L": "WisdomTree Global Quality Real Estate (London)",
        "VGWE.L": "Vanguard Funds PLC (London)",
        "SHLD": "Global X Funds Defense Tech",
        "QDEV.L": "SPDR S&P Developed (London)",
    },
    "Crypto": {
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
        "SOL-USD": "Solana",
        "BNB-USD": "Binance Coin",
        "DOT-USD": "Polkadot",
        "ATOM-USD": "Cosmos",
        "LINK-USD": "Chainlink",
    },
}

# Flat list of all tickers for quick access
ALL_TICKERS = {}
for category, tickers in WATCHLIST.items():
    ALL_TICKERS.update(tickers)

# Category shortcuts for the UI
CATEGORIES = list(WATCHLIST.keys())


def get_tickers_by_category(category: str) -> dict[str, str]:
    """Get tickers for a specific category."""
    return WATCHLIST.get(category, {})


def get_all_ticker_symbols() -> list[str]:
    """Get flat list of all ticker symbols."""
    symbols = []
    for tickers in WATCHLIST.values():
        symbols.extend(tickers.keys())
    return symbols


def get_ticker_display_name(symbol: str) -> str:
    """Get display name for a ticker symbol."""
    return ALL_TICKERS.get(symbol, symbol)
