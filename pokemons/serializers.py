from rest_framework import serializers
from pokemons.models import Pokemon


class PokemonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pokemon
        fields = [
            "id",
            "external_id",
            "name",
            "sprites",
            "abilities",
            "height",
            "weight",
            "types",
            "cry",
        ]
