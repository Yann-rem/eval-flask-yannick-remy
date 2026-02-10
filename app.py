from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel, Field

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.db"

db = SQLAlchemy(app)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f"<Event id={self.id} title={self.title}>"


class CreateEventRequest(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    type: str = Field(min_length=1, max_length=50)
    date: datetime
    location: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)


with app.app_context():
    db.create_all()
