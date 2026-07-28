# ==========================================
# BACKTEST CONFIGURATION
# ==========================================

# --- Account Settings ---
INITIAL_BALANCE = 300.0       # ทุนเริ่มต้น (USD)
RISK_PERCENT = 0.03          # ความเสี่ยงต่อไม้ (3% = 0.03)
CONTRACT_SIZE = 1.0         # ขนาดสัญญา (เช่น 100 สำหรับ XAUUSD Standard Lot)

# --- Strategy Parameters ---
TP_RATIO = 2.0             # Risk to Reward Ratio (1:1.82)
ATR_PERIOD = 14              # จำนวนแท่งสำหรับคำนวณ ATR
SL_ATR_MULTIPLIER = 2.0
      # ระยะ SL คิดเป็นกี่เท่าของ ATR
BB_WINDOW = 20
BB_WINDOW_DEV = 2.0

EMA_PERIOD = 200

VOLUME_PERIOD = 20

# --- Market Friction & Execution Settings ---
# ช่วงการสุ่ม Slippage (สัดส่วนต่อ ATR)
SLIPPAGE_MIN_FACTOR = 0.02   # 3% ของ ATR
SLIPPAGE_MAX_FACTOR = 0.05   # 8% ของ ATR

# กรณีต้องการล็อกผลการสุ่มให้รันกี่รอบก็ได้ค่าเดิมเสมอ (Reproducibility)
RANDOM_SEED = 42

# --- Position Management (สำหรับฟีเจอร์อนาคต) ---
USE_TRAILING_STOP = False    # เปิด-ปิด Trailing Stop
BE_TRIGGER_R = 1.2           # ระยะ R ที่จะเลื่อน SL มาบังทุน (Breakeven)