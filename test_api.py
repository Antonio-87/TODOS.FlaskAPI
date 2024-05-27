import os
import tempfile
import pytest

from flask_api import TaskSchema, app, db, Task


# Фикстура для создания клиента приложения
@pytest.fixture
def client():
    # Создание временной базы данных для тестов
    db_fd, db_path = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql:///" + db_path

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    # Удаление временной базы данных после завершения тестов
    os.close(db_fd)
    os.unlink(db_path)


# Тест на создание задачи
def test_create_task(client):
    with app.app_context():
        db.session.query(Task).delete()
        response = client.post(
            "/tasks", json={"title": "Task 1", "description": "Description for Task 1"}
        )
        assert response.status_code == 200
        assert response.json["title"] == "Task 1"
        assert response.json["description"] == "Description for Task 1"


# Тест на получение списка задач
def test_get_tasks(client):
    with app.app_context():
        response = client.get("/tasks")
        assert response.status_code == 200
        assert len(response.json) == 1


# Тест на обновление задачи
def test_update_task(client):
    with app.app_context():
        response = client.post(
            "/tasks", json={"title": "Task 2", "description": "Description for Task 2"}
        )
        task_id = response.json["id"]

        response = client.put(
            f"/tasks/{task_id}",
            json={"title": "Updated Task 2", "description": "Updated description"},
        )
        assert response.status_code == 200
        assert response.json["title"] == "Updated Task 2"
        assert response.json["description"] == "Updated description"


# Тест на удаление задачи
def test_delete_task(client):
    with app.app_context():
        response = client.post(
            "/tasks", json={"title": "Task 3", "description": "Description for Task 3"}
        )
        task_id = response.json["id"]

        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 200

        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 404


# Тест модели задачи
def test_task_model():
    with app.app_context():
        task = Task(title="Test Task", description="Description for Test Task")
        db.session.add(task)
        db.session.commit()

        assert task.id is not None
        assert task.title == "Test Task"
        assert task.description == "Description for Test Task"


# Тест сериализации задачи
def test_task_schema():
    with app.app_context():
        task = Task(title="Test Task", description="Description for Test Task")
        db.session.add(task)
        db.session.commit()

        task_schema = TaskSchema().dump(task)

        assert task_schema["id"] == task.id
        assert task_schema["title"] == task.title
        assert task_schema["description"] == task.description
