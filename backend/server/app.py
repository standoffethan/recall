import os
import random
from google import genai
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#Get Gemini API client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])



#DATABASE TABLE CLASSES
class User(db.Model):
    __tablename__ = "users"

    uuid = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(128))
    img = db.Column(db.String(128))

    # Lets you access user.tasks to get all tasks belonging to this user
    tasks = db.relationship("Task", backref="user", lazy=True)

    def to_dict(self):
        return {"uuid": self.uuid, "img": self.img}


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(50), db.ForeignKey("users.uuid"))
    accuracy = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True))
    length = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "accuracy": self.accuracy,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "length": self.length,
        }
    
class Passage(db.Model):
    __tablename__ = "passages"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    length = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String(10), default="en")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "text": self.text,
            "length": self.length,
        }



@app.route("/book")
def get_passage():
    response = client.models.generate_content(

    )
    
    length = request.args.get("length", type=int, default=100)

    candidates = (
        Passage.query
        .order_by(db.func.abs(Passage.length - length))
        .limit(20)
        .all()
    )

    if not candidates:
        return jsonify({"error": "no passages available"}), 404

    passage = random.choice(candidates)
    return jsonify(passage.to_dict())


