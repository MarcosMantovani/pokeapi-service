from urllib.parse import urlparse, parse_qs
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

        # serialize local Pokémon objects
        serializer = self.get_serializer(results, many=True)

        # utility function to convert PokeAPI URLs to local URLs
        def convert_url(external_url):
            if not external_url:
                return None
            parsed = urlparse(external_url)
            params = parse_qs(parsed.query)
            next_limit = params.get("limit", [limit])[0]
            next_offset = params.get("offset", [offset])[0]
            base_url = request.build_absolute_uri(request.path)
            return f"{base_url}?limit={next_limit}&offset={next_offset}"

        return Response(
            {
                "count": api_response.get("count"),
                "next": convert_url(api_response.get("next")),
                "previous": convert_url(api_response.get("previous")),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
