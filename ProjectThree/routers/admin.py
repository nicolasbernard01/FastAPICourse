from fastapi import APIRouter, HTTPException, status, Path, Depends ## Depends nos permite hacer cosas detras de escena antes de ejecutar lo que queremos por ejemplo que se abra la base de datos
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from ..models import Todos, Users # Importamos los modelos
from ..database import SessionLocal # Importamos el engine de la base de datos Y la session local

from .auth import get_current_user # importamos la funcion para obtener si el current user esta actualmente authenticado

router = APIRouter(

    prefix = '/admin', # le agrega a las direcciones por predeterminado ese valor antes del valor que le ponemos en la funcion
    tags=['admin']     # como lo identifica dentro de Swagger


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


# TODOS

@router.get("/todo", status_code=status.HTTP_200_OK)
def read_all(user: user_dependency , db : db_dependency):

    if user is None or user.get('role') != 'admin': ## preguntamos su el user rol del usuario (cifrado en la funcion get_current_user
                                                         ## es admin), atencion estamos trayendo el usuario desde la funcion de la dependencia
                                                         ## por eso user_role, porque asi lo devuelve esa funcion

        raise HTTPException(status_code=404, detail='No Permissions Allowed')
    
    return db.query(Todos).all()


@router.delete("/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_todo(user : user_dependency, db : db_dependency, todo_id : int = Path(gt=0)):

    if user is None or user.get('role') != 'admin':

        raise HTTPException(status_code=404, detail='No Permissions Allowed')
    
    todo_object = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_object is None:

        raise HTTPException(status_code=404, detail="Item Not Found")

    db.delete(todo_object)

    db.commit()


# USERS


@router.get('/read_all_users', status_code=status.HTTP_200_OK)
def read_all_users(user : user_dependency, db: db_dependency):

    if user.get('role') == "admin":

        users = db.query(Users).all()

        return users
    
    raise HTTPException(status_code=404, detail="No permissions allowed")