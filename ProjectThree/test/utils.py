# En este archivo colocamos todo lo que vamos a reutilizar para nuestras pruebas

import pytest
from fastapi import status
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient  # Importa el TestClient para realizar pruebas
from ..database import Base  # Importa la base de datos base desde tu módulo
from ..main import app  # Importa la instancia de la aplicación FastAPI
from ..models import Todos, Users
from ..routers.auth import bcrypt_context


# Define la URL de la base de datos de pruebas usando SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

# Configura el motor de la base de datos de prueba con SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,  # Usa StaticPool para evitar problemas con hilos en SQLite
)

# Crea una sesión local para las pruebas
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea todas las tablas definidas en el modelo
Base.metadata.create_all(bind=engine)

# Función para sobrescribir la dependencia de la base de datos y utilizar la de pruebas
def override_get_db():
    db = TestingSessionLocal()  # Crea una sesión de base de datos para pruebas
    try:
        yield db  # Devuelve la sesión para usarla en la prueba
    finally:
        db.close()  # Cierra la sesión después de la prueba

# Crea una instancia de TestClient para realizar pruebas en la aplicación
client = TestClient(app)

# Función para sobrescribir la dependencia del usuario actual y utilizar un usuario simulado


def override_get_current_user():
    
    return {
        'username': 'nicotesting',
        'id': 1,
        'role': 'admin',
        'firstname': 'Nicolas',
        'lastname': 'Bernard',
        'email': 'nicolasemanuelbernard@gmail.com',
        'phone_number': '1111'
    }  # Devuelve un usuario simulado para pruebas



# Fixture para crear datos de prueba
@pytest.fixture
def test_todo():
    db = TestingSessionLocal()  # Crea una sesión de base de datos para pruebas
    todo = Todos(
        title='aprender fastAPI',
        description='siempre todos los dias',
        priority=5,
        complete=False,
        owner=1  # Asegúrate de que este campo coincide con el esquema de tu modelo
    )
    db.add(todo)  # Añade el objeto todo a la sesión
    db.commit()  # Confirma la transacción para guardar el objeto en la base de datos
    db.refresh(todo)  # Refresca la instancia de todo para obtener el ID asignado
    yield todo  # Devuelve el objeto todo para usarlo en la prueba
    db.close()  # Cierra la sesión después de la prueba
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM todos;'))  # Borra todos los registros de la tabla todos
        connection.commit()  # Confirma la transacción de borrado



@pytest.fixture
def test_user():
    # Crea una instancia de la clase Users con datos específicos para el test
    user = Users(
        username='nicotesting',
        firstname='Nicolas',
        lastname='Bernard',
        email='nicolasemanuetest@gmail.com',
        phone_number='1111',
        role='admin',
        hashed_password=bcrypt_context.hash('testpassword')  # Hashing de la contraseña para almacenamiento seguro
    )

    # Crea una sesión de la base de datos de pruebas
    db = TestingSessionLocal()
    # Añade el nuevo usuario a la sesión de la base de datos
    db.add(user)
    # Guarda los cambios en la base de datos
    db.commit()

    # El yield permite que el fixture proporcione el usuario creado a las pruebas que lo utilicen
    yield user

    # Limpia la tabla de usuarios después de que la prueba se haya ejecutado
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users;'))
        connection.commit()
        connection.close()