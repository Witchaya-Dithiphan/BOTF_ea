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
SL_ATR_MULTIPLIER = 1.8
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

# --- SESSION & TIME FILTERS ---
ENABLE_TIME_FILTER = True
TRADING_START_HOUR = 13      # ช่วงบ่ายเริ่มมี Volume (บ่ายสอง/บ่ายสาม)
TRADING_END_HOUR = 23        # สี่ทุ่ม-ห้าทุ่ม (จบช่วง US peak)

AVOID_FRIDAY_NIGHT = True
FRIDAY_CUTOFF_HOUR = 20

# --- SPREAD FILTER FOR BTC ---
# BTC spread หลักสิบเหรียญ ถือเป็นเรื่องปกติ ต้องตั้งค่าให้เหมาะสม
MAX_ALLOWED_SPREAD = 70.0    # เช่น ยอมรับ spread ได้ไม่เกิน $30 (ปรับตาม broker ที่ใช้)