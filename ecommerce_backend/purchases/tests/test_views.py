import pytest
from django.urls import reverse


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize(
    "payload,response_code,response_body",
    [
        ({}, 400, {"username": ["This field is required."]}),
        ({"first_name": "John"}, 400, {"username": ["This field is required."]}),
        (
            {"first_name": "John", "username": ""},
            400,
            {"username": ["This field may not be blank."]},
        ),
        (
            {"username": "jsilver234", "first_name": "John", "last_name": "Silver"},
            201,
            {
                "id": 1,
                "first_name": "John",
                "last_name": "Silver",
                "username": "jsilver234",
            },
        ),
    ],
)
def test_create_person(app, payload, response_code, response_body):
    response = app.post(reverse("purchases:persons"), payload)
    assert response.status_code == response_code
    assert response.json() == response_body
