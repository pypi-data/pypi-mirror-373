"""Main module."""

# library modules
import asyncio
import random
import re
import sys
import traceback
import functools
from collections import deque
from typing import Callable, List, Dict, Any, Union
from datetime import datetime
from pprint import pformat
from pydantic import BaseModel
import pickle
import functools
import hashlib
from functools import reduce
import operator
import time
import pytz

import yaml
import pandas as pd


from glom import glom, Iter, T, Flatten, Coalesce, Fold, Merge

from jinja2 import Template, StrictUndefined

from geomdl import BSpline, utilities, fitting

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from agptools.helpers import (
    build_uri,
    DATE,
    SDATE,
    TO_NS,
    NOW,
    parse_uri,
    build_uri,
    LOCAL_TZ,
    FloatWhen,
)
from agptools.containers import (
    walk,
    Walk,
    rebuild,
    merge,
    soft,
    overlap,
    flatten,
    collect,
    exclude_dict,
    complete,
    complete_on,
    flatten,
)
from agptools.loaders import Finder
from agptools.containers import index
from agptools.logs import logger
from agptools.progress import Progress
from agptools.crontab import Crontab

from syncmodels.crud import parse_duri
from syncmodels.geofactory import GeoFactory
from syncmodels.helpers.crawler import GeojsonManager

from syncmodels.storage import (
    Storage,
    WaveStorage,
    tf,
    REG_SPLIT_PATH,
    SurrealConnectionPool,
)
from syncmodels.definitions import (
    URI,
    JSON,
    UID,
    WAVE,
    ORG_KEY,
    ID_KEY,
    REG_SPLIT_ID,
    extract_wave,
    DATETIME_KEY,
    REG_PRIVATE_KEY,
    EDGE,
    monotonic_wave,
    WAVE_RESUMING_INFO_KEY,
    WAVE_RESUMING_SOURCES,
)
from syncmodels.wave import TUBE_SNAPSHOT
from syncmodels.model.geojson import to_geojson, GEO_FACTORY
from syncmodels.mapper import Mapper

from smartmodels.tokens import NAMESPACES, LOCATION, TYPES, ASPECT

# ---------------------------------------------------------
# local imports
# ---------------------------------------------------------
from ..definitions import MONOTONIC_KEY

WAVE_FACTOR = 10**9

GEO_FILTER_DEFAULT_GRID_MAD_ID = "grid_mad_2x2"
# ---------------------------------------------------------
# models / mappers
# ---------------------------------------------------------
# from ..models.swarmtube import SwarmtubeApp
# from .. import mappers
# from ..models.enums import *
# from ..definitions import TAG_KEY

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

log = logger(__name__)


class Event(BaseModel):
    "TBD"

    wave: WAVE
    uid: UID
    payload: Any = None


class Broker:
    "Basic Broker capabilities"

    def __init__(self):
        self.subscriptions: Dict[UID, List[Callable]] = {}

    async def start(self):
        "any action related to start broker operations"

    async def stop(self):
        "any action related to stop broker operations"

    async def subscribe(self, uid: UID, callback: Callable):
        "TBD"
        inventory = self.subscriptions.setdefault(uid, [])
        if callback not in inventory:
            inventory.append(callback)

    async def unsubscribe(self, uid: UID, callback: Callable):
        "TBD"
        inventory = self.subscriptions.setdefault(uid, [])
        if callback in inventory:
            inventory.remove(callback)

    async def is_connected(self):
        return True


# TODO: agp: unify with syncmodels.crawler.iAgent?
class iAgent:  # TODO: agp: is the same as syncmodels.iAgent/iRunner?
    IDLE_SLEEP = 5

    def __init__(
        self,
        uid,
        broker: Broker,
        storage: Union[WaveStorage, Storage],
        meta=None,
        prefix="",
        target="",
        dead=None,
        *args,
        **kw,
    ):
        if not prefix:
            prefix = uid
        self.uid = uid
        self.broker = broker
        self.storage = storage

        self.state = ST_INIT
        self.dead = dead + time.time() if dead else sys.float_info.max
        self.meta = {} if meta is None else meta

        # prefix template
        # TODO: agp: have the same capabilities as syncmodels.iAgent
        self.prefix = prefix
        if prefix:
            if isinstance(prefix, str):
                _uri = parse_duri(prefix)
                if not _uri["_path"] and (
                    m := re.match(r"/?(?P<prefix>.*?)/?$", prefix)
                ):
                    d = m.groupdict()
                    if d["prefix"]:
                        prefix = "/{{{prefix}}}".format_map(d)
                prefix_template = Template(prefix)
                assert isinstance(prefix_template, Template)
            else:
                prefix_template = prefix

            self.prefix_template = prefix_template
            self.prefix = prefix

        # super().__init__(*args, **kw)

    def render(self, template=None, **kw):
        template = template or self.prefix_template
        soft(kw, self.__dict__)

        result = template.render(kw)
        return result

    async def main(self):
        "main loop"
        # await super().main()
        await self._start_live()
        while self.state < ST_STOPPED:
            await self._idle()
        await self._stop_live()

    async def _start_live(self):
        log.info("[%s] _start_live", self.uid)

    async def _stop_live(self):
        log.info("[%s] _stop_live", self.uid)

    async def _idle(self, timeout=None):
        # log.debug("[%s] alive", self.uid)
        if timeout is None:
            timeout = self.IDLE_SLEEP
        await asyncio.sleep(timeout)
        if time.time() > self.dead:
            await self._stop()

    async def _stop(self):
        self.state = ST_STOPPED


class Tube(iAgent):
    """Represents the concept of a stream of events that
    can be located by a UID or searching metadata
    """

    uid: UID

    def __init__(
        self,
        uid: UID,
        sources: List[UID],
        broker: Broker,
        storage: Storage,
        meta=None,
        **kw,
    ):
        super().__init__(uid=uid, broker=broker, storage=storage, meta=meta, **kw)
        self.sources = sources
        assert isinstance(self.storage, WaveStorage), "needed for subscriptions"
        # TODO: use regexp and instrospection to subcribe multiples
        # TODO: sources


class App(iAgent):
    "TBD"

    TIME_TO_LIVE = sys.float_info.max

    def __init__(self, uid="app", *args, **kw):
        super().__init__(uid=uid, *args, **kw)
        self.tubes = {}
        self.tasks = {}
        self.loop = None
        self.t0 = 0

    async def _start_live(self):
        assert self.loop is None
        self.loop = asyncio.get_running_loop()
        self.t0 = self.loop.time()

        # start broker and storage
        await self.storage.start()
        await self.broker.start()

        # start tubes
        for uid, tube in self.tubes.items():
            log.info("- starting: [%s]", uid)
            self.tasks[uid] = self.loop.create_task(tube.main(), name=uid)

    async def _stop_live(self):
        # requests fibers to TERM
        for uid, tube in self.tubes.items():
            log.info("- term: [%s]", uid)
            tube.state = ST_STOPPED

        # wait and clear stopped for 5 secs
        t0 = self.loop.time()
        while self.tasks and self.loop.time() - t0 < 5:
            for uid, task in list(self.tasks.items()):
                if task.done():
                    self.tasks.pop(uid)
                    log.info("- end: [%s]", uid)
            await asyncio.sleep(0.5)

        # kill remaining
        for uid, task in self.tasks.items():
            log.info("- kill: [%s]", uid)
            task.cancel()

        # wait and clear stopped for 5 secs
        t0 = self.loop.time()
        while self.tasks and self.loop.time() - t0 < 5:
            for uid, task in list(self.tasks.items()):
                if task.done():
                    self.tasks.pop(uid)
                    log.info("- finished: [%s]", uid)
            await asyncio.sleep(0.5)

        # stop broker and storage
        await self.storage.stop()
        await self.broker.stop()

    def must_stop(self):
        return len(self.tubes) < 1

    def add(self, *tubes):
        for tube in tubes:
            self.tubes[tube.uid] = tube

    def run(self):
        asyncio.run(self.main())

    async def _idle(self):
        await super()._idle()
        if self.must_stop():
            self.state = ST_STOPPED
            log.info("[%s] want stop", self.uid)


ST_INIT = 0
ST_HISTORICAL = 1
ST_SWITCHING = 2
ST_LIVE = 3
ST_STOPPED = 4


class Clock(Tube):
    "A tube that emit a clock tick"

    counter: int

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.counter = 0

    async def _start_live(self):
        await super()._start_live()

    async def _stop_live(self):
        await super()._stop_live()

    async def _idle(self):
        await super()._idle()
        self.counter += 1
        edge = {
            # MONOTONIC_KEY: time.time(),  # TODO: let the storage set this value?
            #'uid': uid,
            "payload": self.counter,
        }
        await self.storage.put(self.uid, edge)


class SwarmTubeException(Exception):
    "base for all SwarmTube Exceptions"


class SkipWave(SwarmTubeException):
    """the item can't be processed but we
    need to advance the Wave to the next one
    """


class RetryWave(SwarmTubeException):
    """the item can't be processed but we
    need to retry later on, so the Wave
    doesn't jump to the next one
    """


