from datetime import timedelta
from django.utils import timezone
from django.db import models, transaction

from pokemons.models import Pokemon, PokemonSpecie, PokemonEvolutionChain
from pokemons.services import PokeApiService


service = PokeApiService()


class BasePokeApiHelper:
    model = None
    service_method = None
    cache_ttl_days = 7

    @classmethod
    def get_object(
        cls,
        name_or_id: str | int,
        *,
        force_update: bool = False,
        cache_days: int | None = None,
        **kwargs,
    ):
        """
        Busca no DB ou atualiza/cria a partir da API.
        kwargs são passados para create_instance/update_instance (ex: pokemon=..., specie=...).
        """
        assert cls.model is not None, "Defina cls.model no helper."
        assert cls.service_method is not None, "Defina cls.service_method no helper."

        cache_days = cache_days if cache_days is not None else cls.cache_ttl_days
        cutoff = timezone.now() - timedelta(days=cache_days)

        # build filter: externo ID (numérico) ou nome
        if isinstance(name_or_id, int) or str(name_or_id).isdigit():
            filters = models.Q(external_id=int(name_or_id))
        else:
            filters = models.Q(name__iexact=str(name_or_id))

        instance = cls.model.objects.filter(filters).first()

        # se existe e não for forçar atualização
        if instance and not force_update and instance.last_updated > cutoff:
            return instance

        # obtém dados da API
        data = cls.service_method(name_or_id)

        # atualiza ou cria usando os hooks
        if instance:
            return cls.update_instance(instance, data, **kwargs)
        else:
            return cls.create_instance(data, **kwargs)

    @classmethod
    def create_instance(cls, data: dict, **kwargs):
        """
        Create the instance in the database. Subclasses that need extra fields
        (ex: pokemon from specie) must override this method.
        """
        # by default creates only with the common fields
        return cls.model.objects.create(
            external_id=data["id"],
            name=data.get("name", f"unknown-{data['id']}"),
            data=data,
            last_updated=timezone.now(),
        )

    @classmethod
    def update_instance(cls, instance, data: dict, **kwargs):
        """
        Update the existing instance. Subclasses can override to
        handle additional relationships.
        """
        instance.data = data
        instance.last_updated = timezone.now()
        instance.save(update_fields=["data", "last_updated"])
        return instance


class PokemonHelper(BasePokeApiHelper):
    model = Pokemon
    service_method = service.get_pokemon

    @classmethod
    def get_object(cls, name_or_id: str | int):
        pokemon = super().get_object(name_or_id)
        PokemonSpecieHelper.get_object(name_or_id, pokemon=pokemon)
        return pokemon


class PokemonSpecieHelper(BasePokeApiHelper):
    model = PokemonSpecie
    service_method = service.get_pokemon_specie

    @classmethod
    def get_object(cls, name_or_id: str | int, *, pokemon=None, **kwargs):
        specie = super().get_object(name_or_id, pokemon=pokemon, **kwargs)

        # chama a evolution chain
        evo_chain_url = specie.data.get("evolution_chain", {}).get("url")
        if evo_chain_url:
            evo_chain_id = evo_chain_url.rstrip("/").split("/")[-1]
            evolution_chain = PokemonEvolutionChainHelper.get_object(
                int(evo_chain_id), specie=specie
            )

            # associa a specie e o pokemon
            evolution_chain.species.add(specie)
            if pokemon:
                evolution_chain.pokemons.add(pokemon)

        return specie

    @classmethod
    def create_instance(cls, data: dict, *, pokemon=None, **kwargs):
        if pokemon is None:
            raise ValueError(
                "PokemonSpecieHelper.create_instance requires the 'pokemon' parameter."
            )

        with transaction.atomic():
            instance = cls.model.objects.create(
                external_id=data["id"],
                name=data.get("name", f"unknown-{data['id']}"),
                data=data,
                pokemon=pokemon,
                last_updated=timezone.now(),
            )
        return instance

    @classmethod
    def update_instance(cls, instance, data: dict, *, pokemon=None, **kwargs):
        instance.data = data
        instance.last_updated = timezone.now()
        if pokemon and instance.pokemon_id != pokemon.id:
            instance.pokemon = pokemon
            instance.save(update_fields=["data", "last_updated", "pokemon"])
        else:
            instance.save(update_fields=["data", "last_updated"])
        return instance


class PokemonEvolutionChainHelper(BasePokeApiHelper):
    model = PokemonEvolutionChain
    service_method = service.get_evolution_chain

    @classmethod
    def create_instance(cls, data: dict, *, specie=None, **kwargs):
        if specie is None:
            raise ValueError(
                "PokemonEvolutionChainHelper.create_instance requires the 'specie' parameter."
            )

        with transaction.atomic():
            instance = cls.model.objects.create(
                external_id=data["id"],
                name=data.get("name", f"evo-chain-{data['id']}"),
                data=data,
                last_updated=timezone.now(),
            )

            # associa depois de criar
            instance.species.add(specie)
            if hasattr(specie, "pokemon"):
                instance.pokemons.add(specie.pokemon)

        return instance

    @classmethod
    def update_instance(cls, instance, data: dict, *, specie=None, **kwargs):
        instance.data = data
        instance.last_updated = timezone.now()
        instance.save(update_fields=["data", "last_updated"])

        if specie:
            instance.species.add(specie)
            if hasattr(specie, "pokemon"):
                instance.pokemons.add(specie.pokemon)

        return instance
