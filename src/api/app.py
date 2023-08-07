from flask import Flask, jsonify
import os

app = Flask(__name__)

host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

db_uri = f"postgresql://{user}:{password}@{host}:{port}/{database}"
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