class Particle(Tube):
    "TBD"

    MAX_EVENTS = 1024
    # MAX_EVENTS = 32 # TODO: agp: DO NOT COMMIT
    _live = Dict[UID, List[Event]] | None
    _historical = Dict[UID, List[Event]] | None

    RETRY_DELAY = 15
    LIVE_WAITING = 30

    META_KEYS = {
        "tags",
    }

    FUNC_CAST = {
        "datetime": SDATE,
    }

    def __init__(
        self,
        uid: UID,
        sources: List[UID],
        broker: Broker,
        storage: Storage,
        since=None,
        specs=None,
        mapper=None,
        lambda_mapper=None,
        include=None,
        exclude=None,
        drop=None,
        **kw,
    ):
        super().__init__(uid, sources=sources, broker=broker, storage=storage, **kw)
        self.since = since
        self.specs = specs or {}
        self.mapper = mapper
        self.lambda_mapper = lambda_mapper
        self.include = include
        self.exclude = exclude
        self.drop = drop
        self._model = None
        self._wave = {}
        self._live = {}
        self._historical = {}
        self._live_activity = asyncio.Queue()
        self._need_resync = False

        self._milk = set()
        self._fresh = set()
        self._wip_edge = {}

        self._wip_uncompleted = set()

        self.context = {}
        self.context.update(kw)

        self.metrics = Progress(label=self.uid)

        self._mapper = Finder.find_in_memory(
            modules=".",
            klass=Mapper,
            name=self.mapper,
        )
        self._lambda_mapper = Finder.find_in_memory(
            modules=".",
            klass=Mapper,
            name=self.lambda_mapper,
        )
        self._pending_meta = {}

    # --------------------------------------------------------
    # derived methods
    # --------------------------------------------------------
    async def main(self):
        "TBD"
        self._need_resync = True
        # self.metrics.start()
        while self._need_resync:
            self._need_resync = False
            await self._find_sources()

            await self._start_live()
            await self._start_historical()

        log.info("=" * 70)
        log.info("[%s] >> Idle", self.uid)
        log.info("=" * 70)

        context = self.context
        while self.state < ST_STOPPED:
            try:
                # live processing must be based on analyzing
                # the while buffer, not just reacting to a single event
                # (as if we're processing historical data) because
                # it's safer (race-conditions)
                event = await asyncio.wait_for(
                    self._live_activity.get(),
                    timeout=self.LIVE_WAITING,
                )
                # edge = await self.pop_edge(self._live, context)
                async for edge in self.pop_edge(self._live, context):
                    await self.dispatch(edge)
                    # self._wave[_uid] = _wave
            except asyncio.TimeoutError:
                # we only can sent datetime event when live connection
                #  is active, in order not to move forward the crontab
                # cursors and have problems when connection comes back again
                if await self.broker.is_connected():
                    context[DATETIME_KEY] = NOW()
                    self._live_activity.put_nowait(True)
                    # self._milk.clear()

                await self._idle()
                pass  #  No live data has been received
            except Exception as why:
                log.error(why)
                log.error("".join(traceback.format_exception(*sys.exc_info())))

            # self._live_activity.clear()

            self.metrics.update(n=0)

        await self._stop_live()

    async def _find_sources(self):
        """find and expand sources as patterns, allowing regexp
        instead defining each of them
        """
        storage = self.storage.storage

        sources = []
        for uri in self.sources:
            _uri = parse_duri(uri)
            nsdb = "{fscheme}://{host}".format_map(_uri)
            info = await storage.info(nsdb)
            pattern = _uri["_path"]
            # pattern = tf(pattern) # don't use tr() will alter regexp
            pattern = pattern.replace("/", "_")

            for table in info["tables"]:
                if re.match(f"{pattern}$", table):
                    _uri["path"] = f"/{table}"
                    fquid = build_uri(**_uri)
                    sources.append(fquid)

        if sources:
            log.info("source pattern: %s", self.sources)
            log.info("found [%s] sources", len(sources))
            for idx, tubename in enumerate(sources):
                log.info("[%s]: %s", idx, tubename)
        else:
            log.error(
                "can't find any source using these patterns: %s",
                self.sources,
            )
            log.error("exiting, particle will not start")

        self.sources = sources
        for uri in self.sources:
            # TODO: use faster dqueue?
            self._live[uri] = []
            self._historical[uri] = []

    async def _start_live(self):
        "TBD"
        log.info("[%s] ++ Requesting LIVE STREAMING", self.uid)

        for uid in self.sources:
            await self.broker.subscribe(uid, self.live)

    async def _stop_live(self):
        "TBD"
        for uid in self.sources:
            await self.broker.unsubscribe(uid, self.live)

    async def _start_historical(self):
        "TBD"
        self.state = ST_HISTORICAL
        self._wave = await self.storage.last_waves(self.prefix, self.sources, self.uid)
        if self.since is not None:
            wave__ = TO_NS(self.since.timestamp())
            for key in list(self._wave):
                self._wave[key] = wave__

        assert isinstance(self._wave, Dict), "missing await?"

        # self._wave = {uid: _wave for uid in self.sources}

        log.info("-" * 80)
        log.info("[%s] -- Switching to HISTORICAL", self.uid)
        log.info("-" * 80)

        # init feeding variables
        buffer = self._historical
        self._milk.update(self.sources)

        # reset WIP edge variables
        self._new_wip()

        context = self.context

        while self.state < ST_LIVE:
            # for each input source, feed the historical with ALL
            # available data as we can't switch to LIVE streaming
            # until all historical data has been moved to 'live'
            # buffers when WIP edge can't be completed because
            # some sources are missing.

            # the number of data included from storage
            await self._idle(timeout=0)

            n = 0

            self._fresh.clear()
            for uid in list(self._milk):
                stream = await self.storage.storage.since(
                    uid, self._wave[uid], max_results=self.MAX_EVENTS
                )
                if stream:  # is ordeder by MONOTONIC_KEY
                    buffer[uid].extend(stream)
                    m = len(stream)
                    log.debug("[%s] records loaded from: %s", m, uid)
                    n += m
                    self._wave[uid] = extract_wave(stream[-1])
                    self._fresh.add(uid)

                self._milk.remove(uid)
            # self._milk.clear()
            if n == 0:  # no more historical data
                if self.delivery in ("asap",):
                    transfer = list(self._milk)  # TODO: agp: REVIEW (always blank!?)
                else:
                    transfer = list(self._live)

                # move live data to historical and try to continue until
                # we get a state with no more historical data and no more live data
                self.state = ST_SWITCHING
                assert id(buffer) != id(self._live)
                for uid in transfer:
                    _buff = self._live[uid]
                    _hist = self._historical[uid]
                    while True:
                        try:
                            candidate = _buff.pop(0)
                            if candidate[MONOTONIC_KEY] > self._wave[uid]:
                                _hist.append(candidate)
                                n += 1
                            else:
                                # this live event has been captured by historical polling
                                # so is already processed
                                # print(f"*** already processed: --> {candidate}")
                                pass
                        except IndexError:
                            break

                switch = False
                if self.delivery in ("asap",):
                    for _ in self._wip_stream.values():
                        if _:
                            self.state = ST_HISTORICAL
                            break
                    else:
                        switch = True

                elif self.delivery in ("sync",):
                    if n == 0:
                        switch = True

                if switch:  # n == 0:
                    log.info("*" * 80)
                    log.info("[%s] ** Switching to LIVE STREAMING **", self.uid)
                    log.info("*" * 80)
                    self.metrics.update(n=0, force=True)
                    self.state = ST_LIVE
                await asyncio.sleep(1)

            # try to process buffer
            while self.state < ST_LIVE:
                n_edges = 0
                try:
                    async for edge in self.pop_edge(buffer, context):
                        await self.dispatch(edge)
                        n_edges += 1
                except Exception as why:
                    log.error(why)
                    log.error("".join(traceback.format_exception(*sys.exc_info())))

                if not n_edges:
                    if self.state == ST_SWITCHING:
                        break
                    elif self._milk:
                        break  # continue loading more historical
                    else:
                        # edge can't be generated but buffer maybe has data
                        # so we need to continue feeding wip_edge
                        # until an edge is finally fullfiled
                        for uid, _ in buffer.items():
                            # check that we have data to process
                            if not _:
                                self._milk.add(uid)
                        if self._milk:
                            break  # continue loading more historical

            # check if we have an overflow while processing historical data
            if self._need_resync:
                log.info(
                    "[%s] *** ---> Request Stopping Streaming due OVERFLOW",
                    self.uid,
                )
                await self._stop_live()

    def live(self, _uri: UID, event: Dict):
        "TBD"
        uri = _uri["uri"]
        # TODO: REVIEW it looks like is handled at the end as well ...
        if len(self._live[uri]) >= self.MAX_EVENTS:
            self._need_resync = True
            return

        # wave_uri = parse_duri(event['id'])
        if MONOTONIC_KEY not in event:
            m = REG_SPLIT_PATH.match(event["id"])
            if m:
                event[MONOTONIC_KEY] = m.groupdict()["id"]

        self._live[uri].append(event)
        # self._live_activity.put_nowait(event)
        self._live_activity.put_nowait(False)

        if self.state == ST_LIVE:
            pass
        elif len(self._live[uri]) >= self.MAX_EVENTS:
            # request stop streaming and a new re-sync process
            # TODO: REVIEW it looks like is handled at the beginning as well ...
            self._need_resync = True

    # --------------------------------------------------------
    # private own methods
    # --------------------------------------------------------
    def _get_wip_completed_edge(self, buffer, context) -> EDGE:
        if not self._wip_uncompleted:
            tss = []
            for uid, points in self._wip_edge.items():
                tss.extend(
                    [
                        TO_NS(extract_wave(point) or point.get(MONOTONIC_KEY))
                        for point in points
                    ]
                )
            self._wip_edge[MONOTONIC_KEY] = max(tss)
            yield self._wip_edge  # generate a edge

    def _new_wip(self):
        self._wip_edge = {_: [] for _ in self.sources}
        self._wip_uncompleted = set(self.sources)

    def _ordered_streaming(self, buffer):
        """Return a unified ordered stream composed by:
        - wave__
        - source uid
        - single data from source[uid] stream
        """
        unified = []
        for uid, stream in buffer.items():
            stream.sort(key=lambda x: x.get(ID_KEY))
            for data in stream:
                if not (wave__ := data.get(MONOTONIC_KEY)):
                    # get the wave__ from `id` in case of being a tube
                    if not (did := data.get(ID_KEY)):
                        log.error("data doesn't provide wave info [%s]", data)
                        continue
                    _id = parse_duri(did)
                    if wave__ := _id.get(ID_KEY):
                        wave__ = int(wave__)
                    else:
                        log.error("data id: [%s] doesn't provide wave info ", did)
                        continue

                assert wave__
                unified.append((wave__, uid, data))

        unified.sort()
        return unified

    def _wip_add_point(self, uid, point) -> None:
        self._wip_edge[uid].append(point)
        if uid in self._wip_uncompleted:
            self._wip_uncompleted.remove(uid)

    async def _wip_build_point(self, data) -> dict:
        return data

    async def _wip_feed(self, buffer, context):
        """
        TBD
        """
        for wave__, uid, data in self._ordered_streaming(buffer):
            # TODO: remove stream.pop() if we process all the buffers
            # TODO: it'll be faster
            stream = buffer[uid]
            # stream.remove(data)
            _data = stream.pop(0)
            assert id(data) == id(_data)  # TODO: REMOVE check

            point = await self._wip_build_point(data)
            self._wip_add_point(uid, point)
            for edge in self._get_wip_completed_edge(buffer, context):
                yield edge
        else:
            # milk?
            pass

    # --------------------------------------------------------
    # public own methods
    # --------------------------------------------------------
    def _request_update_meta(self, uid, meta):
        self._pending_meta.setdefault(uid, meta)

    async def _flush_meta(self):
        while self._pending_meta:
            uid, meta = self._pending_meta.popitem()
            log.info("Flushing metadata: [%s] -> [%s]", uid, meta)
            await self.storage.update_meta(uid, meta)

        pass

    async def _idle(self, timeout=None):
        await super()._idle(timeout)

        await self._flush_meta()

    async def dispatch(self, edge):
        "TBD"
        ikeys = set(
            [
                k
                for k in edge
                if k.endswith("__") or not isinstance(edge[k], (List, Dict, deque))
            ]
        )
        ekeys = ikeys.symmetric_difference(edge)
        assert ekeys, "no payload in the edge?"

        data = {k: edge[k] for k in ikeys}
        uid_template = Template(self.uid)
        while self.state < ST_STOPPED:
            # log.debug("[%s] -> dispatch", self.uid)
            # log.info("%s", pformat(edge))

            meta = {
                k: self.context[k] for k in self.META_KEYS.intersection(self.context)
            }

            try:
                # do the computation
                # compute must yield data (async and yield)
                async for payload in self._compute(edge, ekeys):
                    # update
                    if payload:
                        # convert using any valid mapper -> model
                        for mapper in self._mapper:
                            try:
                                if item := mapper.pydantic(payload):
                                    payload = item.model_dump()
                                    meta["model"] = mapper.PYDANTIC.__name__

                            except Exception as why:
                                pass

                        # we increment wave to avoid any collision within the same tube
                        data[MONOTONIC_KEY] = (
                            data.get(MONOTONIC_KEY, monotonic_wave()) + 1
                        )
                        data.update(payload)

                        # store results
                        # and shift sync / waves info
                        uid = uid_template.render(**data, **self.__dict__)
                        if self.drop:
                            data = exclude_dict(data, self.drop)
                        await self.storage.put(uid, data)
                        self._request_update_meta(uid, meta)

                    N = sum([len(_) for _ in self._live.values()])
                    self.metrics.update(buffer=N)
                    # log.info("[%s] <- dispatch:", self.uid)
                    # log.info("%s", pformat(data))

                waves = data.get(WAVE_RESUMING_SOURCES)  # Must exist!
                if waves:
                    await self.storage.update_sync_wave(
                        self.prefix,
                        self.sources,
                        self.uid,
                        waves,
                    )
                else:
                    log.error("data %s has no %s key??", data, WAVE_RESUMING_SOURCES)
                break  #  let continue with next wave
            except SkipWave as why:
                # some error is produced, but we want to jump to the next wave
                wave = data.get(MONOTONIC_KEY)  # Must exist!
                if wave:
                    log.debug("Skip wave [%s], reason: %s", wave, why)

                    await self.storage.update_sync_wave(
                        self.prefix,
                        self.sources,
                        self.uid,
                        wave,
                    )
                else:
                    log.error("data %s has no %s key!", data, MONOTONIC_KEY)
                break  #  let continue with next wave
            except RetryWave as why:
                delay = self.RETRY_DELAY
                for msg in why.args:
                    log.debug("Retry wave, reason: %s", msg)
                    if isinstance(msg, dict):
                        delay = msg.get("delay", self.RETRY_DELAY)
                log.warning(
                    "%s._compute() has failed but is needed a retry (%s secs)",
                    str(self),
                    delay,
                )
                await asyncio.sleep(delay)
            except Exception as why:
                log.error(why)
                log.error("".join(traceback.format_exception(*sys.exc_info())))
                delay = self.RETRY_DELAY * 10
                log.warning(
                    "%s._compute() has failed for an UNEXPECTED reason. "
                    "Wave edge can't be moved forward, retry in (%s secs)",
                    str(self),
                    delay,
                )
                await asyncio.sleep(delay)

    async def pop_edge(self, buffer, context):
        """Analyze buffer and return an edge if all data
        is available for processing the next step"""
        # TODO: implement a policy delegation criteria to know when edge is ready to be processed

        # await self._wip_feed(buffer, context)
        async for edge in self._wip_feed(buffer, context):
            self._new_wip()  # that will be lost here

            # avoid sending empty edges
            if all(edge.values()):
                if WAVE_RESUMING_SOURCES not in edge:
                    # we need to provide a MONOTONIC_KEY for each input source
                    # so edge can resume the last step done
                    waves = edge[WAVE_RESUMING_SOURCES] = {}
                    for key, value in walk(edge):
                        _keys = list(flatten(key))
                        if _keys and _keys[-1] in (MONOTONIC_KEY,):
                            _uid = _keys[0]
                            waves[_uid] = max(waves.get(_uid, 0), value)
                    if not waves:
                        log.error("can't find any %s in the edge!", MONOTONIC_KEY)
                        log.error("%s", edge)

                yield edge

    #         # yield None
    #         # check if we must send the WIP edge
    #         if self._wip_uncompleted:
    #             pass
    #         else:
    #             # TODO: agp: REVIEW: is necessary right now? <---
    #             # WIP edge is completed, so return it back and
    #             # reset WIP place holders for the next edge
    #             edge = self._wip_edge  # get a reference
    #             self._new_wip()  # that will be lost here
    #
    #             # avoid sending empty edges
    #             if all(edge.values()):
    #                 if MONOTONIC_KEY not in edge:
    #                     # we need to provide a MONOTONIC_KEY to the edge
    #                     # try to get the minimal wave value from returned
    #                     # egde
    #                     waves = set()
    #                     for key, value in walk(edge):
    #                         if key and key[-1] in (MONOTONIC_KEY,):
    #                             waves.add(value)
    #                     if waves:
    #                         edge[MONOTONIC_KEY] = max(waves)
    #                     else:
    #                         # error
    #                         log.error("can't find any %s in the edge!", MONOTONIC_KEY)
    #                         log.error("%s", edge)
    #
    #                 yield edge

    async def pop_edge_old(self, buffer, context):  # TODO: delete
        """Analyze buffer and return an edge if all data
        is available for processing the next step"""
        # TODO: implement a policy delegation criteria to know when edge is ready to be processed

        await self._wip_feed(buffer, context)
        # check if we must send the WIP edge
        if self._wip_uncompleted:
            pass
        else:
            # WIP edge is completed, so return it back and
            # reset WIP place holders for the next edge
            edge = self._wip_edge  # get a reference
            self._new_wip()  # that will be lost here

            # avoid sending empty edges
            if all(edge.values()):
                if MONOTONIC_KEY not in edge:
                    # we need to provide a MONOTONIC_KEY to the edge
                    # try to get the minimal wave value from returned
                    # egde
                    waves = set()
                    for key, value in walk(edge):
                        if key and key[-1] in (MONOTONIC_KEY,):
                            waves.add(value)
                    if waves:
                        edge[MONOTONIC_KEY] = max(waves)
                    else:
                        # error
                        log.error("can't find any %s in the edge!", MONOTONIC_KEY)
                        log.error("%s", edge)

                return edge

    # --------------------------------------------------------
    # abstract methods
    # --------------------------------------------------------

    async def _compute(self, edge, ekeys):
        """
        Return None if we don't want to store info
        """
        raise NotImplementedError()


