import os
from dotenv import load_dotenv

load_dotenv()

RESTAURANT_NAME = os.getenv("RESTAURANT_NAME", "AM Restaurant")
TOTAL_TABLES = int(os.getenv("TOTAL_TABLES", 5))
START_HOUR = int(os.getenv("START_HOUR", 10))
END_HOUR = int(os.getenv("END_HOUR", 22))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
TWILIO_WHATSAPP_TO = os.getenv("TWILIO_WHATSAPP_TO")
