from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PokemonViewSet

app_name = "pokemons"

router = DefaultRouter()
router.register(r"pokemons", PokemonViewSet, basename="pokemon")


urlpatterns = [
    path("", include(router.urls)),
]
