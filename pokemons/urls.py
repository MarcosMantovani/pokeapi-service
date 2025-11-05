from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PokemonViewSet, FavoritedPokemonViewSet, PokemonEvolutionChainViewSet

app_name = "pokemons"

router = DefaultRouter()
router.register(r"pokemons", PokemonViewSet, basename="pokemon")
router.register(
    r"evolution-chains", PokemonEvolutionChainViewSet, basename="evolution-chain"
)
router.register(
    r"favorited-pokemons", FavoritedPokemonViewSet, basename="favorited-pokemon"
)


urlpatterns = [
    path("", include(router.urls)),
]
