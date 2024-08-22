from ..routers.todos import get_db, get_current_user  # Importa las dependencias get_db y get_current_user
from fastapi import status  # Importa el módulo status para manejar los códigos de estado HTTP
from ..models import Todos  # Importa el modelo Todos
from .utils import * # importamos todo desde utils para que este archivo funcione

# Sobrescribe las dependencias en la aplicación
app.dependency_overrides[get_db] = override_get_db  # Sobrescribe la dependencia get_db en la aplicación
app.dependency_overrides[get_current_user] = override_get_current_user  # Sobrescribe la dependencia get_current_user en la aplicación


# Prueba para leer todos los todos
def test_read_all_authenticated(test_todo):
    response = client.get("/todos/")  # Realiza una solicitud GET a la ruta /todos/
    assert response.status_code == status.HTTP_200_OK  # Verifica que el código de estado de la respuesta sea 200 OK
    assert response.json() == [{
        'complete': False,
        'title': 'aprender fastAPI',
        'description': 'siempre todos los dias',
        'priority': 5,
        'id': 1,
        'owner': 1  # Asegúrate de que este campo coincida con el esquema de tu modelo
    }]

# Prueba para leer un todo específico por ID
def test_read_one_authenticated(test_todo):
    response = client.get("/todos/1")  # Realiza una solicitud GET a la ruta /todos/{id}
    assert response.status_code == status.HTTP_200_OK  # Verifica que el código de estado de la respuesta sea 200 OK
    assert response.json() == {
        'complete': False,
        'title': 'aprender fastAPI',
        'description': 'siempre todos los dias',
        'priority': 5,
        'id': 1,
        'owner': 1  # Asegúrate de que este campo coincida con el esquema de tu modelo
    }


def test_read_one_authenticated_not_found(test_todo):
    response = client.get('/todos/2')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail' : 'Item Not Found'}


# test para probar el funcionamiento de creacion // recordar que lo que pasamos debe coincidir con el pydantic

def test_create_todo(test_todo):

    # creamos los datos del nuevo todo

    request_data = {
        'title' : 'new todo',
        'description' : 'new todo description',
        'priority' : 5,
        'complete' : False
    }

    response = client.post("todos/todo", json=request_data)
    assert response.status_code == 201

    # Creamos una nueva sesion en la base de datos de prueba para saber si lo que se creo aqui coincide
    # recordar que devuelve los mismos test pasados porque cuenta solo la funcion

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


## Test para probar update todo

def test_update_todo(test_todo):

    request_data = {
        'title' : 'updated todo',
        'description' : 'new updated description',
        'priority' : 4,
        'complete' : False
    }

    response = client.put("/todos/update_todo/1", json=request_data)
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    
    ## notar que aca le pasamos el valor de la string directamente

    assert model.title == 'updated todo'
    assert model.description == 'new updated description'
    assert model.priority == 4
    assert model.complete == False


# Test para cuando no encontramos la task == error 404

def test_update_todo_not_found(test_todo):
    
    # Datos del nuevo todo

    request_data = {
        
        'title' : 'updated todo',
        'description' : 'new updated description',
        'priority' : 4,
        'complete' : False
    }

    # llamamos como cliente la API en put

    response = client.put("/todos/update_todo/3", json=request_data)
    assert response.status_code == 404

# test para probar eliminacion de todo

def test_delete_todo(test_todo):

    response = client.delete("/todos/delete_todo/1")
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model is None  # el modelo deberia ser none porque fue borrado


def test_delete_todo_not_found(test_todo):

    response = client.delete("/todos/delete_todo/3")
    assert response.status_code == 404

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 3).first()

    assert model is None  # el modelo deberia ser none porque nunca existio

    
