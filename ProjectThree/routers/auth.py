from fastapi import APIRouter, status, HTTPException, Depends, Request ## APIRouter nos permitira acceder desde nuestro archivo main a esta parte de la app
from pydantic import BaseModel, Field, EmailStr # Incorporamos EmailStr para verificar que sea email
from ..models import Users # importamos el modelo de usuario

from passlib.context import CryptContext # Libreria para encriptar y hashear passwords

from ..database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session


############# frontend #################
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
############### /frontend ##############

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer ## importamos Oauth2 para que nos pida los datos de inicio de sesion // usar como dependencia
                                                                             ## Recordar instalar python-multipart // pip install python-multipart
                                                                             ## Oauth2PasswordBearer para pedir que compruebe si el jwt es correcto

from jose import jwt, JWTError ## Recordar instalar "python-jose[cryptography]"
from datetime import datetime, timedelta, timezone  ## Esto trabajara junto con la expiracion del token

## Ahora cambiamos, ya no es mas FastAPI, es APIRouter

router = APIRouter(

    prefix='/auth', # le agrega a las direcciones por predeterminado ese valor antes del valor que le ponemos en la funcion
    tags=['auth']   # como lo identifica dentro de Swagger

) 

## Configuracion para JWT para agregar la firma al mismo

SECRET_KEY = '9-TF6tkFc[CpYwvw6D2xc(jBCdt3Qh*fHF8?;Qv@74+ZrhvFX2A]WT+XFzh7@1Pe&23!17ti%!#xGC5&' # Aca podemos poner lo que queramos
ALGORITHM = 'HS256'


## Dependencias

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto') ## Dependencia para encryptar la pass
oaut2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')



## Pydantic para la Request del user

class CreateUserRequest(BaseModel):

    username : str 
    email : str
    firstname : str 
    lastname : str 
    hashed_password : str 
    role : str
    phone_number : str

## Pydantic para el token

class Token(BaseModel):

    access_token : str
    token_type : str
    


## dependecia de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


############ frontend variables ###################


templates = Jinja2Templates(directory="ProjectThree/templates")

router.mount("/static", StaticFiles(directory="ProjectThree/static"), name="static")

@router.get("/login-page")
def render_login_page(request : Request):
    return templates.TemplateResponse('login.html', {'request':request})


@router.get("/register-page")
def render_register_page(request:Request):
    return templates.TemplateResponse('register.html', {"request":request})



## Funcion Para Iniciar Sesion

def authenticate_user(username : str, password : str, db):
    
    user = db.query(Users).filter(Users.username == username).first() # obtenemos el usuario con el nombre de usuario

    if not user:     # si no existe, devuelve false
        return False
    
    if not bcrypt_context.verify(password, user.hashed_password): ## Verificamos que la pass hasheada sea correcta
        return False # Si no lo es devuelve false
    
    return user # Si todo es correcto, devolvemos el usuario


## Funcion para crear access token con JWT

def create_access_token(username : str, user_id : int, role : str , expires_delta : timedelta): # pasamos por parametro lo que estara codificado en el token

    encode = {'sub' : username, 'id' : user_id, 'role' : role} ## Creamos un diccionario con la data

    expires = datetime.now(timezone.utc) + expires_delta ## Agregamos info con el expires

    encode.update({'exp':expires}) ## Actualizamos el diccionario con la info agregando el expires

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


## Esta funcion la usaremos siempre antes de entrar a un endpoint que necesite seguridad

async def get_current_user(token:Annotated[str, Depends(oaut2_bearer)]): 
    try:
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username : str = payload.get('sub')
        user_id : int = payload.get('id')
        user_role : str = payload.get('role')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid credential')

        return {'username' : username, 'id': user_id, "user_role" : user_role}
    
    except JWTError:

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could Not Validate User')

## Creacion de usuario

@router.post("/", status_code=status.HTTP_201_CREATED) ## Ya no es mas app... ahora es router.
def create_user(db: db_dependency, create_user_request : CreateUserRequest): 

    user_model = Users(                                         ## Atencion como este objeto tiene un password tenemos que pasarles los 
                                                                ## parametros para crearlo uno por uno. Y atencion que pasamos is active
        email = create_user_request.email,                      ## como extra
        username = create_user_request.username,
        firstname = create_user_request.firstname,
        lastname = create_user_request.lastname,
        hashed_password = bcrypt_context.hash(create_user_request.hashed_password), ## Password hasheada con la funcion que creamos arriba
        role = create_user_request.role,
        is_active = True,
        phone_number = create_user_request.phone_number

    )

    ## Guardamos nuestro usuario en la Base de datos

    db.add(user_model)
    db.commit()


# Authenticacion de un usuario con JWT

@router.post("/token", response_model=Token)
def login_for_access_token(form_data : Annotated[OAuth2PasswordRequestForm, Depends()], db : db_dependency): ## pasamos el Oauth2 para que nos pida el formulario, como dependencia

    user = authenticate_user(form_data.username, form_data.password, db) ## llamamos la funcion que escribimos arriba para la auth

    if not user:

        return HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Credentials")
    
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=60)) ## llamamos la funcion que crea el access token

    return {"access_token" : token, 'token_type' : 'Bearer' } # Decimos que queremos enviar el username que vamos a llenar en la formulario de la llamada POST (form_data)


## JWT HEADER -> ALGORITMO DE FIRMA Y TIPO DE TOKEN // SE CODIFICA USANDO BASE64

## JWT PAYLOAD -> CONSISTE EN LOS DATOS REALES DEL USUARIO O INFORMACION ADICIONAL, COMO NOMBRE, EMAIL, ADMIN.
##             -> PUEDEN SER REGISTRO, PRIVADO Y PUBICO, SE CODIFICA UTILIZANDO BASE64

## JWT SIGNATURE -> TERCERA Y ULTIMA PARTE DEL JWT

## CUALES SON LOS USOS PRACTICOS? -->  QUE DOS APLICACIONES DE LA MISMA EMPRESA TENGAN LA MISMA FORMA DE AUTH