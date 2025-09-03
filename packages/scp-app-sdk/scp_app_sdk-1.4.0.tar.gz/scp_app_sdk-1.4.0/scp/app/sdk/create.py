import requests
import urllib3


class AppCreationException(Exception):
    def __init__(self, message, status_code=None, response_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class MissingTokenException(Exception):
    pass


def create_app(remote_server, name, id=None, token=None):
    """
    Create a new APP on the SCP APP store
    :param remote_server: SCP APP store server url
    :param name: name of the APP
    :return: APP ID
    """
    headers = None
    if not token:
        raise MissingTokenException("Token is required to create an APP on the SCP APP store")

    headers = {
        "Authorization": f"Bearer {token}" if "Bearer" not in token else token
    }
    data = dict(
        name=name
    )
    if id:
        data['id'] = id
    try:
        response = requests.post(
            url=f'{remote_server}/api/v1/apps',
            headers=headers,
            verify=False,
            json=data
        )
    except requests.exceptions.RequestException as e:
        raise AppCreationException(
            f"SCP APP store error {response.status_code}",
            status_code=response.status_code,
            response_body=response.text
        )

    if response.status_code not in (200, 201):
        raise AppCreationException(
            f"SCP APP store error {response.status_code}",
            status_code=response.status_code,
            response_body=response.text
        )

    return response.json().get('id')
