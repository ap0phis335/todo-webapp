import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, abort, flash
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'todo.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------- Models ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    todos = db.relationship("Todo", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw): self.password_hash = generate_password_hash(raw)
    def check_password(self, raw): return check_password_hash(self.password_hash, raw)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.String(10), default="medium")  # low | medium | high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
        }


# ---------- Auth helpers ----------
def login_required(f):
    @wraps(f)
    def wrapped(*a, **kw):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "unauthorized"}), 401
            return redirect(url_for("login"))
        return f(*a, **kw)
    return wrapped


def current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None


# ---------- Pages ----------
@app.route("/")
def landing():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("login.html", email=email), 401
        session["user_id"] = user.id
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Please fill all fields. Password must be at least 6 characters.", "error")
            return render_template("signup.html", name=name, email=email), 400
        if User.query.filter_by(email=email).first():
            flash("That email is already registered.", "error")
            return render_template("signup.html", name=name, email=email), 400
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        return redirect(url_for("dashboard"))
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user())


# ---------- API ----------
@app.get("/api/todos")
@login_required
def api_list():
    items = Todo.query.filter_by(user_id=session["user_id"]).order_by(Todo.completed, Todo.created_at.desc()).all()
    return jsonify([t.to_dict() for t in items])


@app.post("/api/todos")
@login_required
def api_create():
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    priority = data.get("priority", "medium")
    if not title:
        return jsonify({"error": "title required"}), 400
    if priority not in ("low", "medium", "high"):
        priority = "medium"
    t = Todo(title=title, priority=priority, user_id=session["user_id"])
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201


@app.patch("/api/todos/<int:todo_id>")
@login_required
def api_update(todo_id):
    t = Todo.query.get_or_404(todo_id)
    if t.user_id != session["user_id"]:
        abort(403)
    data = request.get_json() or {}
    if "title" in data:
        title = (data["title"] or "").strip()
        if title:
            t.title = title
    if "completed" in data:
        t.completed = bool(data["completed"])
    if "priority" in data and data["priority"] in ("low", "medium", "high"):
        t.priority = data["priority"]
    db.session.commit()
    return jsonify(t.to_dict())


@app.delete("/api/todos/<int:todo_id>")
@login_required
def api_delete(todo_id):
    t = Todo.query.get_or_404(todo_id)
    if t.user_id != session["user_id"]:
        abort(403)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"ok": True})


# ---------- Bootstrap ----------
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
