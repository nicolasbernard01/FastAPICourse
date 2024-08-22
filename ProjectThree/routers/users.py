from fastapi import APIRouter, HTTPException, status, Path, Depends ## Depends nos permite hacer cosas detras de escena antes de ejecutar lo que queremos por ejemplo que se abra la base de datos
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from ..models import Users # Importamos los modelos
from ..database import SessionLocal # Importamos el engine de la base de datos Y la session local
from passlib.context import CryptContext #

from .auth import get_current_user # importamos la funcion para obtener si el current user esta actualmente authenticado

router = APIRouter(

    prefix = '/users', # le agrega a las direcciones por predeterminado ese valor antes del valor que le ponemos en la funcion
    tags=['users']     # como lo identifica dentro de Swagger


)

## dependecia de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


## pydantics

class NewPasswordRequest(BaseModel):

    old_password : str = Field(min_length=5)
    new_password : str = Field(min_length=5)

class UpdatePhoneNumber(BaseModel):

    phone_number : str = Field( examples=['123456789'] )


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto') ## Dependencia para encryptar la pass


@router.get("/user_data", status_code=status.HTTP_200_OK)
def call_user_data(user : user_dependency, db : db_dependency):

    user = db.query(Users).filter(Users.id == user.get('id')).first()

    if user is None:

        raise HTTPException(status_code=404, detail='User Not Found')
    
    return user


@router.put("/change_password", status_code=status.HTTP_200_OK)
def change_password(user : user_dependency, db : db_dependency, NewPasswordRequest : NewPasswordRequest):

    if user is None:

        raise HTTPException(status_code=404, detail="User dosn't exist")
    
    user = db.query(Users).filter(Users.id == user.get("id")).first()
    
    if not bcrypt_context.verify(NewPasswordRequest.old_password, user.hashed_password): ## usamos el contexto para verificar si el usuario pasa
                                                                                         ## la pass correcta
        raise HTTPException(status_code=401, detail="Error On password Change")
    
    user.hashed_password = bcrypt_context.hash(NewPasswordRequest.new_password) # si es correcta le decimos que la pass ahora es 
                                                                                # lo que llega por el pydantic hasheado por el contexto bcrypt

    db.add(user)

    db.commit()


@router.put("/update_phone", status_code=status.HTTP_204_NO_CONTENT)
def update_phone(user : user_dependency, db : db_dependency, update_phone_number_request : UpdatePhoneNumber):

    user = db.query(Users).filter(Users.id == user.get('id')).first()

    if user is None:

        raise HTTPException(status_code=404, detail="User Not Authenticated")
    
    if update_phone_number_request.phone_number is not None:

        user.phone_number = update_phone_number_request.phone_number

        db.add(user)

        db.commit()

