from django.contrib import admin
from pokemons.models import (
    Pokemon,
    PokemonSpecie,
    PokemonEvolutionChain,
    FavoritedPokemon,
)
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget


# ----- Inline for Specie (still linked directly to Pokemon)
class PokemonSpecieInline(admin.StackedInline):
    model = PokemonSpecie
    extra = 0
    can_delete = False
    readonly_fields = ["external_id", "name", "last_updated"]
    fieldsets = (
        (
            None,
            {"fields": ("external_id", "name", "data", "last_updated")},
        ),
    )

    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }


# ----- Pokémon Admin
@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ["external_id", "name", "last_updated"]
    search_fields = ["external_id", "name"]
    list_filter = ["last_updated"]
    inlines = [PokemonSpecieInline]
    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }

    # Display evolution chains directly in the admin list
    def evolution_chains_display(self, obj):
        return ", ".join(chain.name for chain in obj.evolution_chains.all()) or "—"

    evolution_chains_display.short_description = "Evolution Chains"


# ----- Evolution Chain Admin
@admin.register(PokemonEvolutionChain)
class PokemonEvolutionChainAdmin(admin.ModelAdmin):
    list_display = [
        "external_id",
        "name",
        "species_list",
        "pokemons_list",
        "last_updated",
    ]
    search_fields = ["external_id", "name", "species__name", "pokemons__name"]
    list_filter = ["last_updated"]

    readonly_fields = ["external_id", "name", "last_updated"]
    filter_horizontal = ["species", "pokemons"]

    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }

    def species_list(self, obj):
        return ", ".join(s.name for s in obj.species.all()) or "—"

    species_list.short_description = "Species"

    def pokemons_list(self, obj):
        return ", ".join(p.name for p in obj.pokemons.all()) or "—"

    pokemons_list.short_description = "Pokémons"


# ----- Specie Admin
@admin.register(PokemonSpecie)
class PokemonSpecieAdmin(admin.ModelAdmin):
    list_display = ["external_id", "name", "evolution_chains_list", "last_updated"]
    search_fields = ["external_id", "name", "evolution_chains__name"]
    list_filter = ["last_updated"]

    readonly_fields = ["external_id", "name", "last_updated"]
    filter_horizontal = ["evolution_chains"]

    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }

    def evolution_chains_list(self, obj):
        return ", ".join(chain.name for chain in obj.evolution_chains.all()) or "—"

    evolution_chains_list.short_description = "Evolution Chains"


@admin.register(FavoritedPokemon)
class FavoritedPokemonAdmin(admin.ModelAdmin):
    list_display = ("user", "pokemon", "created_at", "updated_at")
    list_filter = ("user", "pokemon")
    search_fields = ("user__username", "pokemon__name")
    ordering = ("user", "pokemon")
