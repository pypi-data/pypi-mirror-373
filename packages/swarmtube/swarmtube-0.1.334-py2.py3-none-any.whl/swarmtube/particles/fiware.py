"""
`FIWARE` support classes
"""

import asyncio
import json
import re
import sys
import traceback
from datetime import datetime
import functools

import aiohttp


from agptools.logs import logger
from agptools.helpers import DATE, camel_case_split, tf


from syncmodels.definitions import (
    ORG_KEY,
    THINK_KEY,
    MONOTONIC_KEY,
    ID_KEY,
    GEOJSON_KEY,
)

from syncmodels.crud import parse_duri
from syncmodels.helpers.orion import OrionInjector
from syncmodels.helpers.crawler import SortKeyFinder, GeojsonManager


from swarmtube import __version__
from ..logic.swarmtube import (
    Particle,
    SkipWave,
    RetryWave,
)


log = logger(__file__)


class OrionParticleSync(Particle):
    """Generic Particle to synchronize data with Orion"""

    # TODO: set by config / yaml
    # Note: for batch update use the following url (doesn't apply right now as is one to one)
    # url = "hhttps://orion.example.com:1026/v2/op/update?options=flowControl"

    def __init__(
        self,
        uid,
        sources,
        broker,
        storage,
        orion: OrionInjector,
        since=None,
    ):
        super().__init__(uid, sources, broker, storage, since)
        # self.target_url = orion.target_url or self.TARGET_URL

        # self.service = service
        # self.service_path = service_path

        self.orion = orion

    async def _compute(self, edge, ekeys):
        """
        # TODO: looks like is a batch insertion! <-----

        Example
        {
        "actionType": "APPEND",
        "entities": [
            {
                "id": "TL1",
                "type": "totem.views",
                "ts": {
                    "value": "2024-03-06 09:43:11",
                    "type": "timestamp"
                },
                "conteo": {
                    "value": 9,
                    "type": "integer"
                },
                "component": {
                    "value": "C11 - TOTEMS",
                    "type": "string"
                },
                "place": {
                    "value": "LUCENTUM",
                    "type": "string"
                },
                "location": {
                    "type": "geo:point",
                    "value": "38.365156979723906,-0.438225677848391"
                }
            }
        ]
        }

        crateDB fields:

        - entity_location: geo_point
        - entity_type: String
        - fiware_service: String
        - entity_id: String
        - entity_ts: Timestamp
        - validity_ts: Timestamp

        note that 'ts' is missing

        """
        # assert len(ekeys) == 1, "Stream must have just 1 input tube"

        # returning None so no data is really needed to sync
        # just advance the TubeSync wave-mark

        # set 'fiware-servicepath' and 'type' based on tube_name
        def xtf(name, sep):
            x = tf(name)
            x = re.sub(f"_+", sep, x)
            return x

        dtf = functools.partial(xtf, sep=".")  # uri -> orion type

        for tube_name in ekeys:
            stream = edge[tube_name]
            if isinstance(stream, dict):
                stream = [stream]
            if not isinstance(stream, list):
                # TODO: review
                pass

            _fquid = parse_duri(tube_name)

            for data in stream:
                for key, info in {
                    "path": (
                        [
                            "fiware-servicepath",
                            lambda x: x.replace("_", "/"),
                        ],
                    ),
                    "uri": (
                        [
                            "type",  # the type sent to orion
                            dtf,
                        ],
                    ),
                }.items():

                    value = _fquid[key]
                    for where, translate in info:
                        _value = translate(value)
                        data.setdefault(where, _value)

                # add geo-json information
                if not data.get(GEOJSON_KEY):
                    geo_uri = GeojsonManager.geo_uri(data)
                    if geo_uri:
                        # TODO: agp: remove HACK
                        geo_uri = geo_uri.replace(
                            "climate_observations", "meteorological_stations"
                        )

                        for geoitem in await self.storage.query(geo_uri):
                            # TODO: use define for this parameter (model/geojson.py)
                            data[GEOJSON_KEY] = geoitem.get(GEOJSON_KEY)
                    else:
                        log.warning("data hasn't GOJSON info: [%s]", data)

                result = await self.orion.push(data)
                foo = 2
        yield None
