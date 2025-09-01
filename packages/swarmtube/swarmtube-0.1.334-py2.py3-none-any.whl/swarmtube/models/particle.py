import random
from typing import List, Dict, Any, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field

from syncmodels.definitions import UID, URI, TAG, REGEXP
from syncmodels.model import Datetime


# Particle Tags
PARTICLE_PRIMARY = "primary"
PARTICLE_DERIVED = "derived"
PARTICLE_FLUSH = "flush"

PARTICLE_TAGS = [
    PARTICLE_PRIMARY,
    PARTICLE_DERIVED,
    PARTICLE_FLUSH,
]

# class ParticleKindEnum(Enum):
#     """TBD
#     Type of Particles"""
#
#     FINAL = 1

PARTICLE_NS = "particle"
PARTICLE_DB = "particle"


class ParticleDefinition(BaseModel):
    id: UID = Field(
        description="the unique identifier of particle",
        examples=["".join([random.choice("0123456789abcdef") for _ in range(40)])],
    )
    target: URI = Field(
        description="the target uri as holder of KPI",
        examples=[
            "test://test/mypki",
        ],
    )
    sources: List[URI] = Field(
        [],
        description="all the source uris that particle needs for computing",
        examples=[
            [
                "test://test/source_a",
                "test://test/source_b",
            ],
        ],
    )
    kind: str = Field(
        description="the king (class) of the particle that must be used",
        examples=[
            "XParticle",
            # "test://particle/sma",
        ],
    )
    unit: Optional[str] = Field(
        None,
        description="a regexp to find the kind of particle",
        examples=[
            None,
            # "test://particle/sma",
        ],
    )
    specs: Dict[str, Any] = Field(
        {},
        description="the specs that overrides the default ones for the particle construction",
        examples=[
            {
                "__default__": 20,  # default
                "free": 4,
            },
        ],
    )
    cron: Dict[str, Any] | None = Field(
        None,
        description="crontab parameters for timed boundaries",
        examples=[
            {
                "second": 0,  # default
                "minute": 4,
            },
        ],
    )
    function: Optional[str] = Field(
        None,
        description="the lambda function used for built the output",
        examples=[
            "average",
            "max",
            # "test://particle/sma",
        ],
    )
    geo_locator: Optional[str] = Field(
        None,
        description="geo locator for the particle",
        examples=[
            "region_malaga.districts" "grid_mad_2x2",
            # "test://particle/sma",
        ],
    )
    mapper: Optional[str] = Field(
        None,
        description="mapper to be used for the output data",
        examples=["AEMETMeteorologicalStationMapper"],
    )
    lambda_mapper: Optional[str] = Field(
        None,
        description="mapper to be used to transform lambda calls",
        examples=["AEMETMeteorologicalStationMapper"],
    )
    lambda_exclude: Optional[str] = Field(
        r"",
        description="regexp of last key to be exclude from lambda operations",
    )
    # extract: Optional[Union[str, List]] = Field(
    #     None,
    #     description="regexp of values to be excluded when saving payload to storage",
    # )
    tags: List[TAG] = Field(
        [],
        description="",
        examples=[
            PARTICLE_TAGS,
        ],
    )
    group_by: List[TAG] = Field(
        [],
        description="",
        examples=[
            [
                "geo_key_hash",
            ],
        ],
    )
    # TODO: review, used?
    include: Optional[Dict[TAG, str]] = Field(
        {},
        description="",
        examples=[
            {
                "measure": ".*",
            }
        ],
    )
    # TODO: review, used?
    exclude: Optional[Dict[TAG, str]] = Field(
        {},
        description="",
        examples=[
            {
                "measure": ".*",
            }
        ],
    )
    drop: Optional[Dict[TAG, str]] = Field(
        None,
        description="",
        examples=[
            {
                "measure": ".*",
            }
        ],
    )
    delivery: Optional[str] = Field(
        "asap",
        description="",
        examples=[
            "asap",
            "sync",
        ],
    )
    description: str = Field(
        "",
        description="the particle configuration description or purpose",
        examples=[
            "this particle computes the Simple Median Average of two inputs sources"
        ],
    )
    updated: Optional[Datetime] = Field(None)


class ParticleRuntime(ParticleDefinition):
    hearbeat: Optional[Datetime] | None = Field(None)


# ---------------------------------------------------------
# Request
# ---------------------------------------------------------
# TODO: MOVE this class to `syncmodels` as foundations


class Request(BaseModel):
    """A Kraken request to task manager.
    Contains all query data and search parameters.
    """

    filter: Dict[REGEXP, REGEXP] = Field(
        {},
        description="""
        {key: value} inventory filter (both can be regular expressions).
        Multiples values are allowed using AND operator.
        """,
        examples=[
            {
                "fquid": "foo.*bar.*",
            },
            {"name(s)?": r"foo-\d+", "bar": r".*blah$"},
            {"name|path": r".*flow.*"},
        ],
    )


class ParticleRequest(Request):
    """A particle request message information"""


# ---------------------------------------------------------
# Response
# ---------------------------------------------------------
# TODO: MOVE this class to `syncmodels` as foundations


class Response(BaseModel):
    """A Kraken response to task manager.
    Contains the search results given by a request.
    """

    num_items: int = 0
    elapsed: float = 0.0
    # result: Dict[UID_TYPE, Item] = {}


class ParticleResponse(Response):
    """A Kraken response to task manager.
    Contains the search results given by a request.
    """

    data: Dict[URI, ParticleRuntime] = {}
