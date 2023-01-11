import requests

class MtgApi:
    '''
    https://docs.magicthegathering.io/#documentationgetting_started
    '''

    def __init__(self) -> None:
        self.url = "https://api.magicthegathering.io/v1"

    def find_card_by_name(self, name: str):

        response = requests.get(f'{self.url}/cards?name={name}')
        response.raise_for_status()
        data = response.json()
        return data["cards"][0]

