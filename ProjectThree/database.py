from sqlalchemy import create_engine  ## importamos el motor creador de sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base ## esto nos permitira crear el objeto bbdd con el cual interactuar



#######

#  IMPORTANTE CUANDO VAMOS A INSTALAR NUESTRA BASE DE DATOS DE PRODUCCION COMO POSTGRESS NECESITAMOS HACER

#  PIP INSTALL PSYCOPG2-BINARY

# TAMBIEN RECORDAR INSTALAR PIP INSTALL ALEMBIC --> # NOS PERMITIRA MIGRAR Y MODIFICAR NUESTRAS TABLAS SIN NECESIDAD DE BORRARLAS

                    # 1) hacer en terminal alembic init "nombre" (por lo general "alembic")
                    # 2) ir a alembic.ini y configurar la base de datos que estemos usando
                    # 3) ir a la env.py importar modelos
                    # 4) en env.py dejar el fileConfig solo sin el if
                    # 5) configurar metadata de los modelos target_metadata = models.Base.metadata

                    # 6) alembic revision -m "create phone number for user column" --> crea una revision para crear los scripts de upgrade y downgrade
                    # 7) alembic upgrade 383a97177db7 --> hacemos el upgrade a la base de datos pasandole el id que nos dio revision
                    # 8) luego recordar agregar a nuestro modelo que fue modificado el campo tal cual lo agrego alembic a la BBDD

                    #9) alembic downgrade -1 --> da de baja el ultimo cambio que hicismos a la bbdd

#######



## SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db' ## Declaramos el directorio donde vivira nuestra base de datos // database para testeo

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:Argentina2018@localhost/TodoAppDatabase' # datos para conectarse a databse de produccion postgre

## Creamos el motor y le pasamos la URL donde se alojara nuestra sql, tambien le pasamos connect_args que 
## gestionara cada hilo de forma independiente

# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread':False}) --> engine para sqlite3

engine = create_engine(SQLALCHEMY_DATABASE_URL)


## Ahora creamos una session local, y cada instancia de la session local tendra una session a la BBDD que se convertira
## en una bbdd en el futuro. y con los argumentos le decimos que queremos el total control de la misma
SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)


## aca decimos que mas adelante queremos se capaces de llamar a nuestra base de datos para controlar la misma
Base = declarative_base()