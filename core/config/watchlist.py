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


# ═══════════════════════════════════════════════════════════
#  SENSITIVITY TAG MAPPINGS
# ═══════════════════════════════════════════════════════════

# China-exposed tickers (ADRs listed in the US but Chinese companies)
_CHINA_TICKERS = {"BABA", "PDD", "JD", "NIO", "BIDU"}

# Semiconductor-related tickers
_SEMI_TICKERS = {"NVDA", "AVGO", "INTC", "MU", "TSM", "ASML.AS", "TER", "MBLY"}

# Cybersecurity tickers
_CYBER_TICKERS = {"CRWD", "PANW", "FTNT"}

# AI / cloud platform tickers (broad AI beneficiaries)
_AI_TICKERS = {
    "NVDA", "AVGO", "INTC", "MU", "TSM", "ASML.AS", "TER",
    "GOOGL", "META", "MSFT", "AMZN", "AAPL", "CRM", "ADBE",
    "CRWD", "PANW", "FTNT", "BIDU",
}

# Defensive / consumer staple tickers
_DEFENSIVE_TICKERS = {"PEP", "PM", "HSY", "PG", "JNJ", "UNH", "WM"}

# Financials
_FINANCIAL_TICKERS = {"JPM", "V", "MA", "SPGI", "PYPL", "COIN", "BAM", "BN"}

# Liquid options — large-cap US names with heavy options volume
_LIQUID_OPTIONS_TICKERS = {
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
    "JPM", "V", "MA", "DIS", "PYPL", "CRM", "ADBE", "AVGO",
    "UBER", "COIN", "LLY", "UNH", "PG", "JNJ", "PEP",
    "SPY", "QQQ", "IWM", "GLD", "TLT", "SMH", "SOXX",
    "VTI", "SCHD", "JEPQ", "JEPI",
}

# Major US ETFs that have options
_US_ETFS_WITH_OPTIONS = {
    "VTI", "VWO", "VYM", "GLD", "BND", "BSV", "SMH", "SOXX",
    "VTV", "VO", "IWM", "IXJ", "IHI", "PPA", "TLT", "IEMG",
    "JEPQ", "JEPI", "QYLD", "SCHD", "PBDC", "SHLD",
}


def _infer_country(ticker: str, category: str) -> str | None:
    """Infer country from ticker format and category."""
    if category == "Crypto":
        return None
    if category == "EU Stocks":
        if ticker.endswith(".PA"):
            return "France"
        if ticker.endswith(".DE"):
            return "Germany"
        if ticker.endswith(".MI"):
            return "Italy"
        if ticker.endswith(".AS"):
            return "Netherlands"
        return "EU"
    # EU-listed ETFs
    if ticker.endswith((".L", ".DE", ".AS", ".MI", ".PA")):
        return "EU"
    # China ADRs
    if ticker in _CHINA_TICKERS:
        return "China"
    if ticker == "TSM":
        return "Taiwan"
    if ticker == "NVO":
        return "Denmark"
    if ticker == "ONON":
        return "Switzerland"
    if ticker == "MELI":
        return "Argentina"
    if ticker in ("CSU",):
        return "Canada"
    return "US"


def _infer_currency(ticker: str, category: str) -> str:
    """Infer trading currency from ticker."""
    if category == "Crypto":
        return "USD"
    if ticker.endswith(".L"):
        return "GBP"
    if ticker.endswith(".PA") or ticker.endswith(".AS"):
        return "EUR"
    if ticker.endswith(".DE"):
        return "EUR"
    if ticker.endswith(".MI"):
        return "EUR"
    return "USD"


def _infer_sector(ticker: str, name: str) -> str | None:
    """Best-effort sector inference from known tickers."""
    if ticker in _SEMI_TICKERS:
        return "Semiconductors"
    if ticker in _CYBER_TICKERS:
        return "Cybersecurity"
    if ticker in _FINANCIAL_TICKERS:
        return "Financials"
    if ticker in _DEFENSIVE_TICKERS:
        return "Consumer Defensive"
    if ticker in {"GOOGL", "META", "MSFT", "AMZN", "AAPL", "CRM", "ADBE"}:
        return "Technology"
    if ticker in {"TSLA", "STLAM.MI", "MBLY", "NIO"}:
        return "Automotive / EV"
    if ticker in {"LLY", "NVO", "UNH", "HIMS", "VEEV", "ZTS", "TMO"}:
        return "Healthcare / Pharma"
    if ticker in {"LMT", "SPCE", "ASTS"}:
        return "Aerospace & Defense"
    if ticker in {"ABNB", "BKNG", "UBER", "LYFT", "DIS", "DUOL"}:
        return "Consumer Discretionary"
    if ticker in {"MC.PA", "EL.PA", "OR.PA", "KER.PA", "ZAL.DE", "TGYM.MI", "ONON"}:
        return "Luxury / Consumer"
    if ticker == "EXO.MI":
        return "Conglomerate"
    return None


