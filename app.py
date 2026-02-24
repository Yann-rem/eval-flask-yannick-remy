from datetime import datetime

from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel, Field, field_validator, ValidationError
from pydantic_core import PydanticCustomError

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
    title: str
    type: str
    date: datetime
    location: str
    description: str

    # https://docs.pydantic.dev/latest/concepts/validators/#raising-validation-errors
    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if not value or not value.strip():
            raise PydanticCustomError("title_required", "Le titre est obligatoire")
        if len(value.strip()) < 2:
            raise PydanticCustomError(
                "title_min_length", "Le titre doit contenir au minimum 2 caractères"
            )
        if len(value) > 50:
            raise PydanticCustomError(
                "title_max_length", "Le titre doit contenir au maximum 50 caractères"
            )
        return value.strip()

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        if not value or not value.strip():
            raise PydanticCustomError("type_required", "Le type est obligatoire")
        if len(value.strip()) < 2:
            raise PydanticCustomError(
                "type_min_length", "Le type doit contenir au minimum 2 caractères"
            )
        if len(value) > 50:
            raise PydanticCustomError(
                "type_max_length", "Le type doit contenir au maximum 50 caractères"
            )
        return value.strip()

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, value):
        if not value:
            raise PydanticCustomError("date_required", "La date est obligatoire")
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                raise PydanticCustomError(
                    "date_invalid", "Le format de la date est invalide"
                )
        if value < datetime.now():
            raise PydanticCustomError(
                "date_past", "la date doit être postérieure à la date du jour"
            )
        return value

    @field_validator("location")
    @classmethod
    def validate_location(cls, value):
        if not value or not value.strip():
            raise PydanticCustomError("location_required", "Le lieu est obligatoire")
        if len(value.strip()) < 2:
            raise PydanticCustomError(
                "location_min_length", "Le lieu doit contenir au minimum 2 caractères"
            )
        if len(value) > 100:
            raise PydanticCustomError(
                "location_max_length", "Le lieu doit contenir au maximum 100 caractères"
            )
        return value.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        if not value or not value.strip():
            raise PydanticCustomError(
                "description_required", "La description est obligatoire"
            )
        if len(value.strip()) < 2:
            raise PydanticCustomError(
                "description_min_length",
                "La description doit contenir au minimum 2 caractères",
            )
        return value.strip()


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
