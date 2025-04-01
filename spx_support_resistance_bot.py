
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# إعدادات البوت
bot_token = "ضع_توكن_البوت"
chat_id = "ضع_chat_id"

# تحميل بيانات SPX500
data = yf.download("^GSPC", interval="15m", period="2d")

# حساب المتوسطات
data["EMA_9"] = data["Close"].ewm(span=9, adjust=False).mean()
data["EMA_21"] = data["Close"].ewm(span=21, adjust=False).mean()

# تحديد الدعوم والمقاومات تلقائياً
highs = data["High"].rolling(window=10).max()
lows = data["Low"].rolling(window=10).min()
levels = list(set(highs.dropna().round(2)).union(set(lows.dropna().round(2))))
levels = sorted(levels)

# آخر شمعتين
latest = data.iloc[-1]
prev = data.iloc[-2]

alerts = []

# كسر أو ارتداد من المستويات
for level in levels:
    if prev["Close"] < level and latest["Close"] > level:
        alerts.append(f"اختراق صاعد للمستوى {level}")
    elif prev["Close"] > level and latest["Close"] < level:
        alerts.append(f"كسر هابط للمستوى {level}")
    elif abs(latest["Close"] - level) < 2:
        alerts.append(f"ارتداد أو اقتراب قوي من {level}")

# تقاطع المتوسطات
if prev["EMA_9"] < prev["EMA_21"] and latest["EMA_9"] > latest["EMA_21"]:
    alerts.append("تقاطع صاعد EMA 9 مع EMA 21")
elif prev["EMA_9"] > prev["EMA_21"] and latest["EMA_9"] < latest["EMA_21"]:
    alerts.append("تقاطع هابط EMA 9 مع EMA 21")

# نماذج الشموع
if latest["Close"] > latest["Open"] and prev["Close"] < prev["Open"] and latest["Close"] > prev["Open"]:
    alerts.append("نموذج ابتلاع صاعد")
elif latest["Close"] < latest["Open"] and prev["Close"] > prev["Open"] and latest["Close"] < prev["Open"]:
    alerts.append("نموذج ابتلاع هابط")

# إرسال التنبيهات
if alerts:
    message = f"تنبيهات SPX500 - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n" + "\n".join(alerts)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={'chat_id': chat_id, 'text': message})
