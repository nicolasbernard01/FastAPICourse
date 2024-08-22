from .utils import *
from ..routers.auth import get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from jose import jwt
from datetime import datetime, timedelta, timezone  ## Esto trabajara junto con la expiracion del token
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db  # Sobrescribe la dependencia get_db en la aplicación

def test_authenticate_user(test_user):
    
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, 'testpassword', db)
    assert authenticated_user is not None
    assert authenticated_user.username == 'nicotesting'


def test_authenticate_user_fail(test_user):

    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, 'wrongpassword', db)
    assert authenticated_user is False


def test_create_access_token():

    username = "testuser"
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)
    
    access_token = create_access_token(username, user_id, role, expires_delta)

    decode_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature':False})

    assert decode_token['sub'] == username
    assert decode_token['id'] == user_id
    assert decode_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_user_valid_token():

    enconde = {'sub':'testuser', 'id': 1, "role":'admin'}
    token = jwt.encode(enconde, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username':'testuser', 'id':1, 'user_role':'admin'}


@pytest.mark.asyncio
async def test_get_current_user_notvalid_token():

    enconde = {"role":'admin'}
    token = jwt.encode(enconde, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)
    
    assert excinfo.value.status_code == 401

