from rest_framework.response import Response
from rest_framework import status, viewsets
from pokemons.helpers import PokemonHelper
from pokemons.services import PokeApiService
from pokemons.models import Pokemon
from pokemons.serializers import PokemonSerializer


class PokemonViewSet(viewsets.ModelViewSet):
    queryset = Pokemon.objects.all()
    serializer_class = PokemonSerializer

    def list(self, request, *args, **kwargs):
        """
        Overrides default list to fetch the list directly from the PokeAPI,
        then ensures each Pokémon is synchronized locally via PokemonHelper.
        """
        limit = int(request.query_params.get("limit", 20))
        offset = int(request.query_params.get("offset", 0))

        service = PokeApiService()
        api_response = service.get_pokemon_list(limit=limit, offset=offset)

        results = []
        for item in api_response.get("results", []):
            name = item.get("name")
            if not name:
                continue

            # get or create/update the pokemon via our helper
            pokemon = PokemonHelper.get_object(name)
            results.append(pokemon)

        # serialize the local Pokémon objects
        serializer = self.get_serializer(results, many=True)

        return Response(
            {
                "count": api_response.get("count"),
                "next": api_response.get("next"),
                "previous": api_response.get("previous"),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
