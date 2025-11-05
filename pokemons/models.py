from django.db import models
from django.utils import timezone
from typing import Dict, Any
from common.models import AbstractDatableModel
from users.models import User


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

    @property
    def flavor_text(self) -> str:
        """
        Returns the English flavor text from the related specie.
        """
        if hasattr(self, "specie") and self.specie:
            return self.specie.flavor_text
        return ""

    def is_favorited(self, user: User) -> bool:
        return FavoritedPokemon.objects.filter(user=user, pokemon=self).exists()

    class Meta:
        verbose_name = "Pokemon"
        verbose_name_plural = "Pokemons"


class PokemonSpecie(AbstractPokeApiModel):
    pokemon = models.OneToOneField(
        Pokemon, on_delete=models.CASCADE, related_name="specie"
    )

    @property
    def flavor_text(self) -> str:
        """
        Returns the English flavor text (summary) of the Pokemon specie.
        """
        entries = self.data.get("flavor_text_entries", [])
        for entry in entries:
            if entry.get("language", {}).get("name") == "en":
                return (
                    entry.get("flavor_text", "").replace("\n", " ").replace("\f", " ")
                )
        return ""

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

    def _parse_chain_node(
        self, node: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Builds the representation of the chain node.
        """
        from pokemons.serializers import PokemonSerializer

        species_name = node["species"]["name"]
        pokemon = Pokemon.objects.filter(name=species_name).first()
        if not pokemon:
            return {}

        # Serializes the Pokemon
        pokemon_data = PokemonSerializer(pokemon, context=context).data

        # Interprets evolution_details
        details = node.get("evolution_details", [])
        if details:
            # For simplicity, we will take the first detail
            detail = details[0]
            evolution_text = self._build_evolution_text(detail)
        else:
            evolution_text = None

        # Processes future evolutions
        evolves = node.get("evolves_to", [])
        evolves_to = (
            [self._parse_chain_node(e, context) for e in evolves] if evolves else []
        )

        return {
            "pokemon": pokemon_data,
            "evolution_text": evolution_text,
            "evolves_to": evolves_to,
        }

    def _build_evolution_text(self, detail: Dict[str, Any]) -> str:
        """
        Interprets the evolution details and returns a friendly text.
        """
        trigger = detail.get("trigger", {}).get("name", "")
        min_level = detail.get("min_level")
        item = detail.get("item")
        gender = detail.get("gender")
        time_of_day = detail.get("time_of_day")
        # Add more fields if you want to detail more

        parts = []
        if trigger == "level-up" and min_level:
            parts.append(f"evolve ao subir para nível {min_level}")
        elif trigger == "trade":
            parts.append("evolve ao trocar com outro jogador")
        elif trigger == "use-item" and item:
            parts.append(f"evolve usando {item.get('name')}")
        else:
            parts.append(f"evolve via {trigger}")

        if gender is not None:
            parts.append(f"se for do gênero {gender}")
        if time_of_day:
            parts.append(f"durante {time_of_day}")

        return ", ".join(parts)

    def structured_chain(self, user: User) -> Dict[str, Any]:
        """
        Returns the structured evolution chain for the frontend.
        """
        return self._parse_chain_node(self.data["chain"], context={"user": user})

    def __str__(self):
        return f"{self.name} Evolution Chain"

    class Meta:
        verbose_name = "Pokemon Evolution Chain"
        verbose_name_plural = "Pokemon Evolution Chains"
        ordering = ["external_id"]


class FavoritedPokemon(AbstractDatableModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorited_pokemons"
    )
    pokemon = models.ForeignKey(
        Pokemon, on_delete=models.CASCADE, related_name="favorited_pokemons"
    )

    def __str__(self):
        return f"{self.user.username} favorited {self.pokemon.name}"

    class Meta:
        verbose_name = "Favorited Pokemon"
        verbose_name_plural = "Favorited Pokemons"
        ordering = ["user", "pokemon"]