def _build_sensitivity_tags(ticker: str, name: str, category: str) -> list[str]:
    """Build sensitivity tags based on ticker properties."""
    tags: list[str] = []

    if category == "Crypto":
        return ["monetary_hedge", "high_beta", "liquidity_sensitive"]

    # --- US Stocks ---
    if category == "US Stocks":
        # China-exposed
        if ticker in _CHINA_TICKERS:
            tags.extend(["china_sensitive", "geopolitical_risk"])
        # Semis
        if ticker in _SEMI_TICKERS:
            tags.extend(["semis", "ai", "cyclical"])
        elif ticker in _AI_TICKERS:
            tags.extend(["quality", "long_duration_growth", "ai"])
        # Cyber
        if ticker in _CYBER_TICKERS and "ai" not in tags:
            tags.extend(["quality", "long_duration_growth", "ai"])
        # Defensives
        if ticker in _DEFENSIVE_TICKERS:
            tags.extend(["quality", "defensive", "low_beta"])
        # Financials
        if ticker in _FINANCIAL_TICKERS:
            tags.extend(["financials", "rate_sensitive"])
            if ticker == "COIN":
                tags.append("liquidity_sensitive")
        # Other growth names not yet tagged
        if not tags:
            tags.append("quality")

    # --- EU Stocks ---
    if category == "EU Stocks":
        tags.extend(["quality", "eu_exposure"])
        if ticker == "ASML.AS":
            tags.extend(["semis", "ai"])

    # --- ETFs ---
    if category == "ETFs":
        name_lower = name.lower()
        if "gold" in name_lower:
            tags.append("monetary_hedge")
        elif "bond" in name_lower or "treasury" in name_lower:
            tags.extend(["rate_sensitive", "defensive"])
        elif "semiconductor" in name_lower:
            tags.extend(["semis", "ai", "cyclical"])
        elif "emerging" in name_lower:
            tags.extend(["emerging_markets", "cyclical_reflation"])
        elif "dividend" in name_lower or "income" in name_lower or "premium" in name_lower:
            tags.extend(["income", "defensive"])
        elif "defense" in name_lower or "aerospace" in name_lower:
            tags.extend(["defense", "geopolitical_hedge"])
        elif "healthcare" in name_lower or "medical" in name_lower:
            tags.extend(["healthcare", "defensive"])
        elif "value" in name_lower:
            tags.extend(["value", "cyclical_reflation"])
        elif "momentum" in name_lower:
            tags.extend(["momentum", "factor"])
        elif "quality" in name_lower:
            tags.extend(["quality", "factor"])
        elif "real estate" in name_lower:
            tags.extend(["real_estate", "rate_sensitive"])
        elif "small" in name_lower or "russell" in name_lower or "mid-cap" in name_lower:
            tags.extend(["small_mid_cap", "liquidity_beta", "cyclical"])
        elif "bdc" in name_lower:
            tags.extend(["income", "credit_sensitive"])
        else:
            # Broad market ETFs
            tags.append("broad_market")

        # EU-listed ETFs
        if ticker.endswith((".L", ".DE", ".AS")):
            tags.append("eu_listed")

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_tags: list[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            unique_tags.append(t)
    return unique_tags


def get_watchlist_with_metadata() -> dict[str, dict]:
    """
    Return enriched watchlist entries with sensitivity tags, options flags,
    country, currency, and sector pre-populated from the existing WATCHLIST dict.

    Returns:
        dict mapping ticker -> metadata dict with keys:
            name, asset_class, category, sector, theme, country, currency,
            sensitivity_tags, options_available, options_liquid, priority, active
    """
    result: dict[str, dict] = {}

    category_to_asset_class = {
        "US Stocks": "stock",
        "EU Stocks": "stock",
        "ETFs": "etf",
        "Crypto": "crypto",
    }

    for category, tickers in WATCHLIST.items():
        asset_class = category_to_asset_class.get(category, "stock")

        for ticker, name in tickers.items():
            country = _infer_country(ticker, category)
            currency = _infer_currency(ticker, category)
            tags = _build_sensitivity_tags(ticker, name, category)
            sector = _infer_sector(ticker, name)

            # Options availability
            is_us_stock = category == "US Stocks" and not ticker.endswith(
                (".L", ".DE", ".AS", ".MI", ".PA")
            )
            options_available = is_us_stock or ticker in _US_ETFS_WITH_OPTIONS
            options_liquid = ticker in _LIQUID_OPTIONS_TICKERS

            result[ticker] = {
                "name": name,
                "asset_class": asset_class,
                "category": category,
                "sector": sector,
                "theme": None,
                "country": country,
                "currency": currency,
                "sensitivity_tags": tags,
                "options_available": options_available,
                "options_liquid": options_liquid,
                "priority": "tier2",
                "active": True,
            }

    return result


def get_default_watchlist_items() -> list[dict]:
    """
    Return a list of WatchlistItem-compatible dicts built from the existing
    WATCHLIST dict, with all enhanced fields populated.

    Each dict is ready to be unpacked into a WatchlistItem constructor:
        WatchlistItem(**item)
    """
    from datetime import datetime

    enriched = get_watchlist_with_metadata()
    items: list[dict] = []

    for ticker, meta in enriched.items():
        items.append({
            "ticker": ticker,
            "name": meta["name"],
            "asset_class": meta["asset_class"],
            "sector": meta["sector"],
            "theme": meta["theme"],
            "active": meta["active"],
            "notes": None,
            "priority": meta["priority"],
            "options_available": meta["options_available"],
            "options_liquid": meta["options_liquid"],
            "country": meta["country"],
            "currency": meta["currency"],
            "sensitivity_tags": meta["sensitivity_tags"],
            "created_at": datetime.utcnow(),
        })

    return items
