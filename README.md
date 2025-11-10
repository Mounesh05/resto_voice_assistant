\# AM Restaurant - Voice Based Table Reservation Assistant



This project is an \*\*AI-powered restaurant reservation system\*\* where customers can interact using \*\*voice\*\* to book or cancel table reservations. The system uses \*\*speech recognition\*\*, \*\*text-to-speech\*\*, \*\*AI conversation logic\*\*, and \*\*WhatsApp integration\*\* to send booking confirmations along with a \*\*QR code\*\* for verification.



---



\## ✅ Key Features



| Feature | Description |

|--------|-------------|

| Voice Based Interaction | Customer speaks, system understands, replies with natural voice. |

| Smart Conversation Flow | AI guides user through booking: date → time → guests → phone. |

| WhatsApp Confirmation | Booking details + QR sent automatically via WhatsApp. |

| QR Code at Entry | Staff can verify booking using QR scan. |

| Admin Panel | View, search, and cancel bookings (status tracking). |

| Local Database (SQLite) | Stores booking records securely. |



---



\## 🏗 System Architecture



User Voice → Speech Recognition → AI Logic (Python) → Database (SQLite)

↓

WhatsApp Notification + QR



---



\## 🛠 Technologies Used



\### Backend

\- Python, Flask

\- SQLite3 Database

\- Edge-TTS (Text-to-Speech)

\- Ollama / LLaMA model (local AI)



\### Frontend

\- HTML, CSS, JavaScript (Vanilla)

\- Web Speech API



\### Messaging Integration

\- Twilio WhatsApp API



---



\## 📂 Project Structure



resto\_voice\_assistant

│ app.py

│ brain.py

│ database.py

│ whatsapp.py

│ qr\_tool.py

│ config.py

│ requirements.txt

│

├── templates/

│ ├── index.html

│ ├── admin.html

│ └── admin\_login.html

│

├── static/

│ ├── css/style.css

│ └── js/app.js

│

└── .gitignore


---



\## 🔑 Environment Variables (Create `.env` file)



TWILIO\_SID=xxxxxxxxxxxxxxxxxxxx

TWILIO\_AUTH\_TOKEN=xxxxxxxxxxxx

TWILIO\_WHATSAPP\_NUMBER=xxxxxxxxxxxx

OWNER\_WHATSAPP=+91xxxxxxxxxx

NGROK\_URL=xxxxxxxxxxxxxxxx

FLASK\_SECRET\_KEY=supersecretkey

ADMIN\_PIN=xxxx


---



\## ▶ How to Run



```bash

pip install -r requirements.txt

python app.py


Start ngrok:



ngrok http 5000





Open in browser:



http://127.0.0.1:5000/


