# todo-webapp
A professional looking todo webapp using flask for backend and html , css , js for frontend
# Flow — A Modern Flask Todo App

A polished, resume-ready full-stack todo app built with **Flask + SQLite + vanilla HTML/CSS/JS**.
Glassmorphism UI, smooth animations, secure auth, and a clean REST API.

## Features
- 🎨 Modern landing page with animated gradient hero
- 🔐 Secure auth (sign up / log in / log out) with hashed passwords
- ✅ Full CRUD todos with priorities (low / medium / high)
- ⚡ Smooth micro-animations (fade, slide, scale, ripple)
- 📱 Fully responsive
- 🧱 Clean REST API (`/api/todos`)

## Tech
Flask, Flask-SQLAlchemy, Werkzeug, SQLite, vanilla JS (no framework).

## Run locally
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Project structure
```
app.py
requirements.txt
templates/
  base.html  landing.html  login.html  signup.html  dashboard.html
static/
  css/styles.css
  js/dashboard.js
```
