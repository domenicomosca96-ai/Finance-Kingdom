"""Watchlist Control Center — Manage and filter the full trading watchlist."""

import streamlit as st
import pandas as pd
from core.config.watchlist import WATCHLIST, CATEGORIES


# ═══════════════════════════════════════════════════════════
#  DEFAULT DATA BUILDER
# ═══════════════════════════════════════════════════════════

# Mapping from watchlist category to normalized asset class
_ASSET_CLASS_MAP = {
    "US Stocks": "Equity",
    "EU Stocks": "Equity",
    "ETFs": "ETF",
    "Crypto": "Crypto",
}

# Tickers known to have liquid options markets
_OPTIONS_LIQUID = {
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "JPM", "V", "MA",
    "AVGO", "CRM", "ADBE", "CRWD", "PANW", "COIN", "PYPL", "UBER", "DIS", "NVO",
    "LLY", "UNH", "PG", "JNJ", "INTC", "MU", "BABA", "PDD", "JD", "NIO", "BIDU",
    "SPY", "QQQ", "IWM", "SMH", "SOXX", "GLD", "TLT", "VTI",
    "ABNB", "BKNG", "LMT", "TMO", "PEP", "PM", "MELI", "HIMS", "TSM",
}

# Sensitivity tag heuristics based on sector
_SECTOR_MAP = {
    "GOOGL": "Technology", "BABA": "E-Commerce", "ABNB": "Travel",
    "BKNG": "Travel", "AMZN": "E-Commerce", "TSLA": "EV / Auto",
    "JPM": "Financials", "ADBE": "Software", "BN": "Financials",
    "LMT": "Defense", "SPCE": "Aerospace", "VEEV": "Healthcare IT",
    "FTNT": "Cybersecurity", "TMO": "Healthcare", "PEP": "Consumer Staples",
    "PM": "Consumer Staples", "CRM": "Software", "AVGO": "Semiconductors",
    "PANW": "Cybersecurity", "COIN": "Crypto / Fintech", "HSY": "Consumer Staples",
    "PYPL": "Fintech", "PDD": "E-Commerce", "ZTS": "Healthcare",
    "CSU": "Software", "CRWD": "Cybersecurity", "NVDA": "Semiconductors",
    "META": "Social Media", "MSFT": "Software", "V": "Fintech",
    "SPGI": "Financials", "JD": "E-Commerce", "NIO": "EV / Auto",
    "AAPL": "Technology", "NVO": "Healthcare", "LLY": "Healthcare",
    "WM": "Industrials", "MELI": "E-Commerce", "DIS": "Media",
    "UBER": "Ride-sharing", "LYFT": "Ride-sharing", "DUOL": "EdTech",
    "MBLY": "EV / Auto", "HIMS": "Healthcare", "UNH": "Healthcare",
    "PG": "Consumer Staples", "JNJ": "Healthcare", "BIDU": "Technology",
    "ONON": "Consumer Discretionary", "BAM": "Financials", "TER": "Semiconductors",
    "ASTS": "Aerospace", "INTC": "Semiconductors", "MU": "Semiconductors",
    "MA": "Fintech", "TSM": "Semiconductors",
    "MC.PA": "Luxury", "EL.PA": "Luxury", "ZAL.DE": "E-Commerce",
    "TGYM.MI": "Consumer Discretionary", "STLAM.MI": "Auto",
    "EXO.MI": "Financials", "OR.PA": "Consumer Staples",
    "KER.PA": "Luxury", "ASML.AS": "Semiconductors",
    "BTC-USD": "Crypto", "ETH-USD": "Crypto", "SOL-USD": "Crypto",
    "BNB-USD": "Crypto", "DOT-USD": "Crypto", "ATOM-USD": "Crypto",
    "LINK-USD": "Crypto",
}

