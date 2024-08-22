## aca vamos a encontrar que tipo de base de datos y datos vamos a crear dentro de nuestra bbdd
##un MODELO de BBDD va a ser el registro real que esta dentro de una tabla de base de datos

from .database import Base ## importamos la base de datos que creamos o sea crearemos nuestros modelos para esta base de datos

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey ## llamamos de sqlalchemy lo que vamos a utilizar para crear las columnas
                                                                    ## Importamos Foreingkey para enlazar tablas



class Users(Base): ## Creamos el objeto que va a vivir en la base de datos

    __tablename__ = "users"  # Nombre de la tabla

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True) # username va a ser unico
    email = Column(String, unique=True) # email va a ser unico
    firstname = Column(String)
    lastname = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String, nullable=True)



class Todos(Base): # creamos una objeto todos que herede de la bbdd Base
    
    __tablename__ = 'todos' # la tabla va a tener este nombre

    id = Column(Integer, primary_key=True, index=True) # es la clave primaria de identificacion y tambien lo idexamos
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner = Column(Integer, ForeignKey("users.id"))





