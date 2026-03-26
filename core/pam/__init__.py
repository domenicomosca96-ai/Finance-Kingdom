"""PAM Engine — re-export from market_data."""
from core.pam.market_data import (
    download_ohlcv, compute_flow, compute_momentum,
    detect_uc1, detect_ur2, detect_dr2, detect_dc1,
    classify_rotation_segment, compute_micro_score,
    run_full_pam, FlowResult, MomentumResult, PatternResult, FullPAMResult,
)
