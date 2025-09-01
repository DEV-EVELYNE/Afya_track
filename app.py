from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "afyatrack_secret"


# --- Database setup ---
def init_db():
    conn = sqlite3.connect("afyatrack.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            heart_rate INTEGER,
            blood_pressure TEXT,
            calories INTEGER,
            steps INTEGER,
            mood INTEGER,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()


# --- Routes ---
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/auth")
def auth():
    return render_template("auth.html")


@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("afyatrack.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "Username already exists!"
    conn.close()

    return redirect(url_for("auth"))


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("afyatrack.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session["user_id"] = user[0]
        session["username"] = user[1]
        return redirect(url_for("dashboard"))
    else:
        return "Invalid login credentials!"


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth"))

    conn = sqlite3.connect("afyatrack.db")
    c = conn.cursor()
    c.execute("SELECT * FROM health WHERE user_id=? ORDER BY date DESC LIMIT 1", (session["user_id"],))
    health = c.fetchone()
    conn.close()

    # Default values
    percentages = {
        "heart_rate": 0,
        "calories": 0,
        "steps": 0,
        "mood": 0
    }

    if health:
        hr, bp, cal, steps, mood = health[2], health[3], health[4], health[5], health[6]
        percentages = {
            "heart_rate": round((hr / 120) * 100) if hr else 0,
            "calories": round((cal / 2000) * 100) if cal else 0,
            "steps": round((steps / 10000) * 100) if steps else 0,
            "mood": round((mood / 10) * 100) if mood else 0
        }
    else:
        hr, bp, cal, steps, mood = None, None, 0, 0, 0

    return render_template(
        "dashboard.html",
        username=session["username"],
        health=health,
        percentages=percentages
    )


@app.route("/add_health", methods=["POST"])
def add_health():
    if "user_id" not in session:
        return redirect(url_for("auth"))

    heart_rate = int(request.form["heart_rate"])
    blood_pressure = request.form["blood_pressure"]
    calories = int(request.form["calories"])
    steps = int(request.form["steps"])
    mood = int(request.form["mood"])

    conn = sqlite3.connect("afyatrack.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO health (user_id, heart_rate, blood_pressure, calories, steps, mood) VALUES (?, ?, ?, ?, ?, ?)",
        (session["user_id"], heart_rate, blood_pressure, calories, steps, mood)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))

# --- Symptom Checker ---
@app.route("/symptom_checker", methods=["GET", "POST"])
def symptom_checker():
    # Ensure the user is logged in
    if "user_id" not in session:
        return redirect(url_for("auth"))

    result = None
    if request.method == "POST":
        symptoms = request.form.get("symptoms", "").lower()

        # Simple rule-based response
        if "fever" in symptoms and "cough" in symptoms:
            result = "You may have flu or COVID-19. Please consult a doctor."
        elif "headache" in symptoms and "nausea" in symptoms:
            result = "Possible migraine. Stay hydrated and rest."
        elif "stomach" in symptoms or "diarrhea" in symptoms:
            result = "Possible food poisoning. Monitor and seek care if severe."
        else:
            result = "Symptoms are not recognized clearly. Please consult a healthcare professional."

    return render_template("symptom_checker.html", result=result)

# --- Doctor Connect ---
@app.route("/doctor_connect", methods=["GET", "POST"])
def doctor_connect():
    if "user_id" not in session:
        return redirect(url_for("auth"))

    message = None
    if request.method == "POST":
        name = request.form.get("name")
        contact = request.form.get("contact")
        issue = request.form.get("issue")

        # For now, just simulate storing or sending the request
        # Later, you can save it to the database
        print(f"Doctor request submitted: {name}, {contact}, {issue}")

        message = "Your request has been submitted. A doctor will contact you soon!"

    return render_template("doctor_connect.html", message=message)

# --- Wellness Page ---
@app.route("/wellness", methods=["GET", "POST"])
def wellness():
    if "user_id" not in session:
        return redirect(url_for("auth"))

    message = None

    # Example tips
    tips = [
        "Drink at least 8 cups of water today!",
        "Include more greens in your meals.",
        "Take a short walk after lunch.",
        "Practice deep breathing for 5 minutes."
    ]
    import random
    tip = random.choice(tips)

    # Connect to DB
    conn = sqlite3.connect("afyatrack.db")
    c = conn.cursor()

    # Create wellness table if not exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS wellness_foods (
            user_id INTEGER,
            food TEXT
        )
    """)

    # Add food log
    if request.method == "POST":
        food = request.form.get("food")
        c.execute("INSERT INTO wellness_foods (user_id, food) VALUES (?, ?)", (session["user_id"], food))
        conn.commit()
        message = "Food added successfully!"

    # Fetch foods
    c.execute("SELECT food FROM wellness_foods WHERE user_id=?", (session["user_id"],))
    foods = c.fetchall()
    conn.close()

    return render_template("wellness.html", tip=tip, foods=foods, message=message)






@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
