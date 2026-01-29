# GitHub Webhook Monitor 🔔📊

A web-based application that listens to GitHub webhook events, stores them in MongoDB, and displays real-time repository activity through a clean and responsive UI.

The application tracks repository actions such as **pushes**, **pull requests**, and **merges**, providing visibility into GitHub activity in near real time.

---

## 🚀 Features

* 🔔 Receives GitHub webhook events in real time
* 📦 Stores webhook events securely in MongoDB
* 🔄 Auto-refreshing UI (polls every 15 seconds)
* 🌿 Tracks branch activity (Push, Pull Request, Merge)
* ☁️ Cloud-ready deployment using Render
* 💻 Runs seamlessly on both localhost and production

---

## 🛠 Tech Stack

### Backend
* Python (Flask)
* Flask-CORS
* Gunicorn (production server)

### Database
* MongoDB Atlas

### Frontend
* HTML
* CSS
* JavaScript

### DevOps / Cloud
* GitHub Webhooks
* Render
* Environment-based configuration

---

## 📁 Project Structure

```bash
webhook-repo/
│
├── app.py
├── requirements.txt
├── .gitignore
├── .env.example
├── templates/
│   └── index.html
└── README.md
## ⚙️ Setup & Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Aaru607/webhook-repo.git
cd webhook-repo
