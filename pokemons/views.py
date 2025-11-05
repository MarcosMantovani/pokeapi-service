from urllib.parse import urlparse, parse_qs
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from pokemons.helpers import PokemonHelper
from pokemons.services import PokeApiService
from pokemons.models import Pokemon, FavoritedPokemon, PokemonEvolutionChain
from pokemons.serializers import PokemonSerializer


class PokemonViewSet(viewsets.ModelViewSet):
    queryset = Pokemon.objects.all()
    serializer_class = PokemonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Override to fetch Pokemon by 'name' or 'external_id'
        instead of the internal database id.
        """
        identifier = self.kwargs.get("pk")

        if identifier.isdigit():
            identifier = int(identifier)

        try:
            pokemon = PokemonHelper.get_object(identifier)
        except Exception:
            raise NotFound(f"Pokemon '{identifier}' not found or could not be fetched.")

        return pokemon

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

    def retrieve(self, request, *args, **kwargs):
        """
        Overrides default retrieve to use the PokemonHelper,
        fetching data by name or external_id instead of the local database id.
        """
        identifier = kwargs.get("pk")

        # Allow either numeric external_id or string name
        if identifier.isdigit():
            identifier = int(identifier)

        try:
            pokemon = PokemonHelper.get_object(identifier)
        except Exception:
            return Response(
                {
                    "detail": f"Pokémon '{identifier}' not found or could not be fetched."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(pokemon)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def favorite(self, request, *args, **kwargs):
        pokemon = self.get_object()
        serializer = self.get_serializer(pokemon)
        serializer.favorite(request.user, pokemon)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def unfavorite(self, request, *args, **kwargs):
        pokemon = self.get_object()
        serializer = self.get_serializer(pokemon)
        pokemon = serializer.unfavorite(request.user, pokemon)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PokemonEvolutionChainViewSet(viewsets.ViewSet):
    """
    Retrieve the evolution chain of a given Pokémon.
    """

    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, pk=None):
        """
        Fetch the evolution chain for a Pokémon by its name or external_id.
        """
        if pk is None:
            raise NotFound("Pokémon identifier is required.")

        # Resolve Pokémon by name or external_id
        try:
            pokemon = PokemonHelper.get_object(pk)
        except Exception:
            raise NotFound(f"Pokémon '{pk}' not found.")

        # Find the evolution chain related to this Pokémon
        chain_qs = PokemonEvolutionChain.objects.filter(pokemons=pokemon)
        if not chain_qs.exists():
            return Response(
                {"detail": "Evolution chain not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        chain = chain_qs.first()
        # structured_chain property formats it for the frontend
        return Response(chain.structured_chain(request.user), status=status.HTTP_200_OK)


class FavoritedPokemonPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "limit"
    page_query_param = "page"


class FavoritedPokemonViewSet(viewsets.ViewSet):
    """
    Returns the favorited Pokémon of the authenticated user
    """

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        favorites_qs = FavoritedPokemon.objects.filter(user=user).select_related(
            "pokemon"
        )

        paginator = FavoritedPokemonPagination()
        page = paginator.paginate_queryset(favorites_qs, request)
        pokemons = [fav.pokemon for fav in page] if page else []

        serializer = PokemonSerializer(
            pokemons, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)
