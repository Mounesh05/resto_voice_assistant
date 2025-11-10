import os
from twilio.rest import Client

# Load from .env
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN") or os.getenv("TWILIO_AUTH")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_NUMBER")   
NGROK_URL = os.getenv("NGROK_URL")                            
OWNER_WHATSAPP = os.getenv("OWNER_WHATSAPP")                 

client = Client(TWILIO_SID, TWILIO_AUTH)


# ✅ Send booking confirmation + QR
def send_booking_whatsapp(date, time, people, name, phone, qr_path):
    if not NGROK_URL:
        print("❌ ERROR: NGROK_URL missing in .env — WhatsApp skipped")
        return

    qr_path = qr_path.replace("\\", "/")
    filename = os.path.basename(qr_path)
    qr_url = f"{NGROK_URL}/static/qr/{filename}"

    text = (
        f"*Booking Confirmed ✅*\n\n"
        f"👤 Name: {name}\n"
        f"📞 +91 {phone}\n"
        f"🗓 Date: {date}\n"
        f"⏰ Time: {time}\n"
        f"👥 Guests: {people}\n\n"
        f"Please show this QR at the entrance.\n"
        f"🔗 Download QR: {qr_url}"
    )

    try:
        customer = f"whatsapp:+91{phone}"

        client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
            to=customer,
            body=text
        )

        client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
            to=customer,
            media_url=[qr_url]
        )

        print(f"✅ Booking WhatsApp sent to customer: +91{phone}")

    except Exception as e:
        print("❌ Failed to send booking message to customer:", e)


    # Notify Owner (optional)
    if OWNER_WHATSAPP:
        try:
            owner_text = f"📩 *NEW BOOKING RECEIVED*\n\n{text}"
            client.messages.create(
                from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
                to=f"whatsapp:{OWNER_WHATSAPP}",
                body=owner_text
            )
            client.messages.create(
                from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
                to=f"whatsapp:{OWNER_WHATSAPP}",
                media_url=[qr_url]
            )
            print("📨 Owner copy sent.")
        except:
            print("⚠️ Could not send owner copy.")



# ✅ Send cancellation message (REQUIRED FUNCTION)
def send_cancellation_whatsapp(date, time, name, phone):
    customer = f"whatsapp:+91{phone}"

    text = (
        f"*Booking Cancelled ❌*\n\n"
        f"👤 Name: {name}\n"
        f"📞 +91 {phone}\n"
        f"🗓 Date: {date}\n"
        f"⏰ Time: {time}\n\n"
        f"Your reservation has been cancelled successfully."
    )

    try:
        client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
            to=customer,
            body=text
        )
        print("✅ Cancellation WhatsApp sent to customer.")
    except Exception as e:
        print("❌ Failed to send cancellation message:", e)

    if OWNER_WHATSAPP:
        try:
            owner_text = f"⚠️ *BOOKING CANCELLED*\n\n{text}"
            client.messages.create(
                from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
                to=f"whatsapp:{OWNER_WHATSAPP}",
                body=owner_text
            )
            print("📨 Owner cancellation copy sent.")
        except:
            print("⚠️ Could not send cancellation copy to owner.")