class iGeo:
    GEO_CACHE = {}
    MAX_GEO_CACHE = 1000
    GEO_KEYS = set(
        [
            "ubication",
            "location",
            # "geojson",
        ]
    )

    storage: WaveStorage = None

    GEO_URI_TEMPLATE = f"{NAMESPACES.INFRASTRUCTURE.value}://centesimal/{TUBE_SNAPSHOT}"

    def __init__(self, uid, sources, broker, storage, **kw):
        kw.setdefault("geo_uri_template", self.GEO_URI_TEMPLATE),
        # TODO: agp: needed here (specs)
        soft(
            kw.setdefault("specs", {}),
            {
                "__default__": 5,  # None means Default
            },
        )

        super().__init__(uid, sources, broker, storage, **kw)
        self.geo_uri_template = kw["geo_uri_template"]
        self.geo_locator_uri = kw["geo_locator"]
        self._cached_M = {}

    # --------------------------------------------------------
    # private own methods
    # --------------------------------------------------------
    async def _get_geolocation(self, data):
        """
        - build a list of any parameter that indicate geolocations
        - search in cache
        - search into geo table using captured parameter/s

        1. try to find geo using `geo` tube
        2. use another policy

        """
        OPTIONS = set(["geojson", "geometry"])

        async def locate_in_geo_tube(candidates, **params):
            if isinstance(candidates, str):
                candidates = [candidates]
            for query in candidates:
                for geo_info in await self.storage.query(query, **params):
                    # try to find geometry from
                    # TODO: agp: unify
                    for _geo_key in OPTIONS.intersection(geo_info):
                        geo_raw = geo_info[_geo_key]
                        geo_json = to_geojson(geo_raw)
                        return geo_json
                    else:
                        log.error(
                            "can not find geojson form %s using [%s]", geo_info, OPTIONS
                        )

        # 1. try to find geo using `geo` tube
        geo_uri = GeojsonManager.geo_uri(data)
        if not (geo_result := self.GEO_CACHE.get(geo_uri)):
            if geo_json := await locate_in_geo_tube(geo_uri):
                geo_hash__ = geo_uri
                geo_keys__ = ["geojson"]
            elif options := OPTIONS.intersection(data):
                for _geo_key in options:
                    geo_raw = data[_geo_key]
                    geo_json = to_geojson(geo_raw)
                    geo_hash__ = geo_uri
                    geo_keys__ = ["geojson"]
                    break
            else:
                geo_keys__ = self.GEO_KEYS.intersection(data)
                geo_keys__ = list(geo_keys__)
                geo_keys__.sort()

                if not geo_keys__:
                    log.error("can't find geolocation in [%s]", data)

                # try to find the geo of this data
                # using alternative sources in DB
                # by geo_uri_template
                geo_params = {}
                geo_hash__ = []
                for key in geo_keys__:
                    if value := data.get(key):
                        geo_params[key] = value
                # compute a hash for the geo
                geo_hash__ = yaml.dump(geo_params)

                if len(geo_hash__) >= 128:
                    geo_hash__ = hashlib.md5(geo_hash__.encode("utf-8")).hexdigest()
                if not (geo_result := self.GEO_CACHE.get(geo_hash__)):
                    # Note: candidates can be an iterator
                    candidates = [
                        self.geo_uri_template,
                    ]
                    if geo_json := await locate_in_geo_tube(candidates, **geo_params):
                        pass
                    else:
                        log.error(
                            "can not find geo form %s using [%s]",
                            candidates,
                            geo_params,
                        )
                    geo_result = geo_keys__, geo_hash__, geo_json  # TODO: clean code
            geo_result = geo_keys__, geo_hash__, geo_json

            if len(self.GEO_CACHE) > self.MAX_GEO_CACHE:
                self._free_geo_cache()
            # self.GEO_CACHE[geo_hash__] = geo_result
            self.GEO_CACHE[geo_uri] = geo_result

        geo_keys__, geo_hash__, geo_json = geo_result
        data["geo_point__"] = geo_json
        data["geo_keys__"] = geo_keys__
        data["geo_hash__"] = geo_hash__
        return geo_json

    def _free_geo_cache(self):
        keys = list(self.GEO_CACHE)
        random.shuffle(keys)
        for key in list(keys[: self.MAX_GEO_CACHE // 3]):
            self.GEO_CACHE.pop(key)

    def _get_geojson(self, keys):
        for key in flatten(keys):
            if geojson := self.GEO_CACHE.get(key):
                break

            # item = self.geo_locator.grid_to_center_coordinates(key)
            item = self.geo_locator.geokey_to_geojson(key)  # TODO: change name
            # item = self.geo_locator.grid_to_cell(key)
            if item:
                geojson = item.model_dump()
                # geojson = point.coordinates
                self.GEO_CACHE[key] = geojson
                break
        else:
            return tuple(), None
        return key, geojson


CRON_ENUM = {
    "1h": {
        "second": 0,
        "minute": 0,
    },
    "1d": {
        "hour": 0,
        "second": 0,
        "minute": 0,
    },
}


class XBase(iGeo, Particle):
    "TBD"

    DATETIME = ["datetime", MONOTONIC_KEY]  # the ts used for cutting by time boundary
    DEFAULT_TARGET = "{{ uid }}:{{ name }}"
    EXCLUDE = f"id$|{REG_PRIVATE_KEY}"
    FULL_EXCLUDE = f"{EXCLUDE}|datetime"
    IDS_KEYS = set([ID_KEY, ORG_KEY])
    OPERATORS = {  # TODO: REMOVE?
        "max": max,
        "min": min,
        "sum": operator.add,
        "freq": None,
        "copy": None,
        "average": None,
    }
    REG_EXCLUDE_TWICE = re.compile(f".*_({'|'.join(OPERATORS)})_(value|datetime)$")

    KEY_PRIORITY = {  # TODO: use definitions
        "datetime": 0,
        "geo_key_hash__": 1,
        "name": 2,
    }

    def __init__(self, uid, sources, broker, storage, **kw):
        overlap(kw, {"cron": "1h"})

        overlap(
            kw,
            {
                "geo_locator": GEO_FILTER_DEFAULT_GRID_MAD_ID,
                # "extract": [
                #     "value_values.value",
                #     "datetime",
                #     "measure",
                # ],
                "function": "copy",
                "target": self.DEFAULT_TARGET,
                "use_centroid": True,
            },
        )
        complete_on(
            kw,
            "group_by",
            [
                "datetime",
                "geo_key_hash",
            ],
            where="begin",
        )
        kw.setdefault("drop_temp", True)
        # complete_on(
        #     kw,
        #     "extract",  # TODO: 'extract' is used?
        #     [
        #         "datetime",
        #     ],
        #     where="middle",
        # )
        overlap(
            kw,
            {
                "drop": {
                    ".*": "None",
                },
            },
        )
        overlap(
            kw,
            {"delivery": "asap"},
        )
        super().__init__(uid, sources, broker, storage, **kw)

        time_group = kw["cron"]
        # self.cron = {_: Crontab(**cron) for _ in sources}
        if isinstance(time_group, str):
            cron = CRON_ENUM.get(time_group) or CRON_ENUM["1h"]
        else:
            time_group, cron = "custom", time_group

        self.time_group = time_group
        self.cron = Crontab(**cron)

        self.group_by = kw.get("group_by") or []
        self.extract = complete(kw.get("extract", ""), [])
        self.use_centroid = kw.get("use_centroid")
        self.drop_temp = kw.get("drop_temp")

        self._last_output = {}
        self._wip_cursor = {}
        self._wip_stream = {_: {} for _ in sources}
        # self._wip_stream = {}
        self._wip_known_keys = {_: set() for _ in sources}

        self.delivery = kw.get("delivery", "asap")

        # geolocation
        self.geo_locator = GeoFactory.get_locator(self.geo_locator_uri)
        foo = 1

    async def _wip_feed(self, buffer, context):
        """
        We can process buffers in the same way for historical
        data or streaming data as wip internal structure must
        be filled in any order.

        Particle need to wait until some criteria is reached
        and we can compute all defined stats and interpolate
        values in the time-mark defined by "cron" specs, etc
        depending on the XParticle sub-classing.

        What is true, is every data used must be retired from
        buffers, but we can process buffers in any "uid" order.

        Then, cleaning process due by "_new_wip" may keep some
        data for the next cycle, but it's depends on what type
        of interpolation methods are we using.

        - explore _wip_uncompleted signals
        - reach a point where we can stop getting more data from this signal
        - this depends on the interpolation method that we're using
        - remove from _wip_uncompleted
        - continue until all signal are ready (not _wip_uncompleted)
        - do the stats computation within the period t0->t1
        - compute interpolated values in t1
        - clean and do a step forward (_new_wip)

        """
        # for wave__, uid, data in self._ordered_streaming(buffer):
        for uid, stream in buffer.items():
            for data in stream:
                if wdata := await self._wip_build_walk(data):
                    self._wip_add_wdata(uid, wdata)
                # TODO: debug, simulate live streaming
                # if False and random.random() < 0.10:
                #     break
            stream.clear()
        # we've classify all data to determine the logic of
        # the particle, so let's try to update the wip edge
        # with this new data, whatever this means for the subclass
        for edge in self._get_wip_completed_edge(buffer, context):
            yield edge
            # self._push_wip_edge(edge)

    async def _wip_build_walk(self, data) -> List:
        """Try to create a rich data 'point' analyzing the internal
        structure of a single data that comes from stream.

        - enchance with geo location
        - TBD

        """
        # enhance with geo location
        # ignore value when gelocation doesn't belongs to a geodefinition
        # i.e. outside any district using RegionDefinition
        # enhance with geo location
        if await self._get_geolocation(data):
            wdata = Walk(data)
            info = {
                # TODO: agp: REVIEW?
                # TODO: agp: use kw["extract"]
                # TODO: agp, get from Particle definition
                "measure": "value",
            }
            new = wdata.restruct(info)
            for lambda_mapper in self._lambda_mapper:
                mapping_keys = lambda_mapper.mapping_keys({}, only_defined=False)
                for key, value in new.items():
                    if attr := mapping_keys.get(key):
                        wdata.winsert(attr, value)
                        wdata.wpop(key)

            return wdata
        else:
            log.debug("Ignoring measure because is outside of geolocator")

    def _wip_add_wdata(self, uid, wdata: Walk) -> None:
        """
        This method organize the data points in a structure
        that can collect all the data no matter is they comes
        in a structured way or not.

        The structure is drived by the 'structure_values'
        and data is sorted by 'datetime' to be processed in order.
        """
        # filters
        if self.include:
            if not (sub := wdata.rget(self.include)):
                return

        if self.exclude:
            if sub := wdata.rget(self.exclude):
                return

        candidates = wdata.rget(self.group_by)
        keys = list([_ for _ in candidates if hasattr(candidates[_], "__hash__")])
        keys.sort(key=lambda x: self.KEY_PRIORITY.get(x, 1000))

        # holder_key = tuple([tuple([candidates[_] for _ in keys]), uid])
        holder_key = tuple(flatten([candidates[_] for _ in keys]))
        stream = self._wip_stream[uid]

        if (wcurrent := stream.get(holder_key)) is None:
            stream[holder_key] = wdata
        else:
            wcurrent.wupdate(wdata)

    def _get_wip_completed_edge(self, buffer, context) -> EDGE:
        """
        1. find the next time mark (t0) from the 1st data received
        2. t0 > datetime of 1st data point
        3. create a record for each different data point in order to check
        4. add this signal to pending ones
        5. update lower bound_t0, t0, upper bound_t1
         . loop for getting more data
         . update the record
        6. check if record has cross t0 limit
        7. is eligible for interpolating in t0
        8. remove this signal from pending
        9. when no more pending signals are waiting to complete, we can generate an edge
        10. if we receive a point over t1, the we force all pending signals to be part
            of the edge despite we've no data that have crossed the t0 line

        """
        # request current cursors extistence

        # don't assume the data is going to be continous with GAPS smaller that boundary

        self._wip_cursor.clear()

        for uid in self._wip_known_keys:
            if not (self._wip_cursor.get(uid)):
                if interval := self._find_bound_interval(uid):
                    self._wip_cursor[uid] = interval
                    log.debug("[%s] for [%s]", self._wip_cursor[uid], uid)
                    self._wip_uncompleted.add(uid)
                elif self.delivery in ("sync",):
                    log.info(
                        "Input sources are exhausted, we need to wait until more data is comming"
                    )
                    return

        if not self._wip_cursor:
            log.debug("Can not find any boudaries to set the cursor, we need more data")
            return

        if self.delivery in ("asap",):
            min_requiered_key = min(self._wip_cursor.values())
        elif self.delivery in ("sync",):
            min_requiered_key = max(self._wip_cursor.values())
        else:
            log.warning(f"Policy: [%s] is unknown. Using 'asap' as fallback")
            min_requiered_key = max(self._wip_cursor.values())

        # check which sources are ready to be sent
        for dt0 in flatten(min_requiered_key):
            break

        ready2send = []
        for uid, interval in self._wip_cursor.items():
            for dt in flatten(interval):
                if dt == dt0:
                    ready2send.append(uid)
                break

        # check all cursors are ready to compute
        # TODO: remove
        if self.delivery in ("sync", "asap") and all(self._wip_cursor):
            # self._milk.clear()
            # min_requiered_key = max(self._wip_cursor.values())
            log.debug("[%s] is the candidate interval for computing", min_requiered_key)

            for uid, stream in self._wip_stream.items():
                if uid not in self._wip_uncompleted:
                    continue

                holder_keys = list(stream)
                holder_keys.sort()

                # clean records that can not be used due incompleted boundary-time
                drop = False
                for key in holder_keys:
                    if key < min_requiered_key[0]:
                        stream.pop(key)
                        drop = True
                    else:
                        break

                if not holder_keys or holder_keys[-1] < min_requiered_key[-1]:
                    self._milk.add(uid)
                    log.debug("request data for [%s]", uid)
                else:
                    if drop:
                        log.debug(
                            "[%s] has drop some values that can't be used for computing",
                            uid,
                        )

                    log.debug("[%s] is ready to compute", uid)
                    self._wip_cursor[uid] = self._find_bound_interval(uid)
                    log.debug("[%s] for [%s]", self._wip_cursor[uid], uid)
                    self._wip_uncompleted.add(uid)

            # now, all stream has been revised and _milk may have some requests

            if self.delivery in ("asap",):
                if self._fresh.intersection(self._milk):
                    log.debug(
                        "Policy: [%s] we need fill all buffers for [%s] to start computing",
                        self.delivery,
                        min_requiered_key,
                    )
                    return
            elif self.delivery in ("sync",):
                if self._milk:
                    log.debug(
                        "Policy: [%s] we need fill all buffers for [%s] to start computing",
                        self.delivery,
                        min_requiered_key,
                    )
                    return

        # now we can generate the edge
        # from keys between cursor[min][max]
        # min_requiered_key = max(self._wip_cursor.values())

        wave_resuming_sources = {}
        edge = {
            WAVE_RESUMING_SOURCES: wave_resuming_sources,
        }

        WAVE_KEY = (MONOTONIC_KEY,)
        for uid in ready2send:
            stream = self._wip_stream[uid]
            if stream:
                # = (k0, k1) = self._find_bound_interval(uid)
                (k0, k1) = self._wip_cursor[uid]

                tbound = k1[0]
                edge[uid] = partial = []

                # sort the keys, so we deliver them in order to the upper level
                keys = list(stream)
                keys.sort()
                for key in keys:
                    if key[0] < tbound:
                        # retire an item from _wip_stream
                        # we need to get the wave of this data in order to update
                        # particles resuming info
                        wdata = stream.pop(key)
                        wave_resuming_sources[uid] = wdata[WAVE_KEY]

                        # include in partial dataset
                        group_keys = key[1:]
                        partial.append(((tbound, group_keys), wdata))
                    else:
                        log.debug("skipping data from [%s] until found [%s]", uid, key)
                        break
                else:
                    log.error(
                        "you never must reach this line, data must cross datetime boundaries!!"
                    )
            else:
                log.error(
                    "you never must reach this line, buffers must be full filled before computing!"
                )

        # set boundary datetime

        for t1 in flatten(k1):
            edge.update(
                {
                    # MONOTONIC_KEY: TO_NS(t1),
                    # "datetime": TO_NS(t1),  # TODO: use datetime here for a wave?
                    "datetime": t1,
                }
            )
            log.debug("yield edge: datetime: %s", t1)
            for uid in self._wip_known_keys:
                log.debug("- %s datapoints for [%s]:", len(edge.get(uid, [])), uid)
            break

        yield edge
        self._wip_cursor.clear()
        foo = 1

    # --------------------------------------------------------
    # public own methods
    # --------------------------------------------------------
    def _find_bound_interval(self, uid):
        if uid_holder := self._wip_stream[uid]:
            known_idt = list(uid_holder)
            known_idt.sort()
            if len(known_idt) > 1:
                key0 = known_idt[0]
                key1 = known_idt[-1]
                return key0, key1  # TODO: agp: Review TZ / UTC

    #             # use LOCAL_TZ for cron
    #
    #             # now_local = datetime.now(LOCAL_TZ)
    #             # now_utc = datetime.now(pytz.utc)
    #             # delta = now_local - now_utc
    #
    #             # idt0 = idt0.astimezone(LOCAL_TZ)
    #             # idt0 = idt0 - delta
    #             _key0 = Walk(key0)
    #
    #             for idt0 in flatten(key0):
    #                 t1 = self.cron.next_ts(idt0)
    #                 t2 = self.cron.next_ts(t1)
    #                 t0 = t1 - (t2 - t1)
    #
    #                 for k, v in _key0.items():
    #                     if v == idt0:
    #                         if isinstance(idt0, str):
    #                             t0 = SDATE(t0)
    #                         _key0[k] = SDATE(t0)
    #                         key0 = _key0.rebuild(use_ordered=False)
    #
    #                         _key0[k] = SDATE(t1)
    #                         key1 = _key0.rebuild(use_ordered=False)
    #                         return key0, key1

    async def _get_geolocation(self, data):
        """TBD"""

        # generic part for getting the geo_json
        geo_json = await super()._get_geolocation(data)

        # get the geo_key from user geo_locator defined in Particle JSON definition
        geo_key_values = (
            self.geo_locator.coordinates_to_geokey(geo_json.coordinates, **data) or []
        )

        # compute geo_key_hash
        data["geo_key_values__"] = geo_key_values
        keys = list(geo_key_values)
        keys.sort()
        geo_key_hash__ = tuple([geo_key_values[_] for _ in keys])

        # add this geojson to cache
        if not self.GEO_CACHE.get(geo_key_hash__):
            self.GEO_CACHE[geo_key_hash__] = geo_json
            for _ in flatten(geo_key_hash__):
                self.GEO_CACHE[_] = geo_json

        # enhance data item
        data["group_by__"] = data["geo_key_hash__"] = geo_key_hash__

        return geo_json


def pickle_cloner(wdata: Walk, lambda_name: str):
    return pickle.loads(pickle.dumps(wdata))


class XParticle(XBase):
    "TBD: extended particle"

    DATETIME = ["datetime", MONOTONIC_KEY]  # the ts used for cutting by time boundary
    DEFAULT_TARGET = "{{ uid }}:{{ name }}"
    EXCLUDE = f"id$|{REG_PRIVATE_KEY}"
    FULL_EXCLUDE = f"{EXCLUDE}|datetime"
    IDS_KEYS = set([ID_KEY, ORG_KEY])

    # # TODO: REMOVE?
    OPERATORS = {
        **XBase.OPERATORS,
        # "average": None,
        # "max": max,
        # "min": min,
        # "sum": operator.add,
        # "freq": None,
        # "copy": None,
    }
    CLONER = {}
    REG_EXCLUDE_TWICE = re.compile(f".*_({'|'.join(OPERATORS)})_(value|datetime)$")

    def __init__(self, uid, sources, broker, storage, **kw):
        # complete_on(
        #     kw,
        #     "group_by",
        #     [
        #         "datetime",
        #     ],
        #     where="begin",
        # )
        complete_on(
            kw,
            "lambda_exclude",
            [
                REG_PRIVATE_KEY,
                # self.REG_EXCLUDE_TWICE,
                r"\d+",
            ],
            where="end",
        )
        super().__init__(uid, sources, broker, storage, **kw)

        self._dt_idx = index(self.group_by, "datetime")

        self._key_idx = {}  # for optional data re-arrange

        # set the lambda method
        self.lambda_exclude = kw["lambda_exclude"] or ""
        self.lambda_exclude = "|".join(self.lambda_exclude)
        func_names = kw["function"] or "average"  # TODO: use define
        self._lambdas = {}
        self._lambdas_cache = {}

        self.available_lambdas = set()
        for lambda_name in re.findall(r"\w+", func_names):
            for prefix in "pre", "post":
                self._lambdas.setdefault(prefix, {})
                func = getattr(self, f"_{prefix}_{lambda_name}", None)
                if func:
                    # setattr(self, "_calc", func)
                    self._lambdas[prefix][lambda_name] = func
                    self.available_lambdas.add(lambda_name)

        if forbidden := self.available_lambdas.difference(self.OPERATORS):
            if len(self.available_lambdas) > len(forbidden):
                msg = f"you can't mix: {forbidden} lambas with {self.available_lambdas.difference(forbidden)} in a XParticle derived classes ({self.__class__})"
                log.error(msg)
                raise RuntimeError(msg)
        self._tmp_value = {}
        self.CLONER["peak"] = self.floatwhen_cloner

    # --------------------------------------------------------
    # lambda methods
    # --------------------------------------------------------
    def _lambda_max(self, current, value, key):
        if not isinstance(current, FloatWhen):
            current = FloatWhen(current, self.context["datetime"])

        if current.value < value:
            current = FloatWhen(value, self.context["datetime"])

        return current

    def _lambda_min(self, current, value, key):
        if not isinstance(current, FloatWhen):
            current = FloatWhen(current, self.context["datetime"])

        if current.value > value:
            current = FloatWhen(value, self.context["datetime"])

        return current

    def _lambda_average(self, current, value, key):
        attr = key[-1]
        M = self._cached_M.get(attr) or self._find_M(attr)
        return current + (value - current) / M

    def _lambda_sum(self, current, value, key):
        current += value
        return current

    def _lambda_freq(self, current, value, key):
        if isinstance(current, list):
            current.append(value)
        else:
            current = [current, value]
        return current

    def _lambda_peak(self, current, value, key):
        if isinstance(current, list):
            current.append(value)
        else:
            current = [current, value]
        return current

    def _pre_lambda(self, old_value: Walk, new_value: Walk, op, lambda_name):
        # reg1 = re.compile(f".*_(?!{lambda_name})_(value|datetime)$")
        for key, value in new_value.ordered:
            # TODO: bool is an `int`, so enter here ...
            if isinstance(value, (int, float, FloatWhen)):
                key1 = str(key[-1])
                # keyS = str(key)
                for _ in key:
                    if re.match(REG_PRIVATE_KEY, str(_)):
                        break
                else:
                    if not (re.match(self.lambda_exclude, key1)):
                        # chec not doing different lambdas twice
                        if m := self.REG_EXCLUDE_TWICE.match(key1):
                            if m.group(1) != lambda_name:
                                continue

                    if (current := old_value.get(key)) is None:
                        old_value.winsert(key, value)
                    else:
                        old_value[key] = op(current, value, key)

        return old_value

        # if cache := self._lambdas_cache:
        #     for key in cache.intersection(new_value):
        #         value = new_value[key]
        #         if (current := old_value.get(key)) is None:
        #             old_value.winsert(key, value)
        #         else:
        #             old_value[key] = op(current, value, key)
        # else:
        #     cache = self._lambdas_cache = set()
        #     for key, value in new_value.ordered:
        #         if isinstance(value, (int, float, FloatWhen)) and not (
        #             re.match(self.lambda_exclude, str(key[-1]))
        #         ):
        #             cache.add(key)
        #             if (current := old_value.get(key)) is None:
        #                 old_value.winsert(key, value)
        #             else:
        #                 old_value[key] = op(current, value, key)

        # return old_value

    def _pre_peak(self, old_value, new_value, lambda_name):
        op = self._lambda_peak
        # reg1 = re.compile(f".*_(?!{lambda_name})_(value|datetime)$")
        for key, value in new_value.ordered:
            # TODO: bool is an `int`, so enter here ...
            if isinstance(value, (int, float, FloatWhen)):
                key1 = str(key[-1])
                # keyS = str(key)
                for _ in key:
                    if re.match(REG_PRIVATE_KEY, _):
                        break
                else:
                    if not (re.match(self.lambda_exclude, key1)):
                        # chec not doing different lambdas twice
                        if m := self.REG_EXCLUDE_TWICE.match(key1):
                            if m.group(1) != lambda_name:
                                continue

                    if isinstance(value, (int, float)):
                        value = FloatWhen(value, new_value[("datetime",)])

                    if (current := old_value.get(key)) is None:
                        old_value.winsert(key, value)
                    else:
                        assert isinstance(current, (FloatWhen, list))
                        assert isinstance(value, FloatWhen)
                        old_value[key] = op(current, value, key)

        return old_value

    def _pre_max(self, old_value, new_value, lambda_name):
        return self._pre_lambda(old_value, new_value, self._lambda_max, lambda_name)

    def _pre_min(self, old_value, new_value, lambda_name):
        return self._pre_lambda(old_value, new_value, self._lambda_min, lambda_name)

    def _pre_average(self, old_value, new_value, lambda_name):
        return self._pre_lambda(old_value, new_value, self._lambda_average, lambda_name)

    def _pre_copy(self, old_value, new_value, lambda_name):
        return self._pre_average(old_value, new_value, lambda_name)

    def _pre_freq(self, old_value, new_value, lambda_name):
        return self._pre_lambda(old_value, new_value, self._lambda_freq, lambda_name)

    def _pre_sum(self, old_value, new_value, lambda_name):
        return self._pre_lambda(old_value, new_value, self._lambda_sum, lambda_name)

    def _post_freq(self, keys, lambda_name, wdata: Walk):
        """
        create historogram and get the middle point of the max frequency
        """
        assert isinstance(wdata, Walk)

        samples = {}
        for key, value in wdata.ordered:
            if isinstance(value, (int, float)) and not (
                re.match(self.lambda_exclude, str(key[-1]))
            ):
                # cache.add(key)
                current = wdata[key]  # must exists
                if isinstance(current, list):
                    samples[key] = current

        # samples: Dict = values.setdefault("freq", {})
        # for attr, samples in list(aux.items()):
        #     df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in samples.items()]))

        df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in samples.items()]))
        for col_name in df.columns:
            col = df[col_name]

            M = max(col.size // 10, 5)
            df2 = pd.cut(col, bins=M).value_counts()
            idx = df2.idxmax()
            wdata[col_name] = idx.mid

        return wdata

    def _post_peak(self, keys, lambda_name, wdata: Walk):
        """
        TBD
        """
        assert isinstance(wdata, Walk)

        # build the sample data
        samples = {}
        keywords = self.specs.get("keywords", [".*"])
        pattern = "|".join(keywords)
        for key, value in wdata.ordered:
            if key:
                skey = str(key[-1])
                if not (re.match(self.lambda_exclude, skey)):
                    if re.match(pattern, skey):
                        # cache.add(key)
                        current = wdata[key]  # must exists
                        if isinstance(current, list):
                            samples[key] = current
                        elif isinstance(current, FloatWhen):
                            samples[key] = [current]
                    # drop this key as is not used for computing
                    # of must be only inserted when a peak is detected
                    wdata.pop(key)

        # Find peaks
        # TODO: use pandas and nd and solve the problems with scipy.find_peaks
        # TODO: when array have only 2 values (can't find a middle point)

        def find_peaks(data):
            if len(data) > 1:
                last = data[0]
                for new in data[1:]:

                    if last > new:
                        yield last
                    last = new

        existing = self._tmp_value.setdefault("peak", {})

        # peaks will provide data using other datetime, not the boundary
        # so we can drop them and insert just the peak in the right datetime
        self._last_output[keys].pop(lambda_name, None)
        peaks_found = False
        for col_name, data in samples.items():

            if (last_value := existing.get(col_name)) is not None:
                col = [last_value] + data
            else:
                col = data

            # TODO: delete sort (confirm that is not neccesary)
            col.sort(key=lambda x: x[-1])

            for peak in find_peaks(col):
                # peaks_found = True
                # we need to allocate each peak found in the self._last_output
                # TODO: use define or normalization / defines / search wher datetime is
                # TODO: delete all non-relevant data from wdata and let only the pean value
                wdata[col_name] = peak[0]
                wdata[("datetime",)] = peak[1]

                _keys = (peak[1], *keys[1:])
                holder = self._last_output.setdefault(_keys, {})
                holder[lambda_name] = pickle.loads(pickle.dumps(wdata))

            if col:
                self._tmp_value.setdefault(lambda_name, {})[col_name] = col[-1:][0]

        # if peaks_found:
        #     return wdata

    def _pre_toggle(self, key, old_value, new_value, edge):
        raise NotImplementedError()

    # --------------------------------------------------------
    # derived methods
    # --------------------------------------------------------
    def _find_bound_interval(self, uid):
        if uid_holder := self._wip_stream[uid]:
            known_idt = list(uid_holder)
            known_idt.sort()
            for key0 in known_idt:
                # use LOCAL_TZ for cron
                # now_local = datetime.now(LOCAL_TZ)
                # now_utc = datetime.now(pytz.utc)
                # delta = now_local - now_utc

                # idt0 = idt0.astimezone(LOCAL_TZ)
                # idt0 = idt0 - delta
                _key0 = Walk(key0)
                for idt0 in flatten(key0):
                    try:
                        t1 = self.cron.next_ts(idt0)
                        t2 = self.cron.next_ts(t1)
                        t0 = t1 - (t2 - t1)
                    except Exception as why:
                        log.warning("data hasn't datetime??")
                        log.warning("%s", uid_holder[key0])
                        log.warning("ignoring tis data and continue with next one")
                        uid_holder.pop(key0, None)
                        break

                    for k, v in _key0.items():
                        if v == idt0:
                            if isinstance(idt0, str):
                                t0 = SDATE(t0)
                            _key0[k] = SDATE(t0)
                            key0 = _key0.rebuild(use_ordered=False)

                            _key0[k] = SDATE(t1)
                            key1 = _key0.rebuild(use_ordered=False)
                            return key0, key1
                    else:
                        log.warning("can not found datetime info to build the interval")

    def _new_wip(self):
        super()._new_wip()
        self._last_output = {}
        for _ in self.sources:
            # self._wip_stream.setdefault(_, {})
            self._wip_edge = []

        # self._wip_uncompleted = set(self.sources)

    def _wip_add_point(self, uid, point) -> None:
        """
        This method organize the data points in a structure
        that can collect all the data no matter is they comes
        in a structured way or not.

        The structure is drived by the 'structure_values'
        and data is sorted by 'datetime' to be processed in order.
        """

        # collect all different structural values
        holder_key = point["structure_values"]
        self._wip_known_keys[uid].add(holder_key)  # TODO: is used?

        # find interpolation datetime
        # "datetime" is expected to be in data point
        dt = point["datetime"]  # TODO: used define

        # find the holder for this uid and iterpolation time
        # we allocate all related data within its interpolation slot
        uid_holder = self._wip_stream[uid]
        interpolation_holder = uid_holder.setdefault(dt, {})

        # use a list to sort the point received
        last_holder = interpolation_holder.setdefault(holder_key, [])
        # insert backwards
        for idx in range(len(last_holder), 0, -1):
            if last_holder[idx - 1]["datetime"] < dt:
                last_holder.insert(idx, point)
                break
        else:
            last_holder.append(point)
            # idx = 0

    async def _wip_build_point(self, data) -> dict:  # TODO: delete?
        """Try to create a rich data 'point' analyzing the internal
        structure of a single data that comes from stream.

        - enchance with geo location
        - guess which keys are 'structural' keys and the pure data key
        - build the unified data point.

        The data point provide some analyzed data that other may used:
        - values and its keys
        - group_by__
        - the unmodified data
        - etc

        """
        # enhance with geo location
        await self._get_geolocation(data)
        if group_by := data.pop("group_by__", None):
            # guess which keys are 'structural' keys and the pure data key
            keys, data_keys = await self._wip_get_data_keys(data)

            # TODO: agp: use defines, not literals here: 'structure_keys', ...
            point = {}
            point["keys"] = keys
            point["value_keys"] = data_keys

            structure_keys = list(keys.difference(data_keys))
            structure_keys.sort()
            structure_values = tuple([data[_] for _ in structure_keys])
            data_values = {_: data[_] for _ in data_keys}

            point["structure_keys"] = structure_keys
            point["structure_values"] = structure_values
            point["value_values"] = data_values
            point["org"] = data
            point["group_by__"] = group_by

            # TODO: use cache
            for k in self.DATETIME:
                if k in data:
                    # use a coherent datetime no matter the source
                    point["datetime"] = DATE(data[k])  # TODO: used define
                    break
            else:
                log.error("can't find a datetime key from %s candidates", self.DATETIME)

            point[MONOTONIC_KEY] = data.get(MONOTONIC_KEY)

            return point

    def _find_M(self, key):
        skey = str(key)
        for pattern, M in self.specs.items():
            if pattern:
                if re.match(pattern, skey):
                    self._cached_M[key] = M
                    break
        else:
            # get default value (key = "")
            self._cached_M[key] = M = self.specs.get("__default__")

        return M

    async def _wip_get_data_keys(self, data):
        """"""
        _keys = list(self.group_by) + [
            _ for _ in data if not re.match(self.FULL_EXCLUDE, _)
        ]

        keys = []
        data_keys = []
        for key in _keys:
            if key in data:
                value = data[key]
                if isinstance(value, (int, float, str)):
                    if key not in keys:
                        keys.append(key)
                        if isinstance(value, (int, float)) or isinstance(
                            DATE(value), datetime
                        ):
                            data_keys.append(key)

        # data_keys = set([_ for _ in keys if isinstance(data[_], (int, float))])

        return set(keys), set(data_keys)

    # --------------------------------------------------------
    # temporal ...
    # --------------------------------------------------------
    @classmethod
    def _geokey_to_id(self, key):
        seq = []
        for x in key:
            if isinstance(x, (int, float)):
                seq.append(f"p{x}" if x >= 0 else f"n{-x}")
            else:
                seq.append(str(x))
        seq = "".join(seq)
        return seq

    def build_output(self):

        for keys, data in self._last_output.items():
            if not data:
                continue
            _geokey, _geojson = self._get_geojson(keys)
            if not _geojson:
                log.warning("Skip data because hasn't gelocation [%s]", data)
                continue
            if self.use_centroid:
                geojson = GeojsonManager.centroid(_geojson)
            geojson = geojson.model_dump()

            id_by_geo = self._geokey_to_id(_geokey)
            # fquid = self.prefix_template.render({"id": id_by_geo})
            fquid = id_by_geo
            out = {
                **data,
                **{
                    "geojson": geojson,
                    "id": fquid,
                    "geokey": id_by_geo,
                    # "id": id_by_geo,
                },
            }
            yield out

    def group_edge(self, edge, ekeys, selector, group_by, extract):
        """
        we can group data by:

        *: <geo_key_hash__>, <value_values>

        """
        self._key_idx = {}
        for stream in glom(edge, selector):
            for item in stream:
                # log.info(item)
                # keys = tuple(collect(item, group_by, -1, flat=True)) #
                skip = False
                keys = []
                for topic, key, value in collect(item, group_by, -1, flat=True):
                    _filter = group_by[topic]
                    if not re.match(_filter, str(value)):
                        skip = True
                        break
                    self._key_idx[key] = len(keys)
                    keys.append(value)
                if skip:
                    continue
                keys = tuple(keys)

                if extract:
                    new_item = [
                        value
                        for (topic, key, value) in collect(item, extract, cast=SDATE)
                    ]
                yield keys, new_item

    def _reindex(self, keys, new_values, axe):
        if idx := self._key_idx.get(axe):
            keys = list(keys)
            axe_value = keys.pop(idx)
            return tuple(keys), {axe_value: new_values}

        return keys, new_values

    def floatwhen_cloner(self, wdata: Walk, lambda_name: str):
        new_value = pickle_cloner(wdata, lambda_name)
        for key, value in new_value.ordered:
            if isinstance(
                value,
                (
                    int,
                    float,
                ),
            ):
                key1 = str(key[-1])
                for _ in key:
                    if re.match(REG_PRIVATE_KEY, _):
                        break
                else:
                    if not (re.match(self.lambda_exclude, key1)):
                        # chec not doing different lambdas twice
                        if m := self.REG_EXCLUDE_TWICE.match(key1):
                            if m.group(1) != lambda_name:
                                continue

                    if isinstance(value, (int, float)):
                        new_value[key] = FloatWhen(value, new_value[("datetime",)])

        return new_value

    async def _compute(self, edge, ekeys):
        """By default compute the average of similar values

        we can group data by:

        *: <geo_key_hash__>, <value_values>

        universe: a sequence of <group_by>: <extract> items
        """
        for stage in [
            "pre",
        ]:
            lambdas = self._lambdas.setdefault(stage, {})
            for lambda_name, func in lambdas.items():
                for uid in ekeys:
                    stream = edge[uid]
                    for keys, new_values in stream:
                        # TODO: determine when delete lambda cache
                        # TODO: use a cache for each uid
                        # TODO: reset cache when internal wdata struct varies
                        # if uid != last_uid or last_struct != len(new_values):
                        #     self._lambdas_cache.clear()
                        #     last_uid = uid
                        #     last_struct = len(new_values)
                        # TODO: use geokey from keys
                        dt, group_keys = keys
                        self.context["datetime"] = dt
                        self.context["group_keys"] = group_keys
                        old_values = self._last_output.setdefault(keys, {})
                        if old := old_values.get(lambda_name):
                            func(old, new_values, lambda_name)
                        else:
                            cloner = self.CLONER.get(lambda_name, pickle_cloner)
                            old_values[lambda_name] = cloner(new_values, lambda_name)

        # apply post-actions
        for stage in ["post", "final"]:
            lambdas = self._lambdas.setdefault(stage, {})

            for keys, results in list(self._last_output.items()):
                for lambda_name in set(results).intersection(lambdas):
                    # TODO: use lambda cache as well
                    func = lambdas[lambda_name]

                    wdata = results[lambda_name]
                    if (_value := func(keys, lambda_name, wdata)) is None:
                        results.pop(lambda_name, None)
                    else:
                        results[lambda_name] = _value

        # rebuild the all results with the computed values
        for keys, results in self._last_output.items():
            for lambda_name in results:
                wdata = results[lambda_name]
                struct = wdata.rebuild(use_ordered=False)
                results[lambda_name] = struct

        # transform data to be delivered
        # stamp edge meta info in payload
        # non_edge_keys = set(edge).difference(ekeys)
        # edge_meta = {_: edge[_] for _ in non_edge_keys}

        # allow to have individual waves when saving in storage
        # edge_meta[MONOTONIC_KEY] = monotonic_wave()
        edge_meta = {
            _: self.FUNC_CAST[_](edge[_])
            for _ in set(self.FUNC_CAST).intersection(edge)
        }

        for payload in self.build_output():
            payload.update(edge_meta)
            yield payload

    async def _compute_old(self, edge, ekeys):
        """By default compute the average of similar values

        we can group data by:

        *: <geo_key_hash__>, <value_values>

        universe: a sequence of <group_by>: <extract> items
        """
        universe = self.group_edge(
            edge,
            ekeys,
            selector=(
                "*.*",
                Flatten(),
            ),
            # group_by=["org.geokey|org.geo_key_hash__", "org.measure"], # TODO: generalize
            group_by=self.group_by,
            # extract=["value_values.value", ("datetime", str)],
            # extract=["value_values", ("datetime", str)],
            extract=self.extract,
        )

        universe = list(universe)  # TODO: agp: NOT COMMIT: delete, just debug...

        # pre
        lambdas = self._lambdas.setdefault("pre", [])
        for keys, new_values in universe:
            keys, new_values = self._reindex(keys, new_values, self.axe)

            old_values = self._last_output.setdefault(keys, {})
            # call to the lambda function defined in configuration for this instance

            # TODO: agp: check how lambdas are chained
            # TODO: agp: need to have same/simular data layout
            for lambda_name, func in lambdas.items():
                # value = pickle.loads(pickle.dumps(new_values))
                # value
                # {'max': {'WD': [182.0, '2024-07-09 09:27:46+00:00', 'WD']}}
                # value = func(keys, old_values, new_values, edge)
                if old := old_values.get(lambda_name):
                    self._pre_lambda(old, new_values, self.OPERATORS.get(lambda_name))
                else:
                    ordered = list(walk(new_values))
                    access = {k: v for k, v in ordered}
                    old = ordered, access
                    old_values[lambda_name] = old

                # self._last_output.setdefault(keys, {}).update(value)

        # post
        lambdas = self._lambdas.setdefault("post", {})
        for keys, values in list(self._last_output.items()):
            for lambda_name, func in lambdas.items():
                values = func(keys, values, edge)

            self._last_output.setdefault(keys, {}).update(values)

        # rebuild the container but with the modified values
        for keys, lambdas in self._last_output.items():
            for lambda_name in lambdas:
                ordered, access = lambdas[lambda_name]
                stream = [(key, access[key]) for key, _ in ordered]
                struct = rebuild(stream)
                lambdas[lambda_name] = struct

        # transform data to be delivered
        # stamp edge meta info in payload
        # non_edge_keys = set(edge).difference(ekeys)
        # edge_meta = {_: edge[_] for _ in non_edge_keys}

        # allow to have individual waves when saving in storage
        # edge_meta[MONOTONIC_KEY] = monotonic_wave()
        edge_meta = {
            _: self.FUNC_CAST[_](edge[_])
            for _ in set(self.FUNC_CAST).intersection(edge)
        }

        for payload in self.build_output():
            payload.update(edge_meta)
            yield payload

    # --------------------------------------------------------
    # abstract methods
    # --------------------------------------------------------
    def _calc(self, key, old_value, new_value):
        raise RuntimeError("you need to implement this incremental compute")

    def _push_wip_edge(self, ready):
        raise NotImplementedError()


class XParticleLayout(XParticle):
    async def _compute(self, edge, ekeys):
        """
        Example:

        incoming data
        {'max': [0.9, '2024-07-15 06:27:24+00:00', 'WS'],
         'min': [0.1, '2024-07-15 05:33:50+00:00', 'WS'],
         'geojson': {'type': 'Point',
                     'coordinates': [-4.461883079891437, 36.70903446778742]},
         'id': '6',
         'geokey': '6',
         'datetime': '2024-07-15 09:00:00+00:00'}

         outgoing data
         {'geojson': {'type': 'Point',
                      'coordinates': [-4.461883079891437, 36.70903446778742]},
          'id': '6',
          'geokey': '6',
          'datetime': '2024-07-15 09:00:00+00:00',
          'max_WS_value': 0.9,
          'max_WS_ts': '2024-07-15 06:27:24+00:00',
          'min_WS_value': 0.1,
          'min_WS_ts': '2024-07-15 05:33:50+00:00'}

        """
        async for data in super()._compute(edge, ekeys):
            # TODO: agp: move to base class
            # strategy 1
            for lambda_name in self.available_lambdas.intersection(data):
                if self.drop_temp:
                    sub_data = data.pop(lambda_name)
                else:
                    sub_data = data[lambda_name]
                # transform data using all mappers defined

                assert isinstance(sub_data, dict)

                for attr, value in sub_data.items():
                    if re.match(REG_PRIVATE_KEY, attr):
                        continue

                    if lambda_name in ("copy",) or not isinstance(
                        value, (float, int, FloatWhen)
                    ):
                        data.setdefault(f"{attr}", value)
                        continue

                    # if not isinstance(
                    #     value, (float, int, FloatWhen)
                    # ):
                    #     continue

                    # don't apply the layout mapping twice
                    if re.match(self.REG_EXCLUDE_TWICE, attr):
                        continue

                    if lambda_name in (
                        "max",
                        "min",
                        "peak",
                    ):
                        if isinstance(value, FloatWhen):
                            data[f"{attr}_{lambda_name}_value"] = value.value
                            data[f"{attr}_{lambda_name}_datetime"] = value.datetime
                        else:
                            data[f"{attr}_{lambda_name}_value"] = value
                            if not (dt := sub_data.get("datetime")):
                                dt = SDATE(sub_data.get(MONOTONIC_KEY))
                            data[f"{attr}_{lambda_name}_datetime"] = dt

                    elif lambda_name in (
                        "average",
                        "freq",
                        "sum",
                    ):
                        data[f"{attr}_{lambda_name}_value"] = value
                    else:
                        data[f"{attr}_{lambda_name}_XXXXX"] = value

            yield data


class XPeakParticle(XParticleLayout):
    async def _compute(self, edge, ekeys):
        """
        Return None if we don't want to store info
        """
        async for payload in super()._compute(edge, ekeys):
            yield payload


class XGeoParticle(XParticle):
    def __init__(self, uid, sources, broker, storage, **kw):
        complete_on(
            kw,
            "group_by",
            [
                "geo_key",
            ],
            where="begin",
        )
        super().__init__(uid, sources, broker, storage, **kw)


class XMaxParticle(XGeoParticle):
    def __init__(self, uid, sources, broker, storage, **kw):
        kw.setdefault("function", "max")
        super().__init__(uid, sources, broker, storage, **kw)


class XInterpolate(XParticle):
    """A particle that condense and interpolate information before
    generate a new edge

    Some operations may be executed in cascade using subclassing
    """

    def __init__(self, uid, sources, broker, storage, **kw):

        super().__init__(uid, sources, broker, storage, **kw)

        self._cached_M = {}
        self._wip_idt_found = {_: {} for _ in sources}
        self._wip_known_idt = {_: [] for _ in sources}
        self._wip_nurbs = {}
        self._wip_pending_edge = {_: set() for _ in sources}
        self._wip_result = {_: {} for _ in sources}

    # --------------------------------------------------------
    # private derived methods
    # --------------------------------------------------------
    def _get_wip_completed_edge(self, buffer, context) -> EDGE:
        """
        1. find tge next time mark (t0) from the 1st data received
        2. t0 > datetime of 1st data point
        3. create a record for each different data point in order to check:
        4. add this signal to pending ones
        5. update lower bound_t0, t0, upper bound_t1
         . loop for geting more data
         . update the record
        6. check if record has cross t0 limit
        7. is eligible for interpolating in t0
        8. remove this signal from pending
        9. when no more pending signals are waiting to complete, we can generate an edge
        10. if we receive a point over t1, the we force all pending singals to be part
            of the edge despite we've no data that have crossed the t0 line

        """
        result = {}
        try:

            for uid, uid_holder in self._wip_stream.items():
                # 2. t0 > datetime of 1st data point
                known_idt = list(uid_holder)
                known_idt.sort()

                # 1. find tge next time mark (t0) from the 1st data received
                if t0 := self._wip_cursor.get(uid):
                    t1 = self.cron[uid].next_ts(t0)
                else:
                    t0 = self._find_bound_interval(uid)
                    t1 = self.cron[uid].next_ts(t0)
                    delta = t1 - t0
                    t1 = t0
                    t0 = t0 - delta
                    assert t1 > known_idt[0]

                if not known_idt or (idt1 := known_idt[-1]) < t1:
                    # we've not crossed t1 boundary yet
                    continue

                # recollect all keys that can be interpolated
                idt_found = self._wip_idt_found[uid]
                pending = self._wip_pending_edge[uid]
                # _result = self._wip_result[uid]

                # TODO: agp: can we drop values that have been used?
                # TODO: in that case, t1 will be automatically computed
                for idt in known_idt:  # sorted
                    for key, data in uid_holder.get(idt, {}).items():

                        # 3. create a record for each different data point
                        if not (record := idt_found.get(key)):
                            if idt <= t1:
                                record = idt_found[key] = [idt1, idt, t1]
                                # 4. add this signal to pending ones
                                pending.add(key)
                            else:
                                # ignore creation of a unseen record because
                                # it starts in a future interval
                                continue

                        # 5. update lower bound_t1, t1, upper bound_t1
                        record[0] = min(record[0], idt)
                        record[1] = max(record[1], idt)

                        # 6. check if record has cross t1 limit
                        if record[0] < t1 and record[1] > record[-1]:
                            # 7. is eligible for interpolating in t1
                            # _result.setdefault(uid, {})[key] = record

                            # 8. remove this signal from pending
                            if key in pending:
                                pending.remove(key)
                                if not pending:
                                    break

                    # 10. if we receive a point over t1, the we force edge
                    if not pending or idt == idt1:
                        pending.clear()
                        break
                # 9. when no more pending signals are waiting
                # to complete, we can generate an edge
                if not pending:
                    self._wip_cursor[uid] = t1
                    result[uid] = idt_found.copy()
                    # cleanning
                    idt_found.clear()
                    break

        except Exception as why:
            log.error(why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
            print(why)

        return result

    def _new_wip(self):
        super()._new_wip()
        # XInterpolate never cleans its historical by default
        # so don't do something like:
        # self._wip_edge = {_: {} for _ in self.sources}
        # but
        for _ in self.sources:
            self._wip_stream.setdefault(_, {})
            # self._wip_edge.setdefault(_, {})
            self._wip_nurbs.setdefault(_, {})

        # self._wip_uncompleted = set(self.sources)

    def _push_wip_edge(self, ready):
        try:
            for uid, info in ready.items():
                nurbs_data = self._wip_nurbs[uid]
                tmp_holder = self._wip_stream[uid]
                interpolated = self._wip_edge
                for key, known_idts in info.items():
                    data = nurbs_data[key]
                    _info = info[key]
                    for parameter, data_points in data.items():
                        # TODO: remove
                        interval = [_.timestamp() for _ in _info]
                        bt0, bt1, t0 = interval
                        if (r := bt1 - bt0) > 0:
                            # we have more than 1 point
                            x = (t0 - bt0) / r
                        else:
                            x = 2.0  # > 1.0

                        if x < 1.0:
                            # use NURBS for interpolating, but we need to find the real `x`
                            assert 0.0 <= x <= 1.0
                            assert bt0 < t0 < bt1

                            # points = []
                            # for p in data_points:
                            #     p = p.copy()
                            #     p[0] -= bt0
                            #     points.append(p)

                            points = data_points

                            # calc value
                            p0, p1 = None, None
                            N = len(points)
                            for idx, p in enumerate(points):
                                p0 = p1
                                p1 = p
                                if p1[0] > t0:
                                    # estimate the real value of x € [0,1]
                                    # x = float(idx) / N
                                    # use a lineal interpolation
                                    f = (t0 - p0[0]) / (p1[0] - p0[0])
                                    x += f / N
                                    v = p0[1] + (p1[1] - p0[1]) * f
                                    value = [t0, v]
                                    break
                            else:
                                raise RuntimeError()
                            foo = 1

                            # using interpolation?
                            # value0 = curve.evaluate_single(x)

                            debug = False
                            if debug:
                                # degree = 1 if len(points) <= 10 else 2
                                degree = 1
                                curve = fitting.interpolate_curve(points, degree)
                                self._plot(curve, points, value, key)
                        else:
                            # we can't extrapolate, so the the lastest value
                            for value in data_points:
                                if value[0] >= bt1:
                                    value = [t0, value[1]]
                                    break
                            else:
                                log.error(
                                    "can't find  the lastest value from signal, using 1st one!"
                                )
                                value = [t0, data_points[-1][1]]

                        assert len(value) == 2

                        error = value[0] - t0
                        if error > 60:
                            log.warning(
                                "interpolated date and real one differs: %s sec (> 60 secs)",
                                error,
                            )
                        # tsample = datetime.fromtimestamp(value[0])
                        dt = value[0] = _info[2]

                        # we can remove from _wip_stream
                        # but preserve _wip_nurbs as it's been computed by timestamp
                        # and may be usefull for better interpolation (higher degree)
                        # we can drop some values from _wip_nurbs as we want if we
                        # keep the necessary points

                        # drop the data that has been used somehow
                        received = {}

                        # must be sorted to get the last received!
                        all_idts = list(tmp_holder)
                        all_idts.sort()
                        for bdt in all_idts:
                            if bdt > dt:
                                break
                            dated_key_items = tmp_holder[bdt]
                            if key in dated_key_items:
                                received = dated_key_items.pop(key)
                                if not dated_key_items:
                                    # cleaning data
                                    tmp_holder.pop(bdt)
                                # received = dated_key_items[key]
                                received = received[0]  # we've only one!

                        if received:  # use the last found
                            # we don't need to make a copy, it will be drop forever
                            if "org" in received:
                                # TODO: clone same strategy and use always "org" and other fields?
                                new = received.get("org") or received
                                assert parameter in received["value_keys"]
                            else:
                                new = received

                            new[parameter] = value[1]
                            new["datetime"] = dt
                            new[MONOTONIC_KEY] = int(dt.timestamp() * WAVE_FACTOR)
                            interpolated.setdefault(uid, {})[key] = new

            self._wip_uncompleted.difference_update(ready)
            # finally we put back the interpolated values into the
            # `_wip_stream` simulatig a fresh data in order to be
            # to do further interpolation with unseen "future" data
            for uid, uid_holder in interpolated.items():
                if re.match(self.EXCLUDE, uid):
                    continue
                holder = self._wip_stream.setdefault(uid, {})

                for key, data in uid_holder.items():
                    data["datetime"] = dt
                    dt_holder = holder.setdefault(dt, {})
                    dt_holder.setdefault(key, []).append(data)

        except Exception as why:
            print(why)
            log.error(why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
            foo = 1

        return interpolated

    def _wip_add_point(self, uid, point):
        # find interpolation datetime
        dt = point["datetime"]
        # place the data point in its structural value
        holder_key = point["structure_values"]
        self._wip_known_keys[uid].add(holder_key)

        # find the holder for this uid and iterpolation time
        # we allocate all related data with its interpolation slot
        uid_holder = self._wip_stream[uid]
        interpolation_holder = uid_holder.setdefault(dt, {})
        # use a list to sort the signals point received
        last_holder = interpolation_holder.setdefault(holder_key, [])
        # insert backwards
        for idx in range(len(last_holder), 0, -1):
            if last_holder[idx - 1]["datetime"] < dt:
                last_holder.insert(idx, point)
                break
        else:
            last_holder.append(point)
            idx = 0

        # add nurbs info
        tid = dt.timestamp() + dt.microsecond
        uid_nurbs = self._wip_nurbs[uid]
        nurbs_interpolation_holder = uid_nurbs.setdefault(holder_key, {})
        for key, value in point["value_values"].items():
            nurbs_data = nurbs_interpolation_holder.setdefault(key, [])
            nurbs_data.append([tid, value])
            # nurbs_data.insert(idx, [tid, value])

    # --------------------------------------------------------
    # private own methods
    # --------------------------------------------------------

    def _plot(self, curve, data_points, value, label):
        #         from geomdl.visualization import VisMPL
        #
        #         vis_comp = VisMPL.VisCurve2D()
        #         curve.vis = vis_comp
        #         curve.render()
        # Plot the curves using Matplotlib
        plt.figure(figsize=(8, 6))

        # Optionally, plot the control points
        data_points_x, data_points_y = zip(*[(pt[0], pt[1]) for pt in data_points])

        data_points_x = [datetime.fromtimestamp(_) for _ in data_points_x]

        plt.scatter(
            data_points_x,
            data_points_y,
            color="blue",
            marker="o",
            label="Control Points Curve 1",
        )

        point = (datetime.fromtimestamp(value[0]), value[1])
        plt.scatter(
            point[0],
            point[1],
            color="red",
            marker="o",
            label="interpolation",
        )
        # Split the evaluated points into x and y coordinates for plotting
        curve.delta = 0.001
        curve1_points = curve.evalpts

        curve1_x, curve1_y = zip(*[(pt[0], pt[1]) for pt in curve1_points])
        curve1_x = [datetime.fromtimestamp(_) for _ in curve1_x]

        plt.plot(
            curve1_x,
            curve1_y,
            label=f"Curve 1 (Degree {curve.degree})",
            # color="blue",
        )
        # plt.plot(
        #     curve2_x,
        #     curve2_y,
        #     label=f"Curve 2 (Degree {degree_curve2})",
        #     color="green",
        # )

        # plt.scatter(
        #     ctrlpts_curve2_x,
        #     ctrlpts_curve2_y,
        #     color="green",
        #     marker="o",
        #     label="Control Points Curve 2",
        # )

        # Customize the plot
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.legend()
        plt.title(f"NURBS Curve: {label}")
        plt.grid(True)

        # Format the X-axis to display dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        # Adjust the interval as needed

        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
        # plt.axis("equal")

        # Show plot
        plt.xticks(rotation=45)  # Rotate date labels for readability

        plt.show()
        foo = 1

    def _wip_next_ts(self, uid, dt):  # TODO: used?
        if dt:
            dt = DATE(dt)
            if ts := self.cron[uid].check(dt):
                return ts

    # --------------------------------------------------------
    # abstract methods
    # --------------------------------------------------------


class iTimedParticle(Particle):
    """Particle that compute data when at certains moments, similar to crontab

    2024-09-24 11:56:05.231292

    - take 1st date
    - if base mark doesn't exits, set to this value
    - as a base mark
    - iterate over *contab* alike expansion
    - date.replace() and check if

    """

    TIME_REGEXP = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}).*?(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})"

    def __init__(self, uid, sources, broker, storage, **kw):
        cron = soft(
            kw.setdefault("cron", {}),
            {
                "second": 0,
            },
        )
        super().__init__(uid, sources, broker, storage, **kw)

        self.cron = {_: Crontab(**cron) for _ in sources}

    def _get_wip_completed_edge(self, buffer, context) -> EDGE:
        # we need to make the smaller step possible
        # as its happens in a live streaming
        for uid in list(self._wip_uncompleted):
            # we need to use a datetime from data, not wave
            # as the iTimedParticle are based on data
            # stream = buffer[uid]
            delta = context.setdefault("delta", {})
            info = delta.setdefault(uid, {})
            data = info.get("org", {})
            # dt = [
            #     _
            #     for _ in [
            #         DATE(data.get(DATETIME_KEY)),
            #         DATE(extract_wave(data)),
            #         DATE(context.get(DATETIME_KEY)),
            #     ]
            #     if _
            # ]
            # dt = dt and max(dt)
            dt = (
                data.get(DATETIME_KEY)
                or extract_wave(data)
                or context.get(DATETIME_KEY)
            )

            def check(dt):
                if dt:
                    dt = DATE(dt)
                    if ts := self.cron[uid].check(dt):
                        # this uid has reach the timed boundary
                        # so we can pause *milking* this source
                        # until the other ones reach the same boundary
                        # as well
                        self._wip_uncompleted.remove(uid)
                        self._wip_edge[MONOTONIC_KEY] = TO_NS(ts)
                        return ts

            if check(dt):
                pass
            elif buffer[uid]:
                pass  # continue processing buffer
            else:
                # source stream is empty, we need to wait for completion
                self._milk.add(uid)


