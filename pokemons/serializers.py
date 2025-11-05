from rest_framework import serializers
from pokemons.models import Pokemon
from users.models import User
from pokemons.helpers import PokemonHelper


class PokemonSerializer(serializers.ModelSerializer):

    def favorite(self, user: User, pokemon: Pokemon):
        return PokemonHelper.favorite_pokemon(user, pokemon)

    def unfavorite(self, user: User, pokemon: Pokemon):
        return PokemonHelper.unfavorite_pokemon(user, pokemon)

    class Meta:
        model = Pokemon
        fields = [
            "id",
            "external_id",
            "name",
            "sprites",
            "flavor_text",
            "abilities",
            "height",
            "weight",
            "types",
            "cry",
        ]
