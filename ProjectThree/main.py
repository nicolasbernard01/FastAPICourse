from fastapi import FastAPI, Request, status ## Depends nos permite hacer cosas detras de escena antes de ejecutar lo que queremos por ejemplo que se abra la base de datos
from .models import Base
from .database import engine # Importamos el engine de la base de datos Y la session local
from .routers import auth, todos, admin, users ## estas son las otras apps "auth" y "todos", la que estamos trayendo con el router

from fastapi.staticfiles import StaticFiles ## manejamos los staticos // estilos
from fastapi.responses import RedirectResponse

app = FastAPI()

Base.metadata.create_all(bind=engine) ## esto se ejecutara si la bbdd no existe




app.mount("/static", StaticFiles(directory="ProjectThree/static"), name="static")

@app.get("/")  # Define una ruta para el método HTTP GET en la URL raíz "/".
def test_endpoint(request: Request):  
    # Esta función se ejecuta cuando alguien accede a la ruta raíz "/".
    # El parámetro 'request' es de tipo Request y contiene toda la información sobre la solicitud HTTP realizada.

    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)
    # En lugar de devolver una respuesta típica, la función redirige al cliente a la URL "/todos/todo-page".
    # Se utiliza RedirectResponse para indicar que el navegador o cliente debe hacer una nueva solicitud a la URL especificada.
    # Se devuelve un código de estado HTTP 302, que es el código estándar para una redirección temporal.



## Creamos un endopoint que nos permitira saber el estado de nuestra app cuando querramos
@app.get("/healthy")
def health_check():
    return {'status' : 'Healthy'}



app.include_router(auth.router) ## Declaramos los routers que tenemos, en este caso auth
app.include_router(todos.router) ## Llamamos el router de todos
app.include_router(admin.router) ## llamamos el router admin
app.include_router(users.router) ## llamamos el router de users