class XParticleEOD(XParticle):
    """Particle that compute data at the end of the day"""

    def __init__(self, uid, sources, broker, storage, **kw):
        soft(
            kw.setdefault("cron", {}),
            {
                "second": 0,
                "minute": 0,
                "hour": 0,
            },
        )
        super().__init__(uid, sources, broker, storage, **kw)


class XParticleEODMax(XParticleEOD):
    """Particle that compute data at the end of the day"""

    def __init__(self, uid, sources, broker, storage, **kw):
        kw.setdefault("function", "max"),
        super().__init__(uid, sources, broker, storage, **kw)


class HourParticle(iTimedParticle):
    """Particle that extract data from stream to compute result every 1 hour"""

    def __init__(self, uid, sources, broker, storage, **kw):
        soft(
            kw.setdefault("cron", {}),
            {
                "second": 0,
                "minute": 0,
            },
        )
        super().__init__(uid, sources, broker, storage, **kw)


class MinuteParticle(iTimedParticle):
    """Particle that extract data from stream to compute result every 1min"""

    def __init__(self, uid, sources, broker, storage, **kw):
        soft(
            kw.setdefault("cron", {}),
            {
                "second": 0,
            },
        )
        super().__init__(uid, sources, broker, storage, **kw)


class Minute5Particle(iTimedParticle):
    """Particle that extract data from stream to compute result every 5min"""

    def __init__(self, uid, sources, broker, storage, **kw):

        soft(
            kw.setdefault("cron", {}),
            {
                "second": 0,
                "minute": "|".join([str(_) for _ in range(0, 60, 5)]),
            },
        )
        super().__init__(uid, sources, broker, storage, **kw)


