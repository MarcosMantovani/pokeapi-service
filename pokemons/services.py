import os

from common.utils import make_api_request

POKE_API_BASE_URL = "https://pokeapi.co/api/v2"


class PokeApiService:

    def __init__(self):

        self.base_url = os.getenv("BASE_URL", POKE_API_BASE_URL)

    def make_request(
        self, endpoint: str, method: str, payload: dict = None, params: dict = None
    ):
        data, _ = make_api_request(
            method=method,
            url=self.base_url + endpoint,
            payload=payload,
            params=params,
            log_prefix="PokeAPI",
        )
        return data

    def get_pokemon(self, name_or_id: str | int):
        endpoint = f"/pokemon/{name_or_id}"
        return self.make_request(endpoint, "get")

    def get_pokemon_list(self, limit: int = 20, offset: int = 0):
        endpoint = f"/pokemon?limit={limit}&offset={offset}"
        return self.make_request(endpoint, "get")

    def get_pokemon_specie(self, id: int):
        endpoint = f"/pokemon-species/{id}"
        return self.make_request(endpoint, "get")

    def get_pokemon_species_list(self, limit: int = 20, offset: int = 0):
        endpoint = f"/pokemon-species?limit={limit}&offset={offset}"
        return self.make_request(endpoint, "get")

    def get_evolution_chain(self, id: int):
        endpoint = f"/evolution-chain/{id}"
        return self.make_request(endpoint, "get")

    def get_evolution_chains_list(self, limit: int = 20, offset: int = 0):
        endpoint = f"/evolution-chain?limit={limit}&offset={offset}"
        return self.make_request(endpoint, "get")

    def get_pokemon_type(self, name_or_id: str | int):
        endpoint = f"/type/{name_or_id}"
        return self.make_request(endpoint, "get")

    def get_pokemon_types_list(self, limit: int = 20, offset: int = 0):
        endpoint = f"/type?limit={limit}&offset={offset}"
        return self.make_request(endpoint, "get")

    def get_pokemon_move(self, name_or_id: str | int):
        endpoint = f"/move/{name_or_id}"
        return self.make_request(endpoint, "get")

    def get_pokemon_moves_list(self, limit: int = 20, offset: int = 0):
        endpoint = f"/move?limit={limit}&offset={offset}"
        return self.make_request(endpoint, "get")

    def get_item(self, name_or_id: str | int):
        endpoint = f"/item/{name_or_id}"
        return self.make_request(endpoint, "get")

    def get_items_list(self, limit: int = 20, offset: int = 0):
        endpoint = f"/item?limit={limit}&offset={offset}"
        return self.make_request(endpoint, "get")

    def get_ability(self, name_or_id: str | int):
        endpoint = f"/ability/{name_or_id}"
        return self.make_request(endpoint, "get")

    def get_abilities_list(self, limit: int = 20, offset: int = 0):
        endpoint = f"/ability?limit={limit}&offset={offset}"
        return self.make_request(endpoint, "get")

    def get_generation(self, id: int):
        endpoint = f"/generation/{id}"
        return self.make_request(endpoint, "get")

    def get_generations_list(self, limit: int = 20, offset: int = 0):
        endpoint = f"/generation?limit={limit}&offset={offset}"
        return self.make_request(endpoint, "get")

    def get_location(self, name_or_id: str | int):
        endpoint = f"/location/{name_or_id}"
        return self.make_request(endpoint, "get")

    def get_locations_list(self, limit: int = 20, offset: int = 0):
        endpoint = f"/location?limit={limit}&offset={offset}"
        return self.make_request(endpoint, "get")
