import os

import requests


class Csfe:
    def __init__(self, type: str):
        """
        CSFE abstraction

        :param url: SAM URL
        :param type: CSFE type
        """
        self.type = type
        self.user_id = os.environ.get("USER_ID")
        self._sam_url = os.environ.get("SAM_URL")

    def onboard(self, config: dict) -> dict:
        """
        Onboard a user with the provided configuration.

        :param user_id: The ID of the user to onboard.
        :param config: A dictionary containing the user's configuration details.

        :return: A dictionary containing the status code and response data from the CSFE service.
        """
        response = None
        url = f"{self._sam_url}/api/v1/users/{self.user_id}/csfe"
        config['type'] = self.type
        response = requests.post(url, json=config)
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "message": "Onboarding successful",
            "data": response.json()
        }

    def offboard(self) -> dict:
        """
        Off board a user by sending a DELETE request.

        :param user_id: The ID of the user to offboarding.

        :return: A dictionary containing the status code and response message from the CSFE service.
        """

        # Get CSFE ID
        try:
            response = requests.get(f"{self._sam_url}/api/v1/users/{self.user_id}/csfe")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return {
                "status_code": response.status_code if response else 500,
                "message": str(e)
            }

        csfe_list = response.json()['data']
        csfe_list = [csfe for csfe in csfe_list if csfe['type'] == self.type]
        if len(csfe_list) == 0:
            return {
                "status_code": 500,
                "message": f"No CSFE to delete for {self.type}"
            }
        elif len(csfe_list) > 1:
            return {
                "status_code": 500,
                "message": f"Too much CSFE to remove for {self.type}"
            }

        csfe_id = csfe_list[0]['id']

        # Delete CSFE
        response = requests.delete(f"{self._sam_url}/api/v1/users/{self.user_id}/csfe/{csfe_id}")
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "message": "Unboarding successful"
        }
