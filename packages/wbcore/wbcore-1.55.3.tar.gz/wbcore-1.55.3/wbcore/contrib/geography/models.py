from typing import Optional

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.lookups import Unaccent
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.db.models.expressions import Value
from django.db.models.functions import Lower
from django.db.models.query import QuerySet
from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey
from text_unidecode import unidecode
from timezone_field import TimeZoneField

from wbcore.models import WBModel


class LeveledGeographyManager(TreeManager):
    def get_by_natural_key(self, code_2):
        if self.level == 1:
            return self.get(code_2=code_2)

    def get_by_name(self, name, **extra_filter_args):
        qs = self
        if extra_filter_args:
            qs = qs.filter(**extra_filter_args)
        return (
            qs.annotate(name_unaccent=Unaccent(Lower("name")))
            .filter(models.Q(name_unaccent=unidecode(name).lower()) | models.Q(alternative_names__contains=[name]))
            .order_by("ranking")
            .first()
        )

    def __init__(self, level: Optional[int] = None, *args, **kwargs):
        self.level = level
        super().__init__(*args, **kwargs)

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        if level := self.level:
            return queryset.filter(level=level)
        return queryset


class Geography(WBModel, MPTTModel):
    class Level(models.IntegerChoices):
        CONTINENT = 0, "Continent"
        COUNTRY = 1, "Country"
        STATE = 2, "State"
        CITY = 3, "City"

    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    alternative_names = ArrayField(
        base_field=models.CharField(max_length=255),
        default=list,
        blank=True,
        verbose_name="Alternative Names",
        help_text="Alternative Names",
    )
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    representation = models.CharField(max_length=255, default="", blank=True)

    search_vector = SearchVectorField(null=True)
    trigram_search_vector = models.CharField(max_length=1024, null=True, blank=True)

    code_2 = models.CharField(max_length=2, verbose_name="2 Character Alphanumeric Code", null=True, blank=True)
    code_3 = models.CharField(max_length=3, verbose_name="3 Character Alphanumeric Code", null=True, blank=True)
    code = models.CharField(max_length=16, verbose_name="Code", null=True, blank=True)

    population = models.PositiveIntegerField(null=True, blank=True)
    ranking = models.PositiveIntegerField(default=1)
    time_zone = TimeZoneField(choices_display="WITH_GMT_OFFSET", null=True, blank=True)

    objects = LeveledGeographyManager()
    continents = LeveledGeographyManager(level=0)
    countries = LeveledGeographyManager(level=1)
    states = LeveledGeographyManager(level=2)
    cities = LeveledGeographyManager(level=3)

    def lookup_descendants(self, name: str, level: Optional[int] = None) -> models.Model | None:
        qs = self.get_descendants()
        if level is not None:
            qs = qs.filter(level=level)

        qs = qs.annotate(name_unaccent=Unaccent(Lower("name"))).filter(
            models.Q(name_unaccent=unidecode(name).lower()) | models.Q(alternative_names__contains=[name])
        )
        if qs.count() == 1:
            return qs.first()

    class Meta:
        verbose_name_plural = "Geographies"
        indexes = [
            GinIndex(fields=["search_vector"], name="geography_sv_gin_idx"),  # type: ignore
            GinIndex(
                fields=["trigram_search_vector"], opclasses=["gin_trgm_ops"], name="geography_trigram_sv_gin_idx"
            ),  # type: ignore
        ]
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_level_code2__uniq",
                fields=("level", "code_2"),
                condition=models.Q(level=1),
            ),
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_level_code3__uniq",
                fields=("level", "code_3"),
                condition=models.Q(level=1),
            ),
        ]

    def update_search_vectors(self):
        alternative_names = [Value(name) for name in self.alternative_names]
        self.search_vector = SearchVector(Value(self.name), *alternative_names)
        self.trigram_search_vector = f"{self.name} {' '.join(self.alternative_names)}".strip()

    def save(self, *args, **kwargs):
        self.update_search_vectors()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name}"

    @classmethod
    def dict_to_model(cls, country_data, level=Level.COUNTRY):
        qs = Geography.objects.filter(level=level)
        if isinstance(country_data, int):
            return qs.filter(id=country_data).first()
        elif code := country_data.get("code", None):
            return qs.filter(code_3=code).first()
        elif code_alpha2 := country_data.get("code_alpha2", None):
            return qs.filter(code_2=code_alpha2).first()

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcore:geography:geography"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcore:geography:geographyrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{representation}}"