_SENSITIVITY_TAGS = {
    "Semiconductors": "Rate-sensitive, China-exposure",
    "Cybersecurity": "Gov-spending, Geopolitical",
    "Healthcare": "Regulation, FDA-pipeline",
    "Financials": "Rate-sensitive, Credit-cycle",
    "E-Commerce": "Consumer-spending, Tariff-risk",
    "EV / Auto": "Rate-sensitive, Subsidy-dependent",
    "Luxury": "Consumer-spending, FX-sensitive",
    "Crypto": "Risk-on, Regulatory",
    "Crypto / Fintech": "Risk-on, Regulatory",
    "Defense": "Gov-spending, Geopolitical",
    "Consumer Staples": "Defensive, Inflation-hedge",
}


def _build_default_dataframe() -> pd.DataFrame:
    """Build a DataFrame from the static watchlist config."""
    rows = []
    for category, tickers in WATCHLIST.items():
        asset_class = _ASSET_CLASS_MAP.get(category, category)
        for symbol, name in tickers.items():
            sector = _SECTOR_MAP.get(symbol, "General")
            opts_available = asset_class in ("Equity", "ETF")
            opts_liquid = symbol in _OPTIONS_LIQUID
            sensitivity = _SENSITIVITY_TAGS.get(sector, "")
            rows.append({
                "Ticker": symbol,
                "Name": name,
                "Asset Class": asset_class,
                "Sector": sector,
                "Active": True,
                "Priority": "Tier 1",
                "Options Available": opts_available,
                "Options Liquid": opts_liquid,
                "Sensitivity Tags": sensitivity,
                "Notes": "",
            })
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════
#  PAGE RENDERER
# ═══════════════════════════════════════════════════════════

