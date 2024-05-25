import datetime
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv

# Настройка приложения и подключения к базе
app = Flask(__name__)
load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)
ma = Marshmallow(app)


# Создание модели для задач
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


# Создание схемы сериализации с использованием Marshmallow
class TaskSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "description", "created_at", "updated_at")


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


# Создание задачи
@app.route("/tasks", methods=["POST"])
def create_task():

    if not request.json or "title" not in request.json:
        os.abort(400, "Missing title in request data")

    title = request.json["title"]
    description = request.json.get("description", "")

    new_task = Task(title=title, description=description)
    db.session.add(new_task)
    db.session.commit()

    return task_schema.jsonify(new_task)


# Получение списка задач
@app.route("/tasks", methods=["GET"])
def get_tasks():
    all_tasks = Task.query.all()
    result = tasks_schema.dump(all_tasks)

    return jsonify(result)


# Получение информации о задаче
@app.route("/tasks/<int:id>", methods=["GET"])
def get_task(id):
    task = Task.query.get_or_404(id)

    return task_schema.jsonify(task)


# Обновление задачи
@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    task = Task.query.get_or_404(id)

    if not request.json:
        os.abort(400, "No data provided for update")

    title = request.json.get("title", task.title)
    description = request.json.get("description", task.description)

    task.title = title
    task.description = description

    db.session.commit()

    return task_schema.jsonify(task)


# Удаление задачи
@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    task = Task.query.get_or_404(id)

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"})


if __name__ == "__main__":
    app.run(debug=True)
