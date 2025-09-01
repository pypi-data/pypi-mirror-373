"""Main module."""

# library modules
# import asyncio

import asyncio

import aiohttp

import os
import random
import pickle
import re
import sys
import traceback
import time
import yaml

import uvicorn

# from glom import glom  # , assign, T, merge

# ---------------------------------------------------------
# local imports
# ---------------------------------------------------------

# ---------------------------------------------------------
# helpers
# ---------------------------------------------------------
# from agptools.containers import walk, overlap, build_paths, SEP
# from agptools.helpers import replace

# from ..helpers import replace

# ---------------------------------------------------------
# models / mappers
# ---------------------------------------------------------
# from ..models.smartmodels import SmartmodelsApp
# from .. import mappers

# from ..models.enums import *

# from ..definitions import TAG_KEY

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from agptools.logs import logger

log = logger(__name__)


class SmartmodelsCrawler(AsyncCrawler):
    "Example class for Smartmodels crawler"

    MODEL = SmartmodelsApp

    EXPRESSIONS = {
        # "users": "users.*.[id, name, email]",
    }
    EXTRA_KEYS = {
        # "notes": "notes_",
        # "children": "children_",
        # "parent": "parent_",
    }
    PARSE_KIND_URL = {
        # "wikis": [r"/projects/(?P<project_id>\d+)/wikis.*"],
        # "wikis-single": [r"/projects/(?P<project_id>\d+)/wikis.*"],
        # # '/projects/{project_id}/issues/{iid}/notes',
        # "notes": [r"/projects/(?P<project_id>\d+)/issues/(?P<iid>\d+)/notes.*"],
    }
    NESTED_URL = {
        # "attraction": [],
        # "poi": [],
        # "event": [],
        # "destination": [],
        # "trip": [],
        # "root": [
        #     (
        #         "users",
        #         "/users",
        #     ),
        #     (
        #         "groups",
        #         "/groups?statistics=true",
        #     ),
        # ],
        # "groups": [
        #     (
        #         "projects",
        #         "/groups/{id}/projects",
        #     ),
        # ],
        # "projects": [
        #     ##(
        #     ##'users',
        #     ##'/projects/{id}/users',
        #     ##),
        #     (
        #         "issues",
        #         "/projects/{id}/issues",
        #     ),
        #     (
        #         "wikis",
        #         "/projects/{id}/wikis",
        #     ),
        #     (
        #         "milestones",
        #         "/projects/{id}/milestones",
        #     ),
        # ],
        # "milestones": [
        #     (
        #         "milestones-single",
        #         "/projects/{project_id}/milestones/{id}",
        #     ),
        # ],
        # "issues": [
        #     (
        #         "notes",
        #         "/projects/{project_id}/issues/{iid}/notes",
        #     ),
        # ],
        # "notes": [],
        # "users": [
        #     (
        #         "users-single",
        #         "/users/{id}",
        #     ),
        # ],
        # "wikis": [
        #     (
        #         "wikis-single",
        #         "/projects/{project_id}/wikis/{slug}?with_content=1",
        #     ),
        # ],
        # "milestones-single": [],
        # "wikis-single": [],
        # "users-single": [],
    }
    MAPPERS = {
        **AsyncCrawler.MAPPERS,
        **{
            # "poi": mappers.POI,
            # "attraction": mappers.Attraction,
            # "event": mappers.Event,
            # "destination": mappers.Destination,
            # "trip": mappers.Trip,
        },
    }
    REFERENCE_MATCHES = AsyncCrawler.REFERENCE_MATCHES + [
        # r"/author/id$",
        # r"/assignee/id$",
        # r"/assignees/\d+/id$",
        # r"/closed_by/id$",
        # r"/created_by/id$",
        # # r'/notes/\d+/id$',
        # r"/milestone/id$",
        # r".*/author/id$",
    ]
    RESTRUCT_DATA = {
        **AsyncCrawler.RESTRUCT_DATA,
        **{
            # specific restruct info that applies to all kinds
            "default": {
                # # type need only a change in the key used
                # r"@type$": ("type", "{value}"),
                # # use only the 1st image as image_url
                # r"headerMedia/0/link/url": ("image_url", "{value}"),
                # # keywords are mapped as a set(), using a dict with no values
                # r"keywords/(?P<idx>\d+)/text": ("tags/{value}", ""),
                # # location and address
                # r"(?P<path>location)/location/(?P<subpath>.+)": (
                #     "{path}/geojson/{subpath}",
                #     COPY,
                # ),
                # r"(?P<subpath>address)/streetAddress$": ("location/{subpath}", COPY),
            },
            # specific restruct info for different kinds
            # "poi": {},
            # "attraction": {},
            # "event": {},
            # "description": {},
        },
    }
    RETAG_DATA = {
        **AsyncCrawler.RETAG_DATA,
        **{},
    }
    # corner cases for getting uid for specific `kind` objects
    KINDS_UID = {
        **AsyncCrawler.KINDS_UID,
        **{
            "root": ("{url}", I, "url"),
            # 'groups': ("{id}", int, 'id'),
        },
    }
    PAGINATION_KIND = set(
        [
            # "poi",
            # "attraction",
            # "event",
            # "destination",
            # "trip",
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        app_url = self.cfg.get("app_url")
        self.app_url = self.cfg["app_url_dev"] if app_url else self.cfg["app_url"]

        mapping_url = self.cfg.get("mapping_url", "mapping.yaml")

        # mapping = yaml.load(open(mapping_url), Loader=yaml.Loader)
        # self.RETAG_DATA.update(mapping)

        self.tagger = Tagger(mapping_url=mapping_url)
        self.tagger.expand()

        self.model = self.MODEL()

    def _mask_restruct_data(self):
        DATA = self.RESTRUCT_DATA
        for container in DATA.values():
            for k in list(container):
                v = container.pop(k)
                k = k.replace("/", SEP)
                v = tuple([v[0].replace("/", SEP), *v[1:]])
                container[k] = v

    def _bootstrap(self):
        self._mask_restruct_data()

        # func, args, kwargs
        yield self.get_data, [], {
            "kind": "foo",
            "path": "/bar",
            "entity": "buzz",
        }

        # example using known enums
        # for entity in list(POIEntitiesEnum):
        #     yield self.get_data, [], {
        #         "kind": "poi",
        #         "path": "/poi",
        #         "entity": entity.value,
        #     }

    async def get_data(self, kind, path, **kwargs):
        """
        Example a crawling function for Smartmodels crawler.

        Get data related to the given kind and path.
        May add more tasks to be done by crawler.

        """
        real_kind = kind.split("-")[0]  # may be separated by '-'
        holder = getattr(self.model, real_kind, None)
        if holder is None:
            log.warning("model hasn't attribute: '%s'", real_kind)
            return

        query_data = {
            "limit": 50,
            "offset": 0,
        }
        query_data.update(kwargs)
        extra = self._extract_path_info(kind, path)

        # call delegate method to gather the information from 3rd system
        result = await self._get_data(path, query_data)
        if not result:
            return

        for org in result:
            data = {**org, **extra}
            data = self._clean(kind, data)
            uid = self.get_uid(kind, data)

            # restruct data internally, based on RESTRUCT_DATA rules
            reveal = build_paths(data)
            try:
                data = self._restruct(kind, data, reveal)
            except Exception as why:
                print(why)

            # more complex data transformations
            data = self._transform(kind, data)

            # bless data with some additional tags
            tags = self.tagger.retag(kind, data, reveal)
            data[TAG_KEY] = tags  # TODO: review used key...

            data = overlap(holder.setdefault(uid, {}), data)

            # give data to crawler
            yield data, (kind, uid, org)

            # to be nice with other fibers
            # await asyncio.sleep(0)

            # get nested items (if any)
            # I'd rather NESTED_URL to be explicitly filled
            # (i.e NESTED_URL[kind]) instead use NESTED_URL.get(kind)
            # in order to check if there's missing some data for an item
            # in the remote system
            for sub_kind, sub_url in self.NESTED_URL[kind]:
                sub_url = sub_url.format_map(data)
                self.add_task(self.get_data, sub_kind, sub_url)

        if kind in self.PAGINATION_KIND:
            if not query_data["offset"]:  # 1st time
                # request all pagination at once!
                while query_data["offset"] < meta["count"]:
                    query_data = dict(query_data)
                    query_data["offset"] += query_data["limit"]
                    kwargs = {
                        **kwargs,
                        **{
                            "kind": kind,
                            "path": path,
                        },
                        **query_data,
                    }

                    self.add_task(
                        self.get_data,
                        **kwargs,
                    )

            # params['offset'] = (page := page + len(result))

    async def _get_data(self, path, query_data):
        "A helper method to get the data from external system"
        for tries in range(1, 15):
            try:
                async with aiohttp.ClientSession() as session:
                    # log.info(f"{self.app_url}{path}: {query_data}")
                    async with session.get(
                        f"{self.app_url}{path}", params=query_data
                    ) as response:
                        if response.status in (200,):
                            result = await response.json()
                            meta = result["meta"]
                            result = result["result"]
                            return result
                        elif response.status in (400,):
                            log.error("%s: %s: %s", response.status, path, query_data)
                            result = await response.json()
                            log.error(result)
                            return
                        else:
                            log.error("Status: %s", response.status)
            except Exception as why:
                log.error(why)
                log.error("".join(traceback.format_exception(*sys.exc_info())))

            log.warning("retry: %s: %s, %s", tries, path, query_data)
            await asyncio.sleep(0.5)

    def _extract_path_info(self, kind, path):
        result = {}
        for regexp in self.PARSE_KIND_URL.get(kind, []):
            m = re.match(regexp, path)
            if m:
                result.update(m.groupdict())

        return result

    def _transform(self, kind, data):
        """More complex transformations"""
        return data