def render():
    st.title("Watchlist Control Center")
    st.caption("Manage, filter, and annotate your full trading universe")

    # ── Session state initialization ──
    if "watchlist_df" not in st.session_state:
        st.session_state["watchlist_df"] = _build_default_dataframe()

    df: pd.DataFrame = st.session_state["watchlist_df"]

    # ── Toolbar ──
    toolbar_cols = st.columns([1, 1, 1, 2])
    with toolbar_cols[0]:
        if st.button("Reset to Defaults", type="secondary", use_container_width=True):
            st.session_state["watchlist_df"] = _build_default_dataframe()
            st.rerun()
    with toolbar_cols[1]:
        if st.button("Add New Ticker", type="primary", use_container_width=True):
            st.session_state["show_add_form"] = True
    with toolbar_cols[2]:
        st.metric("Total Tickers", len(df))
    with toolbar_cols[3]:
        active_count = int(df["Active"].sum())
        inactive_count = len(df) - active_count
        st.metric("Active / Inactive", f"{active_count} / {inactive_count}")

    # ── Add ticker form ──
    if st.session_state.get("show_add_form", False):
        with st.expander("Add New Ticker", expanded=True):
            add_cols = st.columns(3)
            with add_cols[0]:
                new_ticker = st.text_input("Ticker Symbol", placeholder="e.g. AMD")
                new_name = st.text_input("Company Name", placeholder="e.g. Advanced Micro Devices")
            with add_cols[1]:
                new_asset_class = st.selectbox(
                    "Asset Class", ["Equity", "ETF", "Crypto"], key="add_asset_class"
                )
                new_sector = st.text_input("Sector", placeholder="e.g. Semiconductors")
            with add_cols[2]:
                new_priority = st.selectbox(
                    "Priority", ["Tier 1", "Tier 2", "Tier 3"], key="add_priority"
                )
                new_opts = st.checkbox("Options Available", value=True, key="add_opts")
                new_opts_liquid = st.checkbox("Options Liquid", value=False, key="add_opts_liq")

            if st.button("Confirm Add", type="primary"):
                ticker_clean = new_ticker.strip().upper()
                if not ticker_clean:
                    st.error("Ticker symbol is required.")
                elif ticker_clean in df["Ticker"].values:
                    st.error(f"{ticker_clean} already exists in the watchlist.")
                else:
                    new_row = pd.DataFrame([{
                        "Ticker": ticker_clean,
                        "Name": new_name.strip() or ticker_clean,
                        "Asset Class": new_asset_class,
                        "Sector": new_sector.strip() or "General",
                        "Active": True,
                        "Priority": new_priority,
                        "Options Available": new_opts,
                        "Options Liquid": new_opts_liquid,
                        "Sensitivity Tags": "",
                        "Notes": "",
                    }])
                    st.session_state["watchlist_df"] = pd.concat(
                        [df, new_row], ignore_index=True
                    )
                    st.session_state["show_add_form"] = False
                    st.rerun()

    st.divider()

    # ── Filters ──
    st.subheader("Filters")
    filter_cols = st.columns(4)

    with filter_cols[0]:
        asset_filter = st.multiselect(
            "Asset Class",
            options=sorted(df["Asset Class"].unique()),
            default=[],
            placeholder="All asset classes",
        )
    with filter_cols[1]:
        priority_filter = st.multiselect(
            "Priority",
            options=["Tier 1", "Tier 2", "Tier 3"],
            default=[],
            placeholder="All tiers",
        )
    with filter_cols[2]:
        active_filter = st.selectbox(
            "Status", ["All", "Active Only", "Inactive Only"], index=0
        )
    with filter_cols[3]:
        opts_filter = st.selectbox(
            "Options", ["All", "Options Available", "Options Liquid", "No Options"], index=0
        )

    search_query = st.text_input(
        "Search by ticker or name",
        placeholder="Type to filter...",
        key="watchlist_search",
    )

    # ── Apply filters ──
    filtered = df.copy()

    if asset_filter:
        filtered = filtered[filtered["Asset Class"].isin(asset_filter)]
    if priority_filter:
        filtered = filtered[filtered["Priority"].isin(priority_filter)]
    if active_filter == "Active Only":
        filtered = filtered[filtered["Active"]]
    elif active_filter == "Inactive Only":
        filtered = filtered[~filtered["Active"]]
    if opts_filter == "Options Available":
        filtered = filtered[filtered["Options Available"]]
    elif opts_filter == "Options Liquid":
        filtered = filtered[filtered["Options Liquid"]]
    elif opts_filter == "No Options":
        filtered = filtered[~filtered["Options Available"]]
    if search_query:
        query_upper = search_query.upper()
        filtered = filtered[
            filtered["Ticker"].str.upper().str.contains(query_upper, na=False)
            | filtered["Name"].str.upper().str.contains(query_upper, na=False)
        ]

    st.caption(f"Showing {len(filtered)} of {len(df)} tickers")

    # ── Editable data table ──
    edited = st.data_editor(
        filtered,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", width="small", disabled=True),
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Asset Class": st.column_config.SelectboxColumn(
                "Asset Class", options=["Equity", "ETF", "Crypto"], width="small",
            ),
            "Sector": st.column_config.TextColumn("Sector", width="medium"),
            "Active": st.column_config.CheckboxColumn("Active", width="small"),
            "Priority": st.column_config.SelectboxColumn(
                "Priority", options=["Tier 1", "Tier 2", "Tier 3"], width="small",
            ),
            "Options Available": st.column_config.CheckboxColumn("Options Available", width="small"),
            "Options Liquid": st.column_config.CheckboxColumn("Options Liquid", width="small"),
            "Sensitivity Tags": st.column_config.TextColumn("Sensitivity Tags", width="medium"),
            "Notes": st.column_config.TextColumn("Notes", width="large"),
        },
        key="watchlist_editor",
    )

    # Persist edits back to session state by updating the original df at matching indices
    if edited is not None:
        st.session_state["watchlist_df"].update(edited)

    # ── Summary stats ──
    st.divider()
    st.subheader("Watchlist Summary")
    summary_cols = st.columns(4)
    with summary_cols[0]:
        for ac in sorted(df["Asset Class"].unique()):
            count = int((df["Asset Class"] == ac).sum())
            st.metric(ac, count)
    with summary_cols[1]:
        for tier in ["Tier 1", "Tier 2", "Tier 3"]:
            count = int((df["Priority"] == tier).sum())
            st.metric(tier, count)
    with summary_cols[2]:
        st.metric("Options Available", int(df["Options Available"].sum()))
        st.metric("Options Liquid", int(df["Options Liquid"].sum()))
    with summary_cols[3]:
        st.metric("Active", int(df["Active"].sum()))
        st.metric("Inactive", int((~df["Active"]).sum()))