class Minute15Particle(iTimedParticle):
    """Particle that extract data from stream to compute result every 15min"""

    def __init__(self, uid, sources, broker, storage, **kw):
        soft(
            kw.setdefault("cron", {}),
            {
                "second": 0,
                "minute": "|".join([str(_) for _ in range(0, 60, 15)]),
            },
        )
        super().__init__(uid, sources, broker, storage, **kw)


class iXSMAParticle(XInterpolate):
    def _calc(self, old_values, new_values):  # TODO: review and delete
        for key, new_value in new_values.items():
            old_value = old_values.get(key, new_value)
            M = self._cached_M.get(key) or self._find_M(key)
            old_values[key] = old_value + (new_value - old_value) / M

        foo = 1


class iCollector:
    TRANSLATE = [["measure", "value"]]
    COPY = "|".join(["id.*", "datetime", "name", "ubication", MONOTONIC_KEY])

    CONVERT = {
        "datetime": str,
    }

    async def _compute(self, edge, ekeys):

        result = {}
        for uid, uid_holder in edge.items():
            if re.match(REG_PRIVATE_KEY, uid):
                continue
            aggregated = result.setdefault(
                uid,
                {
                    MONOTONIC_KEY: 0,
                },
            )

            for holder_key, org in uid_holder.items():
                push = False

                for pair in self.TRANSLATE:
                    if all([_ and _ in org for _ in pair]):
                        # use org[name], but last[value]

                        key = org.get(pair[0])
                        value = org.get(pair[1])
                        aggregated[key] = value
                        push = True

                # copy other structural values
                # TODO: don't include data that has been overbound in time
                for key in org:
                    if re.match(self.EXCLUDE, key):
                        continue
                    if re.match(self.COPY, key):
                        aggregated[key] = org[key]

                if dt := org.get("datetime"):
                    wave = int(dt.timestamp() * WAVE_FACTOR)
                    aggregated[MONOTONIC_KEY] = max(
                        aggregated[MONOTONIC_KEY],
                        wave,
                    )
            if push:
                # force datetime to be str
                for key, func in self.CONVERT.items():
                    if value := aggregated.get(key):
                        aggregated[key] = func(value)

                aggregated[ID_KEY] = self.render(**aggregated)

                yield aggregated
            else:
                foo = 1
            foo = 1

        # return result


