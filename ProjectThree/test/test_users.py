from .utils import *
from ..routers.users import get_db, get_current_user

app.dependency_overrides[get_db] = override_get_db  # Sobrescribe la dependencia get_db en la aplicación
app.dependency_overrides[get_current_user] = override_get_current_user  # Sobrescribe la dependencia get_current_user en la aplicación

def test_return_user(test_user):
    response = client.get('/users/user_data')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'nicotesting'
    assert response.json()['firstname'] == 'Nicolas'
    assert response.json()['lastname'] == 'Bernard'
    assert response.json()['email'] == 'nicolasemanuetest@gmail.com'
    assert response.json()['phone_number'] == '1111'
    assert response.json()['role'] == 'admin'


def test_change_password_success(test_user):
    response = client.put("/users/change_password", json={'old_password':'testpassword', 'new_password':'newpassword'}) ## Debe coincidir con el pydantic recordar
    assert response.status_code == status.HTTP_200_OK


def test_change_password_invalid(test_user):
    response = client.put("/users/change_password", json={'old_password':'invalidPass', 'new_password':'newpassword'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    

def test_change_phone_number(test_user):
    response = client.put("/users/update_phone", json={"phone_number" : "22222"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    