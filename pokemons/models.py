from django.db import models
from django.utils import timezone
from common.models import AbstractDatableModel


class AbstractPokeApiModel(AbstractDatableModel):
    external_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    data = models.JSONField()
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ["external_id"]


class Pokemon(AbstractPokeApiModel):
    @property
    def abilities(self):
        """Returns the abilities sorted alphabetically by ability.name"""
        abilities_list = self.data.get("abilities", [])
        return sorted(
            [
                a.get("ability", {}).get("name", "")
                for a in abilities_list
                if a.get("ability")
            ],
            key=str.lower,
        )

    @property
    def height(self):
        """Returns the height of the Pokemon"""
        return self.data.get("height")

    @property
    def weight(self):
        """Returns the weight of the Pokemon"""
        return self.data.get("weight")

    @property
    def types(self):
        """Returns only the type names, sorted alphabetically."""
        types_list = self.data.get("types", [])
        return sorted(
            [t.get("type", {}).get("name", "") for t in types_list if t.get("type")],
            key=str.lower,
        )

    @property
    def cry(self):
        """Returns only the latest cry URL."""
        cries = self.data.get("cries", {})
        return cries.get("latest")

    @property
    def sprites(self):
        """Returns a dict with the default and shiny sprites."""
        other = self.data.get("sprites", {}).get("other", {})
        official_artwork = other.get("official-artwork", {})
        return {
            "default": official_artwork.get("front_default"),
            "shiny": official_artwork.get("front_shiny"),
        }

    class Meta:
        verbose_name = "Pokemon"
        verbose_name_plural = "Pokemons"


class PokemonSpecie(AbstractPokeApiModel):
    pokemon = models.OneToOneField(
        Pokemon, on_delete=models.CASCADE, related_name="specie"
    )

    def __str__(self):
        return f"{self.name} Specie"

    class Meta:
        verbose_name = "Pokemon Specie"
        verbose_name_plural = "Pokemon Species"
        ordering = ["external_id"]


class PokemonEvolutionChain(AbstractPokeApiModel):
    """Represents a full evolution line shared by multiple species."""

    # remove OneToOne com specie/pokemon
    species = models.ManyToManyField(
        "PokemonSpecie",
        related_name="evolution_chains",
        blank=True,
    )
    pokemons = models.ManyToManyField(
        "Pokemon",
        related_name="evolution_chains",
        blank=True,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # optional logic to sync pokemons/species can go here

    def __str__(self):
        return f"{self.name} Evolution Chain"

    class Meta:
        verbose_name = "Pokemon Evolution Chain"
        verbose_name_plural = "Pokemon Evolution Chains"
        ordering = ["external_id"]
