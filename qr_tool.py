# qr_tool.py
import qrcode
import os

def generate_qr(booking_id, data_text):
    """
    Generate a QR code for the booking and return the file path.
    booking_id : int
    data_text : str (content encoded inside QR)
    """
    folder = "static/qr"
    os.makedirs(folder, exist_ok=True)

    filename = f"booking_{booking_id}.png"
    path = os.path.join(folder, filename)

    qr = qrcode.QRCode(
        version=1,
        box_size=8,
        border=4
    )
    qr.add_data(data_text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path)

    return path  # Example: static/qr/booking_12.png
