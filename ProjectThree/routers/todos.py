from fastapi import APIRouter, HTTPException, status, Path, Depends, Request ## Depends nos permite hacer cosas detras de escena antes de ejecutar lo que queremos por ejemplo que se abra la base de datos
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from ..models import Todos # Importamos los modelos
from ..database import SessionLocal # Importamos el engine de la base de datos Y la session local
from .auth import get_current_user # importamos la funcion para obtener si el current user esta actualmente authenticado


from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



router = APIRouter(

    prefix = '/todos', # le agrega a las direcciones por predeterminado ese valor antes del valor que le ponemos en la funcion
    tags=['todos']     # como lo identifica dentro de Swagger


)

## dependecia de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

## pydantic request para crear un todo

class TodoRequest(BaseModel):
    title : str  = Field(min_length=3)
    description : str = Field(min_length=3, max_length=100)
    priority : int = Field(gt=0, lt=6 )
    complete : bool


### pages frontend ###


templates = Jinja2Templates("ProjectThree/templates")
router.mount("/static", StaticFiles(directory="ProjectThree/static"), name="static")

def redirect_to_login():
    # Función que redirige a la página de inicio de sesión.
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    # Crea una redirección HTTP 302 a "/auth/login-page".
    redirect_response.delete_cookie(key="access_token")
    # Elimina la cookie 'access_token'.
    return redirect_response
    # Retorna la respuesta de redirección.


@router.get("/todo-page")
# Define la ruta GET para "/todo-page".
async def render_todo_page(request: Request, db: db_dependency):
    # Función asincrónica para renderizar la página de tareas.
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        # Obtiene el usuario actual a partir del token en las cookies.
        
        if user is None:
            return redirect_to_login()
        # Redirige al login si no hay usuario.

        todos = db.query(Todos).filter(Todos.owner == user.get('id')).all()
        # Obtiene las tareas del usuario desde la base de datos.

        return templates.TemplateResponse("todo.html", {'request': request, "todos": todos, "user": user})
        # Renderiza la plantilla HTML con las tareas y la información del usuario.

    except:
        return redirect_to_login()
        # Redirige al login en caso de error.


@router.get('/add-todo-page')
async def render_todo_page(request:Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {'request':request, 'user':user})
    
    except:
        redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            redirect_to_login()
        
        todo = db.query(Todos).filter(Todos.id == todo_id).first()
        return templates.TemplateResponse("edit-todo.html", {"request":request, "todo":todo, "user":user})
    
    except:
        redirect_to_login()

### endpoints ###

@router.get("/")
def read_all(user : user_dependency, db : db_dependency):
    return db.query(Todos).filter(Todos.owner == user.get('id')).all() ## Devolvemos todo lo relacionado al cliente filtrando por la dependencia



## get todo by ID

@router.get("/{id}", status_code=status.HTTP_200_OK) ## pasamos el id por query y con status decimos que marque 200 si fue correcto
def todo_by_id(user : user_dependency, db : db_dependency, id : int = Path(gt=0)): ## hacemos la dependencia a la base de datos y decimos que ID que pasamos debe ser > 0
    
    todo_model = db.query(Todos).filter(Todos.id == id).filter(Todos.owner == user.get('id')).first() ## Obtenemos el objeto desde la base de datos  
                                                                                                      ## filtrado por la dependencia de current user
                                                                                                      ## filtramos dos
    if todo_model:
        return todo_model
    raise HTTPException(404, "Item Not Found")


## Create someting on database / Para crear algo siempre tenemos que tener antes el pydantic request

@router.post("/todo", status_code=status.HTTP_201_CREATED)
def create_todo(user : user_dependency ,db : db_dependency, todo_request : TodoRequest):

    if user is None:
        
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    todo_model = Todos(**todo_request.model_dump(), owner=user.get("id")) ## Creamos el objeto todo que va a tomar los datos del pydantic TodoRequest y lo volcamos
                                                                          ## al modelo creado y le decimos que le pertenece al usuario del id que le pasamos
    db.add(todo_model) ## Lo agregamos a la Base de datos

    db.commit() 

    return {"detail" : "Todo Created"}


## PUT para editar algo

@router.put("/update_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT) ## pasamos lo que devolveria si todo esta bien
def todo_update(user : user_dependency, db: db_dependency, todo_request : TodoRequest, todo_id : int = Path(gt=0)): ## llamamos la bbdd, la query que pasamos, y el formulario (pydantic) del objeto
    
    # Buscamos en la bbdd el objeto

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner == user.get('id')).first()

    # Si no existe lanzamos una httpException

    if todo_model is None:
        raise HTTPException(404, "Item Not Found")
    
    # pero si existe decimos que el modelo que estamos editando va a tomar los valores que llegan por el pydantic

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    ## y lo volcamos a nuestra base de datos  
    db.add(todo_model)
    db.commit()


## Now Delete a Objet from a database

@router.delete("/delete_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_one_todo(user: user_dependency, db: db_dependency, todo_id : int = Path(gt=0)):

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner == user.get('id')).first() # extraemos el todo que queremos eliminar
                                                                                                           # y junto la dependencia decimos que sea del usuario login

    if todo_model is None:
        raise HTTPException(404, "Item Not Found")
    
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner == user.get('id')).delete()
    
    db.commit()
