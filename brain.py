import re
import base64
import asyncio
import requests
import dateparser
from datetime import datetime
from edge_tts import Communicate
from database import check, book, cancel_by_phone_date_time


# -------------------- TTS (Stable Voice) --------------------
async def _speak_async(text: str) -> str:
    try:
        communicate = Communicate(
            text=text,
            voice="en-IN-PrabhatNeural",
            rate="+5%"
        )
        audio_bytes = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes.extend(chunk["data"])
        return base64.b64encode(bytes(audio_bytes)).decode()
    except:
        print("TTS Failed")
        return None

def speak(text):
    try:
        return asyncio.run(_speak_async(text))
    except:
        return None

def _say(text, state):
    return text, speak(text), state


# -------------------- Ollama LLM --------------------
def ollama(prompt: str, model="llama3.2:3b") -> str:
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=40
        )
        return (r.json().get("response") or "").strip()
    except:
        return "I didn't catch that. Could you say it again?"


# -------------------- Parsing Helpers --------------------
def parse_date(text):
    text = text.lower().replace("on ", "").replace("the ", "")
    text = re.sub(r"(st|nd|rd|th)", "", text)

    parsed = dateparser.parse(text, settings={"PREFER_DATES_FROM": "future"})
    if not parsed:
        return None

    return parsed.date().strftime("%Y-%m-%d")


def parse_time(text):
    text = text.lower().replace(" ", "").replace(".", "")
    for fmt in ("%I:%M%p", "%I%p"):
        try:
            return datetime.strptime(text, fmt).strftime("%H:%M")
        except:
            pass
    return None


def extract_people(text):
    text = text.lower()
    words = {
        "one":1,"1":1,"two":2,"to":2,"too":2,"2":2,
        "three":3,"3":3,"four":4,"for":4,"4":4,
        "five":5,"5":5,"six":6,"6":6,
        "seven":7,"7":7,"eight":8,"ate":8,"8":8,
        "nine":9,"9":9,"ten":10,"10":10,
        "couple":2,"pair":2,"family":4
    }
    for w,n in words.items():
        if f" {w} " in f" {text} ":
            return n
    nums = re.findall(r"\d+", text)
    return int(nums[0]) if nums else None


# -------------------- MAIN AI LOGIC --------------------
def get_ai_response(message, state):
    msg = (message or "").strip()
    low = msg.lower()

    # ---------- WELCOME ----------
    if msg == "__WELCOME__":
        return _say("Hello, welcome to AM Restaurant. How may I assist you today?", state)

    # ---------- START CANCELLATION ----------
    if any(x in low for x in ["cancel", "remove", "delete"]) and not state.get("step"):
        state.clear()
        state["step"] = "cancel_phone"
        return _say("Sure, please tell me the phone number used for the booking.", state)

    if state.get("step") == "cancel_phone":
        digits = "".join(re.findall(r"\d", msg))
        if len(digits) < 10:
            return _say("Please say the 10 digit phone number clearly.", state)
        state["phone"] = digits[-10:]
        state["step"] = "cancel_date"
        return _say("On which date was the booking? For example: 12 November.", state)

    if state.get("step") == "cancel_date":
        d = parse_date(msg)
        if not d:
            return _say("Please repeat the date clearly.", state)
        state["date"] = d
        state["step"] = "cancel_time"
        return _say("At what time was the booking?", state)

    if state.get("step") == "cancel_time":
        t = parse_time(msg)
        if not t:
            return _say("Please repeat the time clearly, like 7 PM.", state)
        state["time"] = t

        result = cancel_by_phone_date_time(state["phone"], state["date"], state["time"])
        state.clear()
        return _say(result, state)

    # ---------- START BOOKING ----------
    if any(x in low for x in ["book", "reserve", "table"]) and not state.get("step"):
        state.clear()
        state["step"] = "date"
        return _say("Sure, what date should I book the table for?", state)

    step = state.get("step")

    # ---------- BOOKING STEPS ----------
    if step == "date":
        d = parse_date(msg)
        if not d:
            return _say("Please tell the date clearly. For example: 12 November.", state)
        state["date"] = d
        state["step"] = "time"
        return _say("At what time should I make the reservation? For example: 7 PM.", state)

    if step == "time":
        t = parse_time(msg)
        if not t:
            return _say("Please repeat the time clearly.", state)
        if check(state["date"], t) != "ok":
            return _say("Sorry, that time is full. Please choose another.", state)
        state["time"] = t
        state["step"] = "people"
        return _say("How many guests?", state)

    if step == "people":
        n = extract_people(msg)
        if not n:
            return _say("Please tell me the number of guests.", state)
        state["people"] = n
        state["step"] = "name"
        return _say("Under which name should I reserve the table?", state)

    if step == "name":
        state["name"] = msg.title()
        state["step"] = "phone"
        return _say("What phone number should I register?", state)

    if step == "phone":
        digits = "".join(re.findall(r"\d", msg))
        if len(digits) < 10:
            return _say("Please say the 10 digit phone number clearly.", state)

        state["phone"] = digits[-10:]

        result, _qr = book(state["date"], state["time"], state["people"], state["name"], state["phone"])
        state.clear()
        return _say(result + " I have also sent the confirmation & QR code to WhatsApp.", state)

    # ---------- SMALL TALK ----------
    ai = ollama(f"You are a friendly restaurant assistant.\nUser: {msg}\nAssistant:")
    return _say(ai, state)
