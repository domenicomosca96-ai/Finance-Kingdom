import React, { useMemo, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { X, Shield, TrendingUp, Loader2, Volume2, Info, History, ShieldAlert, Globe, DollarSign } from "lucide-react";
import {
  PieChart, Pie, Cell, Tooltip, Legend,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis
} from "recharts";

// ---------------------------------------------
//  DYNAMIC ASSET ALLOCATION — v12
//  - Watchlist unificata con bucket e riskClass
//  - Matrice PHASE_BUCKET_SCORES unica per semaforo e picks
//  - Overlay DXY e Inflazione coerenti
//  - Speculation trattata come fase tardiva / prudente
//  - Fondi rimossi dai suggeriti
//  - Tab Crypto aggiunta
// ---------------------------------------------

const PROFILES = ["Default","Conservative","Aggressive"] as const;
const PHASES = ["Rebound", "Calm", "Speculation", "Turbulence"] as const;
const REGIONS = ["USA", "Eurozona", "Cina"] as const;
const DXY_TRENDS = ["Bearish", "Neutral", "Bullish"] as const;
const HISTORICAL_REGIMES = {
  "stagflation_70s": "Stagflazione (Anni '70)",
  "moderation_90s": "Grande Moderazione (1985-2007)",
  "disinflation_2010s": "Disinflazione Post-GFC (2010-2019)",
  "gfc_2008": "Crisi Finanziaria Globale (2008 - Shock)",
  "inflation_2022": "Shock Inflazionistico (2022 - Shock)"
};

type Profile = typeof PROFILES[number];
type Phase = typeof PHASES[number];
type Region = typeof REGIONS[number];
type RegionPhases = Record<Region, Phase>;
type DxyTrend = typeof DXY_TRENDS[number];
type AssetType = "stock" | "etf" | "crypto";
type Bucket =
  | "quality" | "technology" | "financials" | "travel" | "luxury"
  | "healthcare" | "defensive" | "chinaEM" | "cyclical" | "speculative"
  | "broadETF" | "dividendETF" | "defensiveETF" | "gold" | "commodities"
  | "bondShort" | "bondLong" | "cashETF" | "cryptoCore" | "cryptoAlt";
type RiskClass = "core" | "growth" | "speculative";
type BucketScore = -2 | -1 | 0 | 1 | 2;

type WatchItem = {
  ticker: string;
  name: string;
  type: AssetType;
  bucket: Bucket;
  riskClass: RiskClass;
};

const COLORS = { azioni: "#2563eb", gold: "#c2a200", materiePrime: "#ef6c00", obbligazioni: "#0ea5e9", cash: "#6b7280", bitcoin: "#f7931a" };

const clamp = (x: number, min: number, max: number) => Math.max(min, Math.min(max, x));
const pct = (x: number) => `${x.toFixed(1)}%`;
const level = (inf: number) => inf < 0 ? "deflation" : inf < 1.5 ? "low" : inf <= 3.5 ? "sweet" : inf <= 5 ? "high" : "veryHigh";

// --- WATCHLIST UNIFICATA ---
const WATCHLIST: WatchItem[] = [
  // STOCKS
  { ticker:"GOOGL", name:"Alphabet", type:"stock", bucket:"quality", riskClass:"core" },
  { ticker:"BABA", name:"Alibaba", type:"stock", bucket:"chinaEM", riskClass:"growth" },
  { ticker:"ABNB", name:"Airbnb", type:"stock", bucket:"travel", riskClass:"growth" },
  { ticker:"BKNG", name:"Booking", type:"stock", bucket:"travel", riskClass:"core" },
  { ticker:"AMZN", name:"Amazon", type:"stock", bucket:"quality", riskClass:"core" },
  { ticker:"MC", name:"LVMH", type:"stock", bucket:"luxury", riskClass:"core" },
  { ticker:"TSLA", name:"Tesla", type:"stock", bucket:"technology", riskClass:"growth" },
  { ticker:"JPM", name:"JPMorgan", type:"stock", bucket:"financials", riskClass:"core" },
  { ticker:"ADBE", name:"Adobe", type:"stock", bucket:"quality", riskClass:"core" },
  { ticker:"BN", name:"Brookfield Corp", type:"stock", bucket:"financials", riskClass:"growth" },
  { ticker:"LMT", name:"Lockheed Martin", type:"stock", bucket:"defensive", riskClass:"core" },
  { ticker:"EL", name:"EssilorLuxottica", type:"stock", bucket:"luxury", riskClass:"core" },
  { ticker:"ZAL", name:"Zalando", type:"stock", bucket:"cyclical", riskClass:"growth" },
  { ticker:"SPCE", name:"Virgin Galactic", type:"stock", bucket:"speculative", riskClass:"speculative" },
  { ticker:"VEEV", name:"Veeva Systems", type:"stock", bucket:"healthcare", riskClass:"core" },
  { ticker:"FTNT", name:"Fortinet", type:"stock", bucket:"technology", riskClass:"growth" },
  { ticker:"TMO", name:"Thermo Fisher", type:"stock", bucket:"healthcare", riskClass:"core" },
  { ticker:"PEP", name:"PepsiCo", type:"stock", bucket:"defensive", riskClass:"core" },
  { ticker:"TSM", name:"TSMC", type:"stock", bucket:"technology", riskClass:"core" },
  { ticker:"PM", name:"Philip Morris", type:"stock", bucket:"defensive", riskClass:"core" },
  { ticker:"TGYM", name:"Technogym", type:"stock", bucket:"cyclical", riskClass:"growth" },
  { ticker:"STLAM", name:"Stellantis", type:"stock", bucket:"cyclical", riskClass:"growth" },
  { ticker:"CRM", name:"Salesforce", type:"stock", bucket:"quality", riskClass:"core" },
  { ticker:"EXO", name:"Exor", type:"stock", bucket:"cyclical", riskClass:"core" },
  { ticker:"AVGO", name:"Broadcom", type:"stock", bucket:"technology", riskClass:"core" },
  { ticker:"PANW", name:"Palo Alto Networks", type:"stock", bucket:"technology", riskClass:"growth" },
  { ticker:"COIN", name:"Coinbase", type:"stock", bucket:"speculative", riskClass:"speculative" },
  { ticker:"HSY", name:"Hershey", type:"stock", bucket:"defensive", riskClass:"core" },
  { ticker:"PYPL", name:"PayPal", type:"stock", bucket:"financials", riskClass:"growth" },
  { ticker:"PDD", name:"PDD Holdings", type:"stock", bucket:"chinaEM", riskClass:"growth" },
  { ticker:"ZTS", name:"Zoetis", type:"stock", bucket:"healthcare", riskClass:"core" },
  { ticker:"OR", name:"L'Oreal", type:"stock", bucket:"luxury", riskClass:"core" },
  { ticker:"CSU", name:"Constellation Software", type:"stock", bucket:"quality", riskClass:"core" },
  { ticker:"CRWD", name:"CrowdStrike", type:"stock", bucket:"technology", riskClass:"growth" },
  { ticker:"NVDA", name:"NVIDIA", type:"stock", bucket:"technology", riskClass:"core" },
  { ticker:"META", name:"Meta", type:"stock", bucket:"quality", riskClass:"core" },
  { ticker:"MSFT", name:"Microsoft", type:"stock", bucket:"quality", riskClass:"core" },
  { ticker:"ASML", name:"ASML", type:"stock", bucket:"technology", riskClass:"core" },
  { ticker:"KER", name:"Kering", type:"stock", bucket:"luxury", riskClass:"core" },
  { ticker:"V", name:"Visa", type:"stock", bucket:"quality", riskClass:"core" },
  { ticker:"SPGI", name:"S&P Global", type:"stock", bucket:"quality", riskClass:"core" },
  { ticker:"JD", name:"JD.com", type:"stock", bucket:"chinaEM", riskClass:"growth" },
  { ticker:"NIO", name:"NIO", type:"stock", bucket:"chinaEM", riskClass:"speculative" },
  { ticker:"AAPL", name:"Apple", type:"stock", bucket:"quality", riskClass:"core" },
  { ticker:"NVO", name:"Novo Nordisk", type:"stock", bucket:"healthcare", riskClass:"core" },
  { ticker:"LLY", name:"Eli Lilly", type:"stock", bucket:"healthcare", riskClass:"core" },
  { ticker:"WM", name:"Waste Management", type:"stock", bucket:"defensive", riskClass:"core" },
  { ticker:"MELI", name:"MercadoLibre", type:"stock", bucket:"chinaEM", riskClass:"growth" },
  { ticker:"DIS", name:"Disney", type:"stock", bucket:"travel", riskClass:"growth" },
  { ticker:"UBER", name:"Uber", type:"stock", bucket:"travel", riskClass:"growth" },
  { ticker:"LYFT", name:"Lyft", type:"stock", bucket:"travel", riskClass:"speculative" },
  { ticker:"DUOL", name:"Duolingo", type:"stock", bucket:"speculative", riskClass:"speculative" },
  { ticker:"MBLY", name:"Mobileye", type:"stock", bucket:"technology", riskClass:"speculative" },
  { ticker:"HIMS", name:"Hims & Hers", type:"stock", bucket:"speculative", riskClass:"speculative" },
  { ticker:"UNH", name:"UnitedHealth", type:"stock", bucket:"healthcare", riskClass:"core" },
  { ticker:"PG", name:"Procter & Gamble", type:"stock", bucket:"defensive", riskClass:"core" },
  { ticker:"JNJ", name:"Johnson & Johnson", type:"stock", bucket:"healthcare", riskClass:"core" },
  { ticker:"BIDU", name:"Baidu", type:"stock", bucket:"chinaEM", riskClass:"growth" },
  { ticker:"ONON", name:"On Holding", type:"stock", bucket:"cyclical", riskClass:"growth" },
  { ticker:"BAM", name:"Brookfield Asset Mgmt", type:"stock", bucket:"financials", riskClass:"growth" },
  { ticker:"TER", name:"Teradyne", type:"stock", bucket:"technology", riskClass:"growth" },
  { ticker:"ASTS", name:"AST SpaceMobile", type:"stock", bucket:"speculative", riskClass:"speculative" },
  { ticker:"INTC", name:"Intel", type:"stock", bucket:"technology", riskClass:"growth" },
  { ticker:"MU", name:"Micron", type:"stock", bucket:"technology", riskClass:"growth" },
  { ticker:"MA", name:"Mastercard", type:"stock", bucket:"quality", riskClass:"core" },
  // ETFs
  { ticker:"VGWE", name:"Vanguard Funds PLC", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"VUSA", name:"Vanguard S&P 500", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"SLMC", name:"iShares MSCI Europe", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"XDEM", name:"Xtrackers MSCI World", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"IEMA", name:"iShares MSCI EM", type:"etf", bucket:"broadETF", riskClass:"growth" },
  { ticker:"VTI", name:"Vanguard Total Stock Mkt", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"VWO", name:"Vanguard FTSE Emerging", type:"etf", bucket:"broadETF", riskClass:"growth" },
  { ticker:"IEMG", name:"iShares Core MSCI Emerging", type:"etf", bucket:"broadETF", riskClass:"growth" },
  { ticker:"VYM", name:"Vanguard High Dividend", type:"etf", bucket:"dividendETF", riskClass:"core" },
  { ticker:"GLD", name:"SPDR Gold Trust", type:"etf", bucket:"gold", riskClass:"core" },
  { ticker:"BND", name:"Vanguard Total Bond Mkt", type:"etf", bucket:"bondLong", riskClass:"core" },
  { ticker:"BSV", name:"Vanguard Short-Term Bond", type:"etf", bucket:"bondShort", riskClass:"core" },
  { ticker:"SMH", name:"VanEck Semiconductor", type:"etf", bucket:"technology", riskClass:"growth" },
  { ticker:"SOXX", name:"iShares Semiconductor", type:"etf", bucket:"technology", riskClass:"growth" },
  { ticker:"VTV", name:"Vanguard Value ETF", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"VO", name:"Vanguard Mid-Cap ETF", type:"etf", bucket:"broadETF", riskClass:"growth" },
  { ticker:"IWM", name:"iShares Russell 2000", type:"etf", bucket:"broadETF", riskClass:"growth" },
  { ticker:"IXJ", name:"iShares Global Healthcare", type:"etf", bucket:"defensiveETF", riskClass:"core" },
  { ticker:"IHI", name:"iShares U.S. Medical Devices", type:"etf", bucket:"defensiveETF", riskClass:"core" },
  { ticker:"PPA", name:"Invesco Aerospace", type:"etf", bucket:"defensiveETF", riskClass:"core" },
  { ticker:"VWCE", name:"Vanguard FTSE All-World", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"CSNDX", name:"iShares NASDAQ 100", type:"etf", bucket:"technology", riskClass:"growth" },
  { ticker:"TLT", name:"iShares Treasury Bond", type:"etf", bucket:"bondLong", riskClass:"core" },
  { ticker:"GGRE", name:"WisdomTree Global Quality", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"SWDA", name:"iShares Core MSCI World", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"XDEQ", name:"Xtrackers MSCI World", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"IWDA", name:"iShares Core MSCI World", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"JEPQ", name:"JPMorgan Nasdaq Equity", type:"etf", bucket:"dividendETF", riskClass:"core" },
  { ticker:"JEPI", name:"JPMorgan Equity Premium", type:"etf", bucket:"dividendETF", riskClass:"core" },
  { ticker:"QYLD", name:"Global X Nasdaq 100", type:"etf", bucket:"dividendETF", riskClass:"core" },
  { ticker:"IWMO", name:"iShares Edge MSCI World", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"IWQU", name:"iShares Edge MSCI World Quality", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"QDEV", name:"SPDR S&P Developed", type:"etf", bucket:"broadETF", riskClass:"core" },
  { ticker:"SCHD", name:"Schwab US Dividend", type:"etf", bucket:"dividendETF", riskClass:"core" },
  { ticker:"PBDC", name:"Putnam BDC Income", type:"etf", bucket:"dividendETF", riskClass:"growth" },
  { ticker:"SHLD", name:"Global X Funds", type:"etf", bucket:"defensiveETF", riskClass:"core" },
  // CRYPTO
  { ticker:"BTCUSD", name:"Bitcoin", type:"crypto", bucket:"cryptoCore", riskClass:"core" },
  { ticker:"BTC.D", name:"BTC Dominance", type:"crypto", bucket:"cryptoCore", riskClass:"core" },
  { ticker:"TOTAL", name:"Crypto Total Market", type:"crypto", bucket:"cryptoCore", riskClass:"growth" },
  { ticker:"TOTAL2", name:"Crypto Total Market Alt", type:"crypto", bucket:"cryptoAlt", riskClass:"speculative" },
  { ticker:"ETHUSD", name:"Ethereum", type:"crypto", bucket:"cryptoCore", riskClass:"growth" },
  { ticker:"SOLUSD", name:"Solana", type:"crypto", bucket:"cryptoAlt", riskClass:"speculative" },
  { ticker:"BNBUSDT", name:"BNB", type:"crypto", bucket:"cryptoAlt", riskClass:"growth" },
  { ticker:"DOTUSDT", name:"Polkadot", type:"crypto", bucket:"cryptoAlt", riskClass:"speculative" },
  { ticker:"ATOMUSDT", name:"Cosmos", type:"crypto", bucket:"cryptoAlt", riskClass:"speculative" },
  { ticker:"LINKUSDT", name:"Chainlink", type:"crypto", bucket:"cryptoAlt", riskClass:"growth" },
];

// --- PRESET ALLOCAZIONE (Speculation corretta: più prudente) ---
const PRESETS: Record<Profile, Record<Phase, Record<string, number>>> = {
  Default: {
    Rebound:     { azioni:60, gold:8,  materiePrime:12, obbligazioni:10, cash:5,  bitcoin:5 },
    Calm:        { azioni:55, gold:10, materiePrime:15, obbligazioni:10, cash:5,  bitcoin:5 },
    Speculation: { azioni:32, gold:15, materiePrime:14, obbligazioni:15, cash:22, bitcoin:2 },
    Turbulence:  { azioni:18, gold:18, materiePrime:14, obbligazioni:13, cash:37, bitcoin:0 },
  },
  Conservative: {
    Rebound:     { azioni:45, gold:15, materiePrime:15, obbligazioni:15, cash:10, bitcoin:0 },
    Calm:        { azioni:42, gold:15, materiePrime:15, obbligazioni:18, cash:10, bitcoin:0 },
    Speculation: { azioni:22, gold:18, materiePrime:12, obbligazioni:20, cash:28, bitcoin:0 },
    Turbulence:  { azioni:12, gold:20, materiePrime:10, obbligazioni:23, cash:35, bitcoin:0 },
  },
  Aggressive: {
    Rebound:     { azioni:50, gold:7,  materiePrime:15, obbligazioni:8,  cash:5,  bitcoin:15 },
    Calm:        { azioni:53, gold:5,  materiePrime:17, obbligazioni:8,  cash:5,  bitcoin:12 },
    Speculation: { azioni:38, gold:10, materiePrime:16, obbligazioni:12, cash:18, bitcoin:6 },
    Turbulence:  { azioni:18, gold:16, materiePrime:12, obbligazioni:14, cash:40, bitcoin:0 },
  }
};

// --- MATRICE UNICA DI REGIME (bucket scores) ---
const PHASE_BUCKET_SCORES: Record<Phase, Record<Bucket, BucketScore>> = {
  Rebound: {
    quality: 1, technology: 1, financials: 1, travel: 2, luxury: 1,
    healthcare: 0, defensive: -1, chinaEM: 1, cyclical: 2, speculative: 0,
    broadETF: 1, dividendETF: 0, defensiveETF: 0, gold: 0, commodities: 1,
    bondShort: 0, bondLong: 1, cashETF: -1, cryptoCore: 1, cryptoAlt: 0,
  },
  Calm: {
    quality: 2, technology: 1, financials: 1, travel: 1, luxury: 0,
    healthcare: 1, defensive: 0, chinaEM: 0, cyclical: 0, speculative: -1,
    broadETF: 1, dividendETF: 0, defensiveETF: 1, gold: 0, commodities: 0,
    bondShort: 0, bondLong: 0, cashETF: -1, cryptoCore: 1, cryptoAlt: 0,
  },
  Speculation: {
    quality: 0, technology: 0, financials: 0, travel: -1, luxury: -1,
    healthcare: 1, defensive: 2, chinaEM: -1, cyclical: -1, speculative: -2,
    broadETF: 0, dividendETF: 1, defensiveETF: 1, gold: 1, commodities: 1,
    bondShort: 1, bondLong: -1, cashETF: 2, cryptoCore: -1, cryptoAlt: -2,
  },
  Turbulence: {
    quality: 0, technology: -2, financials: -1, travel: -2, luxury: -2,
    healthcare: 2, defensive: 2, chinaEM: -2, cyclical: -2, speculative: -2,
    broadETF: -1, dividendETF: 1, defensiveETF: 2, gold: 2, commodities: 1,
    bondShort: 2, bondLong: 0, cashETF: 2, cryptoCore: -2, cryptoAlt: -2,
  }
};

// --- DXY OVERLAY ---
const DXY_BUCKET_OVERLAY: Record<DxyTrend, Partial<Record<Bucket, number>>> = {
  Bearish: {
    chinaEM: 1, travel: 1, cyclical: 1, luxury: 1,
    cryptoCore: 1, cryptoAlt: 1, cashETF: -1, bondShort: -1,
  },
  Neutral: {},
  Bullish: {
    quality: 1, financials: 1, healthcare: 1, defensive: 1,
    chinaEM: -2, travel: -1, cyclical: -1, luxury: -1,
    technology: -1, speculative: -2, commodities: -2,
    gold: 0, cryptoCore: -2, cryptoAlt: -2,
    cashETF: 2, bondShort: 1, bondLong: 0,
  },
};

// --- INFLATION OVERLAY PER BUCKET ---
function inflationBucketOverlay(inf: number): Partial<Record<Bucket, number>> {
  const reg = level(inf);
  if (reg === "deflation") {
    return { bondLong: 2, bondShort: 1, defensive: 1, healthcare: 1, commodities: -2, cryptoCore: -1, cryptoAlt: -2, cyclical: -1 };
  }
  if (reg === "low") {
    return { quality: 1, bondLong: 1, commodities: -1, gold: -1 };
  }
  if (reg === "sweet") {
    return { quality: 1, technology: 1, financials: 1, defensive: 0, bondLong: 0 };
  }
  if (reg === "high") {
    return { gold: 1, commodities: 2, defensive: 1, healthcare: 1, technology: -1, bondLong: -2, chinaEM: -1 };
  }
  // veryHigh
  return { gold: 2, commodities: 2, defensive: 1, healthcare: 1, technology: -2, bondLong: -2, cryptoAlt: -2 };
}

// --- RISK CLASS OVERLAY PER FASE ---
const RISKCLASS_OVERLAY: Record<Phase, Record<RiskClass, number>> = {
  Rebound:     { core: 0, growth: 0, speculative: -1 },
  Calm:        { core: 1, growth: 0, speculative: -1 },
  Speculation: { core: 1, growth: 0, speculative: -2 },
  Turbulence:  { core: 1, growth: -1, speculative: -3 },
};

// --- SCORING FUNCTIONS ---
const clampScore = (x: number): BucketScore =>
  Math.max(-2, Math.min(2, x)) as BucketScore;

function scoreToTraffic(score: number): "red" | "orange" | "green" {
  if (score >= 1) return "green";
  if (score <= -1) return "red";
  return "orange";
}

function getBucketScore(bucket: Bucket, phase: Phase, inf: number, dxy: DxyTrend): BucketScore {
  const base = PHASE_BUCKET_SCORES[phase][bucket] ?? 0;
  const infAdj = inflationBucketOverlay(inf)[bucket] ?? 0;
  const dxyAdj = DXY_BUCKET_OVERLAY[dxy][bucket] ?? 0;
  return clampScore(base + infAdj + dxyAdj);
}

function buildTrafficMap(phase: Phase, inf: number, dxy: DxyTrend) {
  return {
    "Quality": scoreToTraffic(getBucketScore("quality", phase, inf, dxy)),
    "Technology": scoreToTraffic(getBucketScore("technology", phase, inf, dxy)),
    "Financials": scoreToTraffic(getBucketScore("financials", phase, inf, dxy)),
    "China / EM": scoreToTraffic(getBucketScore("chinaEM", phase, inf, dxy)),
    "Travel / Cyclicals": scoreToTraffic(
      Math.round((getBucketScore("travel", phase, inf, dxy) + getBucketScore("cyclical", phase, inf, dxy)) / 2)
    ),
    "Luxury": scoreToTraffic(getBucketScore("luxury", phase, inf, dxy)),
    "Healthcare": scoreToTraffic(getBucketScore("healthcare", phase, inf, dxy)),
    "Defensives": scoreToTraffic(getBucketScore("defensive", phase, inf, dxy)),
    "Gold": scoreToTraffic(getBucketScore("gold", phase, inf, dxy)),
    "Commodities": scoreToTraffic(getBucketScore("commodities", phase, inf, dxy)),
    "Bonds": scoreToTraffic(
      Math.round((getBucketScore("bondShort", phase, inf, dxy) + getBucketScore("bondLong", phase, inf, dxy)) / 2)
    ),
    "Cash": scoreToTraffic(getBucketScore("cashETF", phase, inf, dxy)),
    "Bitcoin": scoreToTraffic(getBucketScore("cryptoCore", phase, inf, dxy)),
  };
}

// --- PICKS DETERMINISTICI DALLA WATCHLIST ---
function getItemScore(item: WatchItem, phase: Phase, inf: number, dxy: DxyTrend) {
  const bucketScore = getBucketScore(item.bucket, phase, inf, dxy);
  const riskAdj = RISKCLASS_OVERLAY[phase][item.riskClass] ?? 0;
  return bucketScore + riskAdj;
}

function pickSuggestions(phase: Phase, inf: number, dxy: DxyTrend) {
  const ranked = WATCHLIST
    .map(item => ({ ...item, score: getItemScore(item, phase, inf, dxy) }))
    .filter(item => item.score >= 1)
    .sort((a, b) => b.score - a.score);

  return {
    stocks: ranked.filter(x => x.type === "stock").slice(0, 12),
    etfs: ranked.filter(x => x.type === "etf").slice(0, 10),
    crypto: ranked.filter(x => x.type === "crypto").slice(0, 8),
  };
}

// --- LOGICA DI ALLOCAZIONE ---
const ASSET_KEYS = ["azioni", "gold", "materiePrime", "obbligazioni", "cash", "bitcoin"];

function rebalance(w: Record<string, number>): Record<string, number> {
  ASSET_KEYS.forEach(k => w[k] = Math.max(0, w[k] || 0));
  const total = ASSET_KEYS.reduce((sum, key) => sum + (w[key] || 0), 0);
  if (total === 0) return w;
  const scale = 100 / total;
  ASSET_KEYS.forEach(key => { w[key] = Math.round((w[key] * scale) * 10) / 10; });
  return w;
}

// Inflazione phase-sensitive
function applyInflationDeltas(w: Record<string, number>, inf: number, phase: Phase, profile: Profile) {
  const reg = level(inf);
  const eqSweetBoostByPhase: Record<Phase, number> = {
    Rebound: 6, Calm: 8, Speculation: 2, Turbulence: -4,
  };

  if (reg === "deflation") {
    w.azioni -= 10; w.obbligazioni += 14; w.materiePrime -= 8; w.gold += 2;
  } else if (reg === "low") {
    w.azioni -= 3; w.obbligazioni += 8; w.materiePrime -= 4; w.gold -= 1;
  } else if (reg === "sweet") {
    w.azioni += eqSweetBoostByPhase[phase];
    w.obbligazioni += phase === "Calm" ? 2 : 0;
    w.materiePrime -= phase === "Calm" ? 4 : 1;
    w.gold -= 2;
  } else if (reg === "high") {
    w.azioni -= phase === "Calm" ? 4 : 7;
    w.obbligazioni -= 8; w.gold += 5; w.materiePrime += 8;
  } else { // veryHigh
    w.azioni -= 10; w.obbligazioni -= 12; w.gold += 8; w.materiePrime += 12;
  }

  if (reg === "deflation") {
    if (profile === "Conservative") w.obbligazioni = Math.max(w.obbligazioni, 45);
    if (profile === "Default") w.obbligazioni = Math.max(w.obbligazioni, 35);
  }

  return rebalance(w);
}

// DXY Wrecking Ball corretto
function applyDxyImpact(w: Record<string, number>, dxy: DxyTrend, profile: Profile) {
  if (dxy !== "Bullish") return w;
  const impactFactor = profile === "Aggressive" ? 1.0 : 0.8;

  const cutCommodities = w.materiePrime * 0.25 * impactFactor;
  const cutBtc = w.bitcoin * 0.35 * impactFactor;
  const cutGold = w.gold * 0.05 * impactFactor;
  const cutEq = w.azioni * 0.08 * impactFactor;

  w.materiePrime -= cutCommodities;
  w.bitcoin -= cutBtc;
  w.gold -= cutGold;
  w.azioni -= cutEq;

  const freedCapital = cutCommodities + cutBtc + cutGold + cutEq;
  w.cash += freedCapital * 0.65;
  w.obbligazioni += freedCapital * 0.35;

  return rebalance(w);
}

function applyBTC(w: Record<string, number>, includeBTC: boolean, profile: Profile, phase: Phase, inf: number) {
  const cap = profile === "Aggressive" ? 20 : (profile === "Conservative" ? 0 : 10);
  let target = w.bitcoin ?? 0;
  if (!includeBTC || cap === 0 || phase === "Turbulence") target = 0;
  else if (phase === "Speculation") target = Math.min(8, cap);
  else if (phase === "Rebound" || phase === "Calm") {
    const reg = level(inf);
    target = (reg === "sweet" || reg === "high") ? cap : Math.min(8, cap);
  }
  const delta = Math.round((target - (w.bitcoin || 0)) * 10) / 10;
  if (delta !== 0) {
    w.bitcoin = Math.round(target * 10) / 10;
    w.azioni = Math.max(0, Math.round((w.azioni - delta) * 10) / 10);
  }
  return rebalance(w);
}

function applyCashOverride(w: Record<string, number>, customCash: number | null) {
  if (customCash == null) return w;
  const desired = clamp(Number(customCash), 0, 100);
  const otherKeys = ["azioni", "gold", "materiePrime", "obbligazioni", "bitcoin"];
  const sumOthers = otherKeys.reduce((a, k) => a + (w[k] || 0), 0);
  const scale = sumOthers > 0 ? (100 - desired) / sumOthers : 0;
  otherKeys.forEach(k => w[k] = Math.round((w[k] * scale) * 10) / 10);
  w.cash = Math.round(desired * 10) / 10;
  return w;
}

function enforceMin5(w: Record<string, number>, lockCash: boolean) {
  let freed = 0;
  ASSET_KEYS.forEach(k => { if (w[k] > 0 && w[k] < 5) { freed += w[k]; w[k] = 0; } });
  const order = ["azioni", "materiePrime", "gold"];
  order.forEach(k => { if (freed <= 0) return; const add = Math.min(freed, 100 - (w[k] || 0)); w[k] = Math.round(((w[k] || 0) + add) * 10) / 10; freed -= add; });
  if (!lockCash && freed > 0) { const add = Math.min(freed, 100 - (w.cash || 0)); w.cash = Math.round(((w.cash || 0) + add) * 10) / 10; freed -= add; }
  return rebalance(w);
}

// --- TESTI ---
const PHASE_BLURB: Record<Phase, string> = {
  Rebound: "La liquidità torna e la curva tende a irripidire: si può aumentare il rischio in modo selettivo, privilegiando quality, ciclici e aree in recupero.",
  Calm: "Fase costruttiva: leadership di quality e tecnologia profittevole, con partecipazione ampia ma ancora ordinata. Il rischio è ben remunerato.",
  Speculation: "Fase tardiva: il mercato può ancora salire, ma il rapporto rischio/rendimento peggiora. Evita di inseguire tecnologia e high beta; aumenta selettività, cash, difensivi e strumenti di protezione.",
  Turbulence: "Risk-off: preserva capitale e collaterale. Favorisci cash, difensivi, healthcare e oro; riduci beta, crypto e ciclici.",
};

function inflationLine(inf: number) {
  const reg = level(inf);
  if (reg === "deflation") return "Deflazione (<0%): +Obbligazioni forte (guadagno reale), -Azioni, -Materie Prime. Scenario molto negativo per gli asset di rischio.";
  if (reg === "low") return "Inflazione bassa (<1.5%): +Obbligazioni, -Materie Prime. Si privilegia la duration.";
  if (reg === "sweet") return "Sweet spot (1.5-3.5%): +Azioni forte. È il regime ideale per gli asset di rischio.";
  if (reg === "high") return "Inflazione alta (3.5-5%): +Materie Prime/Gold, -Obbligazioni, -Azioni. Si cerca protezione.";
  return "Inflazione molto alta (>5%): +Materie Prime forte, +Gold, -Obbligazioni forte, -Azioni. Massima protezione inflazionistica.";
}

// --- TTS HELPERS ---
function base64ToArrayBuffer(base64: string) { const binaryString = window.atob(base64); const len = binaryString.length; const bytes = new Uint8Array(len); for (let i = 0; i < len; i++) { bytes[i] = binaryString.charCodeAt(i); } return bytes.buffer; }
function pcmToWav(pcmData: Int16Array, sampleRate: number) { const numChannels = 1; const bitsPerSample = 16; const blockAlign = (numChannels * bitsPerSample) / 8; const byteRate = sampleRate * blockAlign; const dataSize = pcmData.length * (bitsPerSample / 8); const buffer = new ArrayBuffer(44 + dataSize); const view = new DataView(buffer); function writeString(offset: number, str: string) { for (let i = 0; i < str.length; i++) { view.setUint8(offset + i, str.charCodeAt(i)); } } writeString(0, 'RIFF'); view.setUint32(4, 36 + dataSize, true); writeString(8, 'WAVE'); writeString(12, 'fmt '); view.setUint32(16, 16, true); view.setUint16(20, 1, true); view.setUint16(22, numChannels, true); view.setUint32(24, sampleRate, true); view.setUint32(28, byteRate, true); view.setUint16(32, blockAlign, true); view.setUint16(34, bitsPerSample, true); writeString(36, 'data'); view.setUint32(40, dataSize, true); const pcmAsDataView = new DataView(pcmData.buffer); for (let i = 0; i < pcmData.length; i++) { view.setInt16(44 + i * 2, pcmAsDataView.getInt16(i * 2, true), true); } return new Blob([view], { type: 'audio/wav' }); }

// ==================== COMPONENT ====================
export default function App() {
  const [profile, setProfile] = useState<Profile>("Default");
  const [regionPhases, setRegionPhases] = useState<RegionPhases>({ USA: "Calm", Eurozona: "Rebound", Cina: "Turbulence" });

  const [inflationUSA, setInflationUSA] = useState(2.5);
  const [inflationEU, setInflationEU] = useState(2.0);
  const [inflationCN, setInflationCN] = useState(0.5);
  const [dxyTrend, setDxyTrend] = useState<DxyTrend>("Neutral");
  const [customCash, setCustomCash] = useState<number | null>(null);
  const [includeBTC, setIncludeBTC] = useState(true);

  const [analysis, setAnalysis] = useState("");
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);
  const [errorAnalysis, setErrorAnalysis] = useState("");
  const [isTtsLoading, setIsTtsLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isInstrumentLoading, setIsInstrumentLoading] = useState(false);
  const [selectedInstrument, setSelectedInstrument] = useState<{ name: string; ticker?: string } | null>(null);
  const [instrumentAnalysis, setInstrumentAnalysis] = useState("");
  const [instrumentError, setInstrumentError] = useState("");
  const [isBacktestingLoading, setIsBacktestingLoading] = useState(false);
  const [backtestAnalysis, setBacktestAnalysis] = useState("");
  const [backtestError, setBacktestError] = useState("");
  const [historicalScenario, setHistoricalScenario] = useState<string>("stagflation_70s");
  const [isRiskLoading, setIsRiskLoading] = useState(false);
  const [riskAnalysis, setRiskAnalysis] = useState("");
  const [riskError, setRiskError] = useState("");
  const [isMacroLoading, setIsMacroLoading] = useState(false);
  const [macroAnalysis, setMacroAnalysis] = useState("");
  const [macroError, setMacroError] = useState("");

  const aggregatePhase = useMemo<Phase>(() => {
    const phaseScores: Record<Phase, number> = { Rebound: 0, Calm: 1, Speculation: 2, Turbulence: 3 };
    const weights: Record<Region, number> = { USA: 0.5, Eurozona: 0.3, Cina: 0.2 };
    const score = REGIONS.reduce((acc, region) => acc + phaseScores[regionPhases[region]] * weights[region], 0);
    if (score < 0.5) return "Rebound";
    if (score < 1.5) return "Calm";
    if (score < 2.5) return "Speculation";
    return "Turbulence";
  }, [regionPhases]);

  const globalInflation = useMemo(() => {
    return (inflationUSA * 0.5) + (inflationEU * 0.3) + (inflationCN * 0.2);
  }, [inflationUSA, inflationEU, inflationCN]);

  const finalMix = useMemo(() => {
    let w: Record<string, number> = { ...PRESETS[profile][aggregatePhase] };
    w = applyInflationDeltas(w, globalInflation, aggregatePhase, profile);
    w = applyBTC(w, includeBTC, profile, aggregatePhase, globalInflation);
    w = applyDxyImpact(w, dxyTrend, profile);
    const cashLocked = customCash != null;
    w = applyCashOverride(w, customCash);
    w = enforceMin5(w, cashLocked);
    return w;
  }, [profile, aggregatePhase, globalInflation, includeBTC, customCash, dxyTrend]);

  const callGeminiApi = async (prompt: string) => {
    const chatHistory = [{ role: "user", parts: [{ text: prompt }] }];
    const payload = { contents: chatHistory };
    const apiKey = "";
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${apiKey}`;
    let response!: Response;
    let retries = 0;
    const maxRetries = 3;
    let delay = 1000;
    while (retries < maxRetries) {
      response = await fetch(apiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (response.ok) break;
      await new Promise(resolve => setTimeout(resolve, delay));
      delay *= 2;
      retries++;
    }
    if (!response.ok) throw new Error(`API request failed after ${maxRetries} retries.`);
    const result = await response.json();
    if (result.candidates?.[0]?.content?.parts?.[0]?.text) {
      return result.candidates[0].content.parts[0].text;
    }
    throw new Error("Invalid API response structure.");
  };

  const handleGenerateAnalysis = async () => {
    setIsLoadingAnalysis(true); setAnalysis(""); setErrorAnalysis("");
    const prompt = `Sei un portfolio strategist esperto. Analizza lo scenario di mercato e l'allocazione di portafoglio risultante.

    DATI MACRO:
    - Fase Ciclo Aggregata: ${aggregatePhase} (USA:${regionPhases.USA}, EU:${regionPhases.Eurozona}, Cina:${regionPhases.Cina})
    - Inflazione Regionale: USA ${inflationUSA.toFixed(1)}%, EU ${inflationEU.toFixed(1)}%, Cina ${inflationCN.toFixed(1)}% (Globale Effettiva: ${globalInflation.toFixed(1)}%)
    - Trend DXY (Dollaro): ${dxyTrend}

    CONTESTO TEORICO DA USARE:
    Fai riferimento implicito alla curva "Valuation vs Inflation". Ricorda che:
    - Il "Sweet Spot" per le valutazioni azionarie (Equity Multiples) è tipicamente con inflazione tra 1.5% e 3% (dove spesso si trovano USA/EU in fasi positive).
    - La Deflazione (<1%) è negativa per le azioni (es. Cina se inflazione bassa) e favorisce i Bond.
    - L'Inflazione alta (>4-5%) comprime i multipli azionari e favorisce Commodities/Gold.
    - Se il DXY è "Bullish", cita l'effetto "Wrecking Ball" che drena liquidità globale e colpisce asset rischiosi ed emergenti.

    ALLOCAZIONE SUGGERITA (%):
    Azioni=${finalMix.azioni}, Gold=${finalMix.gold}, Materie Prime=${finalMix.materiePrime}, Obbligazioni=${finalMix.obbligazioni}, Cash=${finalMix.cash}, Bitcoin=${finalMix.bitcoin}.

    Scrivi un'analisi concisa (2-3 paragrafi) in italiano.`;
    try { const text = await callGeminiApi(prompt); setAnalysis(text); } catch (error) { console.error("Error generating analysis:", error); setErrorAnalysis("Errore durante la generazione dell'analisi."); } finally { setIsLoadingAnalysis(false); }
  };

  const handleInstrumentClick = async (instrument: { name: string; ticker?: string }) => {
    setSelectedInstrument(instrument);
    setIsInstrumentLoading(true); setInstrumentAnalysis(""); setInstrumentError("");
    const instrumentIdentifier = instrument.ticker ? `${instrument.name} (${instrument.ticker})` : instrument.name;
    const prompt = `Sei un analista finanziario. Fornisci una tesi d'investimento concisa per ${instrumentIdentifier}. Spiega il suo potenziale ruolo in un portafoglio durante la fase aggregata di '${aggregatePhase}' del ciclo economico, con un'inflazione globale del ${globalInflation.toFixed(1)}%. Considera anche il trend del DXY (${dxyTrend}). Limita la risposta a 2-4 frasi. Lingua: italiano.`;
    try { const text = await callGeminiApi(prompt); setInstrumentAnalysis(text); } catch (error) { console.error("Error generating instrument analysis:", error); setInstrumentError("Impossibile generare l'analisi per questo strumento."); } finally { setIsInstrumentLoading(false); }
  };

  const handleGenerateTts = async () => {
    if (!analysis) return;
    setIsTtsLoading(true);
    if (audioRef.current?.src) { URL.revokeObjectURL(audioRef.current.src); }
    const payload = { contents: [{ parts: [{ text: `Parla con tono professionale e chiaro: ${analysis}` }] }], generationConfig: { responseModalities: ["AUDIO"], speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: "Kore" } } } }, model: "gemini-2.5-flash-preview-tts" };
    const apiKey = "";
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key=${apiKey}`;
    try {
      const response = await fetch(apiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (!response.ok) throw new Error(`TTS API request failed with status ${response.status}`);
      const result = await response.json();
      const part = result?.candidates?.[0]?.content?.parts?.[0];
      const audioData = part?.inlineData?.data;
      const mimeType = part?.inlineData?.mimeType;
      if (audioData && mimeType?.startsWith("audio/")) {
        const sampleRateMatch = mimeType.match(/rate=(\d+)/);
        if (!sampleRateMatch) throw new Error("Sample rate not found in mimeType");
        const sampleRate = parseInt(sampleRateMatch[1], 10);
        const pcmData = base64ToArrayBuffer(audioData);
        const pcm16 = new Int16Array(pcmData);
        const wavBlob = pcmToWav(pcm16, sampleRate);
        const audioUrl = URL.createObjectURL(wavBlob);
        if (audioRef.current) { audioRef.current.src = audioUrl; audioRef.current.play(); }
      } else { throw new Error("Audio data not found in response."); }
    } catch (error) { console.error("Error generating TTS:", error); } finally { setIsTtsLoading(false); }
  };

  const handleGenerateBacktest = async () => {
    setIsBacktestingLoading(true); setBacktestAnalysis(""); setBacktestError("");
    const scenarioName = HISTORICAL_REGIMES[historicalScenario as keyof typeof HISTORICAL_REGIMES];
    const allocationString = Object.entries(finalMix).filter(([, val]) => val > 0).map(([key, val]) => `${key}: ${val}%`).join(', ');
    const prompt = `Sei un economista storico e portfolio strategist. Analizza qualitativamente come si sarebbe comportato il seguente portafoglio durante il regime macroeconomico storico della "${scenarioName}": ${allocationString}. Descrivi i probabili punti di forza e di debolezza di questa allocazione in quel contesto specifico. Sii conciso (2-3 paragrafi) e focalizzati sulle dinamiche chiave di quel periodo. Lingua: italiano.`;
    try { const text = await callGeminiApi(prompt); setBacktestAnalysis(text); } catch (error) { console.error("Error generating backtest analysis:", error); setBacktestError("Errore durante la generazione dell'analisi storica."); } finally { setIsBacktestingLoading(false); }
  };

  const handleGenerateRiskAnalysis = async () => {
    setIsRiskLoading(true); setRiskAnalysis(""); setRiskError("");
    const allocationString = Object.entries(finalMix).filter(([, val]) => val > 0).map(([key, val]) => `${key}: ${val}%`).join(', ');
    const prompt = `Sei un risk manager. Identifica i 3 principali rischi (macroeconomici, geopolitici o di mercato) per il seguente portafoglio: ${allocationString}. Contesto: DXY Trend=${dxyTrend}, Inflazione USA=${inflationUSA}%, EU=${inflationEU}%, CN=${inflationCN}%. Considera la divergenza e il rischio cambio. Per ogni rischio, fornisci una breve spiegazione (1-2 frasi). Lingua: italiano. Formatta la risposta con un titolo per ogni rischio.`;
    try { const text = await callGeminiApi(prompt); setRiskAnalysis(text); } catch (error) { console.error("Error generating risk analysis:", error); setRiskError("Errore durante la generazione dell'analisi dei rischi."); } finally { setIsRiskLoading(false); }
  };

  const handleGenerateMacroContext = async () => {
    setIsMacroLoading(true); setMacroAnalysis(""); setMacroError("");
    const prompt = `Sei un analista macroeconomico.
    DATI:
    - Fasi Ciclo: USA '${regionPhases.USA}', Eurozona '${regionPhases.Eurozona}', Cina '${regionPhases.Cina}'.
    - Inflazione: USA ${inflationUSA.toFixed(1)}%, Eurozona ${inflationEU.toFixed(1)}%, Cina ${inflationCN.toFixed(1)}%.
    - DXY Trend: ${dxyTrend}.

    ANALISI RICHIESTA:
    Scrivi un breve riassunto (2-3 paragrafi) delle implicazioni globali.
    1. Analizza le divergenze di inflazione usando la teoria del "Sweet Spot" (2-3% buono per Equity) vs rischi Deflazionistici (es. Cina).
    2. Commenta l'impatto del Dollaro (${dxyTrend}): se Bullish, è una "palla da demolizione" (wrecking ball) per la liquidità globale e gli asset emergenti?

    Lingua: italiano.`;
    try { const text = await callGeminiApi(prompt); setMacroAnalysis(text); } catch (error) { console.error("Error generating macro context:", error); setMacroError("Errore durante la generazione del contesto macro."); } finally { setIsMacroLoading(false); }
  };

  const pieData = useMemo(() => [
    { name: "Azioni", value: finalMix.azioni, fill: COLORS.azioni },
    { name: "Gold", value: finalMix.gold, fill: COLORS.gold },
    { name: "Materie Prime", value: finalMix.materiePrime, fill: COLORS.materiePrime },
    { name: "Obbligazioni", value: finalMix.obbligazioni, fill: COLORS.obbligazioni },
    { name: "Cash", value: finalMix.cash, fill: COLORS.cash },
    { name: "Bitcoin", value: finalMix.bitcoin, fill: COLORS.bitcoin },
  ].filter(d => d.value > 0), [finalMix]);

  const sem = useMemo(() => buildTrafficMap(aggregatePhase, globalInflation, dxyTrend), [aggregatePhase, globalInflation, dxyTrend]);
  const picks = useMemo(() => pickSuggestions(aggregatePhase, globalInflation, dxyTrend), [aggregatePhase, globalInflation, dxyTrend]);

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-amber-50">
        <div className="p-4 md:p-6 max-w-7xl mx-auto space-y-6">
          <motion.header initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-3xl font-bold">Allocazione Dinamica degli Asset</h1>
            <p className="text-gray-600">Un motore di allocazione <b>adattivo</b> che calibra il portafoglio al <b>ciclo di liquidità globale</b>, alle <b>divergenze d'inflazione</b> e al <b>Dollaro (DXY)</b>.</p>
          </motion.header>

          <div className="grid lg:grid-cols-3 gap-6">
            {/* COLONNA SINISTRA: INPUT */}
            <div className="lg:col-span-1 space-y-6">
              <Card>
                <CardHeader><CardTitle>1. Definisci il Contesto</CardTitle></CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <label className="text-sm font-semibold mb-2 block">Profilo di Rischio</label>
                    <Tabs value={profile} onValueChange={(v) => setProfile(v as Profile)}>
                      <TabsList className="grid grid-cols-3">
                        {PROFILES.map(p => <TabsTrigger key={p} value={p}>{p === "Conservative" ? "Conservativo" : p}</TabsTrigger>)}
                      </TabsList>
                    </Tabs>
                  </div>

                  <div className="space-y-3">
                    <label className="text-sm font-semibold flex items-center gap-2"><TrendingUp className="w-4 h-4" />Inflazione Attesa (YoY)</label>
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-gray-500"><span>USA</span><span>{inflationUSA.toFixed(1)}%</span></div>
                      <Slider value={[inflationUSA]} min={-2} max={10} step={0.1} onValueChange={(v) => setInflationUSA(v[0])} className="py-1" />
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-gray-500"><span>Eurozona</span><span>{inflationEU.toFixed(1)}%</span></div>
                      <Slider value={[inflationEU]} min={-2} max={10} step={0.1} onValueChange={(v) => setInflationEU(v[0])} className="py-1" />
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-gray-500"><span>Cina</span><span>{inflationCN.toFixed(1)}%</span></div>
                      <Slider value={[inflationCN]} min={-2} max={10} step={0.1} onValueChange={(v) => setInflationCN(v[0])} className="py-1" />
                    </div>
                    <div className="pt-1 text-xs text-center text-blue-600 font-medium">Globale Effettiva (Ponderata): {globalInflation.toFixed(1)}%</div>
                  </div>

                  <div className="space-y-3 pt-2 border-t">
                    <label className="text-sm font-semibold flex items-center gap-2"><DollarSign className="w-4 h-4" />Trend DXY (USD Index)</label>
                    <Tabs value={dxyTrend} onValueChange={(v) => setDxyTrend(v as DxyTrend)}>
                      <TabsList className="grid grid-cols-3">
                        <TabsTrigger value="Bearish" className="text-red-600 data-[state=active]:text-red-700">Bearish</TabsTrigger>
                        <TabsTrigger value="Neutral">Neutral</TabsTrigger>
                        <TabsTrigger value="Bullish" className="text-green-600 data-[state=active]:text-green-700 font-bold">Bullish</TabsTrigger>
                      </TabsList>
                    </Tabs>
                    {dxyTrend === "Bullish" && <p className="text-xs text-amber-600 italic">Effetto "Wrecking Ball" attivo: penalità su Commodities, Crypto e EM.</p>}
                  </div>

                  <div className="grid grid-cols-2 gap-4 items-center pt-2 border-t">
                    <div><label className="text-sm font-semibold">Cash Obbligatorio %</label><Input type="number" placeholder="Default" onChange={(e) => setCustomCash(e.target.value === '' ? null : Number(e.target.value))} className="h-8 mt-1" /></div>
                    <div className="flex items-center gap-3 pt-6"><Switch checked={includeBTC} onCheckedChange={setIncludeBTC} /><span className="text-sm">Bitcoin</span></div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2"><Globe className="w-5 h-5" />Dashboard Globale del Ciclo</CardTitle></CardHeader>
                <CardContent className="space-y-4">
                  {REGIONS.map(region => (
                    <div key={region}>
                      <label className="text-sm font-semibold">{region}</label>
                      <Tabs value={regionPhases[region]} onValueChange={(v) => setRegionPhases(p => ({ ...p, [region]: v as Phase }))}>
                        <TabsList className="grid grid-cols-4">{PHASES.map(p => <TabsTrigger key={p} value={p} className="text-xs px-1">{p}</TabsTrigger>)}</TabsList>
                      </Tabs>
                    </div>
                  ))}
                  <Button onClick={handleGenerateMacroContext} disabled={isMacroLoading} className="w-full mt-2">
                    {isMacroLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Analisi...</> : "Genera Contesto Macro"}
                  </Button>
                  <AnimatePresence>
                    {isMacroLoading && (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-2 text-gray-600 text-sm"><p>Analisi del contesto globale in corso...</p></motion.div>)}
                  </AnimatePresence>
                  <AnimatePresence>
                    {macroAnalysis && !isMacroLoading && (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="prose prose-sm max-w-none p-3 bg-blue-50/50 rounded-lg border border-blue-200 text-xs mt-2" style={{ whiteSpace: 'pre-wrap' }}>{macroAnalysis}</motion.div>)}
                  </AnimatePresence>
                  <AnimatePresence>
                    {macroError && !isMacroLoading && (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-red-600 bg-red-50 p-2 rounded-lg text-xs mt-2">{macroError}</motion.div>)}
                  </AnimatePresence>
                </CardContent>
              </Card>
            </div>

            {/* COLONNA DESTRA: OUTPUT */}
            <div className="lg:col-span-2 space-y-6">
              <Card>
                <CardHeader><CardTitle>2. Allocazione Risultante</CardTitle></CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-4 items-center">
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart><Pie data={pieData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80}>{pieData.map((e, i) => (<Cell key={i} fill={e.fill} />))}</Pie><Tooltip formatter={(v) => `${v}%`} /><Legend wrapperStyle={{ fontSize: "12px" }} /></PieChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={pieData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}><XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} /><YAxis tickFormatter={(v) => `${v}%`} /><Tooltip formatter={(v) => `${v}%`} /><Bar dataKey="value" radius={[6, 6, 0, 0]}>{pieData.map((entry, index) => (<Cell key={`cell-${index}`} fill={entry.fill} />))}</Bar></BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  <div className="mt-4 text-center"><p className="text-sm text-gray-600">Fase aggregata del ciclo: <Badge>{aggregatePhase}</Badge></p></div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>3. Analisi e Strategia</CardTitle></CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-gray-700">{PHASE_BLURB[aggregatePhase]}</p>
                  <div className={`text-sm text-gray-700 border rounded-xl p-3 ${globalInflation < 0 ? 'bg-red-50 border-red-200' : 'bg-slate-50'}`}>{inflationLine(globalInflation)}</div>
                  <div className="flex justify-end items-center gap-2 pt-2">
                    <Button onClick={handleGenerateAnalysis} disabled={isLoadingAnalysis}>
                      {isLoadingAnalysis ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Generazione...</> : "Genera Analisi Allocazione"}
                    </Button>
                    {analysis && !isLoadingAnalysis && (
                      <Button onClick={handleGenerateTts} disabled={isTtsLoading} variant="outline" size="icon">
                        {isTtsLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Volume2 className="h-4 w-4" />}
                      </Button>
                    )}
                  </div>
                  <AnimatePresence>
                    {analysis && !isLoadingAnalysis && (<motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="prose prose-sm max-w-none p-4 bg-blue-50/50 rounded-lg border border-blue-200" style={{ whiteSpace: 'pre-wrap' }}>{analysis}</motion.div>)}
                  </AnimatePresence>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* ANALISI AVANZATA */}
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <Card>
              <CardHeader><CardTitle>4. Analisi Avanzata</CardTitle></CardHeader>
              <CardContent className="p-4">
                <Tabs defaultValue="backtest">
                  <TabsList>
                    <TabsTrigger value="backtest"><History className="w-4 h-4 mr-2" />Backtest di Regime</TabsTrigger>
                    <TabsTrigger value="risks"><ShieldAlert className="w-4 h-4 mr-2" />Analisi Rischi</TabsTrigger>
                  </TabsList>
                  <TabsContent value="backtest" className="pt-4 space-y-4">
                    <div className="flex items-center gap-4 flex-wrap">
                      <select value={historicalScenario} onChange={(e) => setHistoricalScenario(e.target.value)} className="flex h-10 w-full md:w-auto flex-grow items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                        <option disabled>Seleziona un regime o shock...</option>
                        {Object.entries(HISTORICAL_REGIMES).map(([key, value]) => (<option key={key} value={key}>{value}</option>))}
                      </select>
                      <Button onClick={handleGenerateBacktest} disabled={isBacktestingLoading} className="flex-shrink-0">
                        {isBacktestingLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Analisi...</> : "Esegui Analisi"}
                      </Button>
                    </div>
                    <AnimatePresence>{isBacktestingLoading && (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-4 text-gray-600"><p>Analisi del regime storico in corso...</p></motion.div>)}</AnimatePresence>
                    <AnimatePresence>{backtestAnalysis && !isBacktestingLoading && (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="prose prose-sm max-w-none p-4 bg-slate-50 rounded-lg border" style={{ whiteSpace: 'pre-wrap' }}>{backtestAnalysis}</motion.div>)}</AnimatePresence>
                    <AnimatePresence>{backtestError && !isBacktestingLoading && (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-red-600 bg-red-50 p-3 rounded-lg text-sm">{backtestError}</motion.div>)}</AnimatePresence>
                  </TabsContent>
                  <TabsContent value="risks" className="pt-4 space-y-4">
                    <div className="flex justify-end">
                      <Button onClick={handleGenerateRiskAnalysis} disabled={isRiskLoading}>
                        {isRiskLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Analisi...</> : "Identifica Rischi Principali"}
                      </Button>
                    </div>
                    <AnimatePresence>{isRiskLoading && (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-4 text-gray-600"><p>Identificazione dei rischi in corso...</p></motion.div>)}</AnimatePresence>
                    <AnimatePresence>{riskAnalysis && !isRiskLoading && (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="prose prose-sm max-w-none p-4 bg-amber-50 rounded-lg border border-amber-200" style={{ whiteSpace: 'pre-wrap' }}>{riskAnalysis}</motion.div>)}</AnimatePresence>
                    <AnimatePresence>{riskError && !isRiskLoading && (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-red-600 bg-red-50 p-3 rounded-lg text-sm">{riskError}</motion.div>)}</AnimatePresence>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </motion.div>

          {/* SEMAFORO + PESI */}
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="grid lg:grid-cols-2 gap-6">
            <Card>
              <CardContent className="p-4 space-y-2">
                <h2 className="text-xl font-semibold">Semaforo asset / settori</h2>
                <div className="grid md:grid-cols-2 gap-3">
                  {Object.entries(sem).map(([k, v]) => {
                    const color = v === "green" ? "bg-green-600" : v === "orange" ? "bg-orange-500" : "bg-red-600";
                    return (
                      <div key={k} className="flex items-center justify-between border rounded-xl p-3">
                        <span className="text-sm">{k}</span>
                        <span className={`text-xs text-white px-2 py-1 rounded ${color}`}>{v.toUpperCase()}</span>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 space-y-3">
                <h2 className="text-xl font-semibold">Pesi Suggeriti</h2>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {pieData.map(({ name, value, fill }) => (
                    <div key={name} className="flex items-center justify-between border rounded-xl px-3 py-2">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: fill }}></div>
                        <span className="capitalize">{name}</span>
                      </div>
                      <Badge variant="secondary">{pct(value)}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* PROPOSTE DINAMICHE - Azioni, ETF, Crypto (no Fondi) */}
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
            <Card>
              <CardContent className="p-4 space-y-4">
                <h2 className="text-xl font-semibold flex items-center gap-2"><Shield className="w-5 h-5" />Proposte dinamiche</h2>
                <Tabs defaultValue="stocks" className="w-full">
                  <TabsList>
                    <TabsTrigger value="stocks">Azioni</TabsTrigger>
                    <TabsTrigger value="etfs">ETF</TabsTrigger>
                    <TabsTrigger value="crypto">Crypto</TabsTrigger>
                  </TabsList>
                  <TabsContent value="stocks">
                    <div className="flex flex-wrap gap-2 mt-2">
                      {picks.stocks.map(x => (
                        <Button key={x.ticker} variant="secondary" size="sm" className="h-auto" onClick={() => handleInstrumentClick({ name: x.name, ticker: x.ticker })}>
                          {x.ticker} · {x.name} <Info className="w-3 h-3 ml-2" />
                        </Button>
                      ))}
                      {picks.stocks.length === 0 && <p className="text-sm text-gray-500 italic">Nessun titolo suggerito in questo regime.</p>}
                    </div>
                  </TabsContent>
                  <TabsContent value="etfs">
                    <div className="flex flex-wrap gap-2 mt-2">
                      {picks.etfs.map(x => (
                        <Button key={x.ticker} variant="outline" size="sm" className="h-auto" onClick={() => handleInstrumentClick({ name: x.name, ticker: x.ticker })}>
                          {x.ticker} · {x.name} <Info className="w-3 h-3 ml-2" />
                        </Button>
                      ))}
                      {picks.etfs.length === 0 && <p className="text-sm text-gray-500 italic">Nessun ETF suggerito in questo regime.</p>}
                    </div>
                  </TabsContent>
                  <TabsContent value="crypto">
                    <div className="flex flex-wrap gap-2 mt-2">
                      {picks.crypto.map(x => (
                        <Button key={x.ticker} variant="outline" size="sm" className="h-auto" onClick={() => handleInstrumentClick({ name: x.name, ticker: x.ticker })}>
                          {x.ticker} · {x.name} <Info className="w-3 h-3 ml-2" />
                        </Button>
                      ))}
                      {picks.crypto.length === 0 && <p className="text-sm text-gray-500 italic">Nessuna crypto suggerita in questo regime.</p>}
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </motion.div>

          <footer className="text-xs text-gray-500 mt-2 text-center">
            <p>Dynamic Asset Allocation v12. Modello basato sul ciclo di liquidità globale, divergenze di inflazione e Dollaro.</p>
          </footer>
        </div>
        <audio ref={audioRef} style={{ display: 'none' }} />
      </div>

      {/* MODAL STRUMENTO */}
      <AnimatePresence>
        {selectedInstrument && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={() => setSelectedInstrument(null)}>
            <motion.div initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.9, y: 20 }} className="bg-white rounded-2xl shadow-xl w-full max-w-lg relative" onClick={(e) => e.stopPropagation()}>
              <Card>
                <CardContent className="p-6 space-y-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-bold">{selectedInstrument.name}</h3>
                      {selectedInstrument.ticker && <p className="text-sm text-gray-500">{selectedInstrument.ticker}</p>}
                    </div>
                    <Button variant="ghost" size="icon" className="rounded-full" onClick={() => setSelectedInstrument(null)}><X className="w-4 h-4" /></Button>
                  </div>
                  {isInstrumentLoading && (<div className="flex items-center justify-center h-24 text-gray-600"><Loader2 className="mr-2 h-5 w-5 animate-spin" /><span>Analisi in corso...</span></div>)}
                  {instrumentAnalysis && !isInstrumentLoading && (<p className="text-sm text-gray-800 bg-slate-50 p-3 rounded-lg">{instrumentAnalysis}</p>)}
                  {instrumentError && !isInstrumentLoading && (<p className="text-sm text-red-600 bg-red-50 p-3 rounded-lg">{instrumentError}</p>)}
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
