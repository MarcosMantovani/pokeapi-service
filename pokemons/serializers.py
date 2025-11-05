from rest_framework import serializers
from pokemons.models import Pokemon
from users.models import User
from pokemons.helpers import PokemonHelper


class PokemonSerializer(serializers.ModelSerializer):

    is_favorited = serializers.SerializerMethodField()

    def get_is_favorited(self, obj: Pokemon) -> bool:
        user = None
        if "request" in self.context and self.context["request"] is not None:
            user = getattr(self.context["request"], "user", None)
        elif "user" in self.context:
            user = self.context["user"]

        if user is None or not user.is_authenticated:
            return False

        return obj.is_favorited(user)

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
            "is_favorited",
        ]