class XSMAParticle(iCollector, XInterpolate):
    "example of SMA + iTimedParticle"


class XSMAParticle(iCollector, XInterpolate):
    "example of SMA + iTimedParticle"


# class ConfortParticle(XSMAParticle):
#     "example of SMA + iTimedParticle"


# ---------------------------------------------------------
# Surreal Implementation
# ---------------------------------------------------------
# from surrealist import Surreal


class Subscription(BaseModel):
    "live queries callbacks to be fired"

    lq_uid: UID
    callbacks: List[Callable]


class SurrealBroker(Broker):
    "pub / sub broker based on surreal"

    def __init__(self, url):
        super().__init__()
        self.url = url
        # TODO: missing surreal credentials
        self.connection_pool = SurrealConnectionPool(url)
        self._live_queries = {}
        log.info("broker will use [%s]", self.url)

    async def subscribe(self, uri: URI, callback: Callable):
        "TBD"
        await super().subscribe(uri, callback)

        _uri = parse_duri(uri)
        _sub_uri = dict(_uri)
        _sub_uri["path"] = f"/{_sub_uri['_path']}"
        # sub_uri = build_uri(**_sub_uri)

        table = tf(_sub_uri["_path"])
        if not (lq := self._live_queries.get(table)):
            handler = functools.partial(self.dispatch, uri)

            key = (_uri["fscheme"], _uri["host"])
            pool = self.connection_pool
            connection = pool.connections.get(key) or await pool._connect(*key)
            assert connection, "surreal connection has failed"

            # TODO: I think this is unnecessary
            # info = connection.session_info().result  #TODO: agp: Report Bug to Surrealist
            # namespace, database = _uri["fscheme"], _uri["host"]
            # if info["ns"] != namespace or info["db"] != database:
            #     connection.use(namespace, database)

            res = connection.live(table, callback=handler)
            lq_uid = res.result
            # print(f"{uri}: {lq_uid}")
            lq = self._live_queries[uri] = Subscription(lq_uid=lq_uid, callbacks=[])

        lq.callbacks.append((callback, _uri))

    async def unsubscribe(self, uri: URI, callback: Callable):
        "TBD"
        await super().unsubscribe(uri, callback)

        _uri = parse_duri(uri)
        _sub_uri = dict(_uri)
        _sub_uri["path"] = f"/{_sub_uri['_path']}"
        # sub_uri = build_uri(**_sub_uri)

        table = tf(_sub_uri["_path"])
        if lq := self._live_queries.get(uri):
            item = (callback, _uri)
            if item in lq.callbacks:
                lq.callbacks.remove(item)

            if not lq.callbacks:

                key = (_uri["fscheme"], _uri["host"])
                pool = self.connection_pool
                connection = pool.connections.get(key) or await pool._connect(*key)
                assert connection, "surreal connection has failed"

                # TODO: I think this is unnecessary
                # info = connection.session_info()
                # info = info.result
                # namespace, database = _uri["fscheme"], _uri["host"]
                # if info["ns"] != namespace or info["db"] != database:
                #     connection.use(namespace, database)

                result = connection.kill(lq.lq_uid)
                if result.status in ("OK",):
                    log.debug("Live Query for  [%s] deactivated", uri)
                else:
                    log.error(
                        "Error Deactivating subscription for [%s] -> [%s]", uri, result
                    )
                self._live_queries.pop(uri)
        else:
            log.warning("subscription [%s] is not found", uri)

    def dispatch(self, uid: str, res):
        "process an event from broker"
        result = res["result"]
        # assert result["action"] in (
        #     "CREATE",
        #     "UPDATE",
        # )
        # event = Event(uid=uid, **result['result'])
        event = result["result"]
        for callback, _uri in self._live_queries[uid].callbacks:
            if _uri.get("id") in (event.get(ORG_KEY), None):
                callback(_uri, event)

    async def is_connected(self):
        connections = [
            con.is_connected() for con in self.connection_pool.connections.values()
        ]
        return all(connections)


# ---------------------------------------------------------
# Example of a Particle Implementation
# ---------------------------------------------------------
class PlusOne(Particle):
    "Example of a Particle Implementation that adds 1 to the payload"

    async def _compute(self, edge, ekeys):
        s = 0
        for k in ekeys:
            s += edge[k]["payload"]

        s /= len(ekeys)
        s += random.random()
        data = {
            self.uid: s,
        }
        return data


class TempDiff(Particle):
    """Example of a Particle Implementation that computes
    the difference between the first and the last value"""

    async def _compute(self, edge, ekeys):
        X = [edge[k]["payload"] for k in ekeys]
        y = X[0] - X[-1]
        return y


# ---------------------------------------------------------
class TubeSync(Particle):
    """Do nothing special, but synchronize data"""
