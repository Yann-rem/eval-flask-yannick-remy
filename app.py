from datetime import datetime

from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel, Field, ValidationError

app = Flask(__name__)
app.secret_key = "metz-numeric-school"
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


@app.get("/")
def list_events():
    events = Event.query.all()

    return render_template("home.html", events=events)


@app.get("/evenements/ajouter")
def create_event_get():
    return render_template("event-form.html")


@app.post("/evenements/ajouter")
def create_event_post():
    data = request.form

    try:
        validated_data = CreateEventRequest.model_validate(data)
    except ValidationError as e:
        errors = {}

        for error in e.errors():
            field = error["loc"][0]
            message = error["msg"]
            errors[field] = message

        return render_template("event-form.html", errors=errors, old=data)

    new_event = Event()
    new_event.title = validated_data.title
    new_event.type = validated_data.type
    new_event.date = validated_data.date
    new_event.location = validated_data.location
    new_event.description = validated_data.description

    db.session.add(new_event)
    db.session.commit()

    return redirect(url_for("list_events"))
