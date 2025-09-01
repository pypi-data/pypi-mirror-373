from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum

from ....core.classes.data_source.data_source_parameters import (
    DataSourceParameters,
)


class CategoryEnum(str, Enum):
    def __str__(self):
        return self.value

    NONE = ""
    ZVIERATA = "zvierata"
    DETI = "deti"
    REALITY = "reality"
    PRACA = "praca"
    AUTO = "auto"
    MOTOCYKLE = "motocykle"
    STROJE = "stroje"
    DOM_A_ZAHRADA = "dom_a_zahrada"
    PC = "pc"
    MOBILY = "mobily"
    FOTO = "foto"
    ELEKTRO = "elektro"
    SPORT = "sport"
    HUDBA = "hudba"
    VSTUPENKY = "vstupenky"
    KNIHY = "knihy"
    NABYTOK = "nabytok"
    OBLECENIE = "oblecenie"
    SLUZBY = "sluzby"
    OSTATNE = "ostatne"


class BazosSkParameters(BaseModel, DataSourceParameters):
    category: Optional[CategoryEnum] = Field(
        CategoryEnum.NONE,
        json_schema_extra={"uri_param_name": "rub"},
    )
    search: Optional[str] = Field(
        "",
        examples=["iPhone 12"],
        json_schema_extra={"uri_param_name": "hledat"},
    )
    location: Optional[str] = Field(
        "",
        title="Location (ZIP)",
        examples=["12345"],
        json_schema_extra={"uri_param_name": "hlokalita"},
    )
    radius: Optional[int] = Field(
        25,
        title="Radius (km)",
        ge=0,
        examples=[25],
        json_schema_extra={"uri_param_name": "humkreis"},
    )
    min_price: Optional[int] = Field(
        None,
        title="Min price (eur)",
        ge=0,
        examples=[100],
        json_schema_extra={"uri_param_name": "cenaod"},
    )
    max_price: Optional[int] = Field(
        None,
        title="Max price (eur)",
        ge=0,
        examples=[500],
        json_schema_extra={"uri_param_name": "cenado"},
    )

    @field_validator("location")
    def validate_location(cls, value):
        if not value:
            return value

        if not value.isdigit() or len(value) != 5:
            raise ValueError(
                "Location must be in the form of a 5 digit number (12345)."
            )
        return value
