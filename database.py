import sqlite3
from whatsapp import send_booking_whatsapp, send_cancellation_whatsapp
from qr_tool import generate_qr

DB = "bookings.db"


def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        time TEXT,
        people INTEGER,
        name TEXT,
        phone TEXT,
        status TEXT DEFAULT 'confirmed'
    )
    """)
    con.commit()
    con.close()


init_db()


# Check maximum capacity (Limit = 5 confirmed bookings per time slot)
def check(date, time):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM bookings WHERE date=? AND time=? AND status='confirmed'", (date, time))
    count = cur.fetchone()[0]
    con.close()
    return "full" if count >= 5 else "ok"


def book(date, time, people, name, phone):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO bookings(date, time, people, name, phone, status) VALUES (?, ?, ?, ?, ?, 'confirmed')",
        (date, time, people, name, phone)
    )
    con.commit()
    booking_id = cur.lastrowid
    con.close()

    # Generate QR Code
    qr_file = generate_qr(booking_id, f"{name}\n{date} {time}\nGuests: {people}")

    # Send WhatsApp Confirmation
    send_booking_whatsapp(date, time, people, name, phone, qr_file)

    return f"Booking confirmed for {people} guests on {date} at {time} under {name}.", qr_file


# Used for Admin Panel (show all bookings)
def get_all():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT id, date, time, people, name, phone, status FROM bookings ORDER BY date, time")
    rows = cur.fetchall()
    con.close()
    return rows


# Admin Cancel (mark as cancelled, do not delete)
def admin_cancel(id):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (id,))
    con.commit()
    con.close()


# Admin Search
def search_bookings(query):
    q = f"%{query}%"
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
        SELECT id, date, time, people, name, phone, status
        FROM bookings
        WHERE name LIKE ? OR phone LIKE ?
        ORDER BY date, time
    """, (q, q))
    rows = cur.fetchall()
    con.close()
    return rows


# 3-STEP CANCELLATION → Phone + Date + Time
def cancel_by_phone_date_time(phone, date, time):
    phone = "".join(filter(str.isdigit, phone))[-10:]  # normalize just in case

    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
        SELECT id, name 
        FROM bookings 
        WHERE phone=? AND date=? AND time=? AND status='confirmed'
    """, (phone, date, time))
    row = cur.fetchone()

    if not row:
        con.close()
        return "I could not find a booking matching those details."

    booking_id, name = row

    cur.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,))
    con.commit()
    con.close()

    send_cancellation_whatsapp(date, time, name, phone)

    return "Your booking has been cancelled successfully."
