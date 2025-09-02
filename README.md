AfyaTrack – SDG Health App

AfyaTrack is a web application that promotes health awareness and access to medical guidance, aligned with the SDG Health goal. Users can track symptoms, connect with doctors, and monitor nutrition and fitness.

Features

🩺 Symptom Checker: Log symptoms and get basic health insights.

🏥 Doctor Connect: Send messages to medical professionals for guidance.

🥗 Nutrition & Fitness Guide: Track meals and exercises.

Dashboard: Central hub with easy access to all features.

Technology Stack

Backend: Python, Flask

Frontend: HTML, CSS

Database: SQLite (afyatrack.db)

Deployment: Railway.app 

Installation
Install dependencies:

pip install -r requirements.txt


Run the app:

python app.py


Open http://127.0.0.1:5000 in your browser.

File Structure
afyatrack/
│── app.py
│── requirements.txt
│── afyatrack.db          # SQLite database
│── templates/
│   ├── dashboard.html
│   ├── symptom.html
│   ├── doctor.html
│   └── wellness.html


Integrate real-time doctor chat.
