from flask import Flask, render_template, request, redirect, session, jsonify
import os, uuid
from dotenv import load_dotenv

from brain import get_ai_response
from database import get_all, admin_cancel, search_bookings

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

ADMIN_PIN = os.getenv("ADMIN_PIN")
if not ADMIN_PIN:
    raise Exception("ADMIN_PIN missing in .env — Add ADMIN_PIN=0550")

# Ensure admin login resets when server restarts
SERVER_RUN_ID = str(uuid.uuid4())


# Remove ngrok warning page
@app.after_request
def skip_ngrok_warning(response):
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response


# Admin session protection
@app.before_request
def enforce_session():
    if request.path.startswith("/admin") and not request.path.startswith("/admin/login"):
        if session.get("admin") != SERVER_RUN_ID:
            session.clear()
            return redirect("/admin/login")


# ---------- USER / VOICE ASSISTANT ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.get_json()
    msg = data.get("message", "")

    if "state" not in session:
        session["state"] = {}

    reply, audio, new_state = get_ai_response(msg, session["state"])
    session["state"] = new_state
    return jsonify({"response": reply, "audio": audio})


# ---------- ADMIN LOGIN ----------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("pin") == ADMIN_PIN:
            session["admin"] = SERVER_RUN_ID
            return redirect("/admin")
        return render_template("admin_login.html", error="Incorrect PIN.")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin/login")


# ---------- ADMIN DASHBOARD ----------
@app.route("/admin")
def admin():
    bookings = get_all()
    return render_template("admin.html", bookings=bookings)


@app.route("/admin/cancel/<int:id>")
def admin_cancel_route(id):
    admin_cancel(id)
    return redirect("/admin")


@app.route("/admin/search", methods=["POST"])
def admin_search():
    q = request.form.get("query", "")
    results = search_bookings(q)
    return render_template("admin.html", bookings=results)


# ---------- RUN SERVER ----------
if __name__ == "__main__":
    app.run(debug=True)
    