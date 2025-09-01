"""Main module."""

import aiohttp

# library partial

# local imports

# ---------------------------------------------------------
# parallel processing
# ---------------------------------------------------------
from syncmodels.helpers import I
from syncmodels.crawler import iAsyncCrawler

# from syncmodels.syncmodels import SyncModel, COPY
# from syncmodels.storage import PickleStorage as Storage

# ---------------------------------------------------------
# helpers
# ---------------------------------------------------------
from agptools.containers import SEP

# from agptools.helpers import replace, get_wday

# from ..helpers import replace

# ---------------------------------------------------------
# models / mappers
# ---------------------------------------------------------
# from ..models import *
# from .. import mappers

# from ..models.enums import POIEntitiesEnum
from ..models.smartmodels import SmartmodelsApp

# from ..models.dates import RelativeDateRange

# ---------------------------------------------------------
# models / mappers
# ---------------------------------------------------------
# from ..definitions import TAG_KEY

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from agptools.logs import logger

log = logger(__name__)

# ---------------------------------------------------------
# Smartmodels Sync
# ---------------------------------------------------------


class Tagger:
    "Example class for tagging data before creating a model item"

    def __init__(self, mapping_tags: dict = None, mapping_url: str = None):
        if not mapping_tags:
            mapping_tags = yaml.load(open(mapping_url), Loader=yaml.Loader)

        self.mapping_tags = mapping_tags

    def expand(self):
        DATA = self.mapping_tags

        for kind, data in DATA.items():
            INFO = DATA.get("default", {})
            INFO.update(DATA.get(kind, {}))

            changes = 1
            while changes > 0:
                changes = 0
                for kind, values in INFO.items():
                    result = []
                    for value in values:
                        value = replace(value)
                        m = re.match(r"\$\((?P<key>.*)\)$", value)
                        if m:
                            other_key = m.group(1)
                            result.extend(INFO[other_key])
                            changes += 1
                        else:
                            result.append(value)
                    INFO[kind] = result

        for kind, data in DATA.items():
            default = DATA.get("default", {})
            DATA[kind] = {**default, **data}

    def retag(self, kind, data, reveal):
        tags = set()
        DATA = self.mapping_tags
        info = DATA.get("default", {})
        # extend with kind: poi, attraction
        info.update(DATA.get(kind, {}))
        # extend with @type value: Store, Beach, etc
        info.update(DATA.get(replace(data.get("@type", "")), {}))

        # analyze tags
        for path, value in reveal.items():
            value = replace(value)
            found = False
            for template, regexps in info.items():
                for pattern in regexps:
                    pattern = pattern.replace(" ", "\s+")
                    pattern = f".*\s*({pattern})"
                    m = re.match(pattern, value, re.I | re.DOTALL)
                    if m:
                        d = m.groupdict()
                        d["value"] = value

                        tag = template.format_map(d).lower()
                        tags.add(tag)
                        found = True

            if (
                re.search("(keywords|category|audience).*/(text|title|name)", path)
                and not found
            ):
                # log.warning(f"{path}:{value} match is missing in mapping.yaml")
                foo = 1

        tags = list(tags)
        tags.sort()
        return tags


# ---------------------------------------------------------
# Smartmodels Sync
# ---------------------------------------------------------

my_timeout = aiohttp.ClientTimeout(
    total=None,  # total timeout (time consists connection establishment for a new connection or waiting for a free connection from a pool if pool connection limits are exceeded) default value is 5 minutes, set to `None` or `0` for unlimited timeout
    sock_connect=15,  # Maximal number of seconds for connecting to a peer for a new connection, not given from a pool. See also connect.
    sock_read=15,  # Maximal number of seconds for reading a portion of data from a peer
)


class SmartmodelsCrawler(iAsyncCrawler):
    MODEL = SmartmodelsApp

    EXPRESSIONS = {
        # "users": "users.*.[id, name, email]",
    }
    EXTRA_KEYS = {
        # "notes": "notes_",
        # "children": "children_",
        # "parent": "parent_",
    }

    MAPPERS = {
        **iAsyncCrawler.MAPPERS,
        # **{
        #     "poi": mappers.POI,
        #     "attraction": mappers.Attraction,
        #     "event": mappers.Event,
        #     "destination": mappers.Destination,
        #     "trip": mappers.Trip,
        # },
    }
    REFERENCE_MATCHES = iAsyncCrawler.REFERENCE_MATCHES + [
        # r"/author/id$",
        # r"/assignee/id$",
        # r"/assignees/\d+/id$",
        # r"/closed_by/id$",
        # r"/created_by/id$",
        # # r'/notes/\d+/id$',
        # r"/milestone/id$",
        # r".*/author/id$",
    ]

    RETAG_DATA = {
        **iAsyncCrawler.RETAG_DATA,
        **{},
    }
    # corner cases for getting uid for specific `kind` objects
    KINDS_UID = {
        **iAsyncCrawler.KINDS_UID,
        **{
            "root": ("{url}", I, "url"),
            # 'groups': ("{id}", int, 'id'),
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        app_url = self.cfg.get("app_url")
        self.app_url = self.cfg["app_url_dev"] if app_url else self.cfg["app_url"]

        # mapping_url = self.cfg.get("mapping_url", "mapping.yaml")
        # mapping = yaml.load(open(mapping_url), Loader=yaml.Loader)
        # self.RETAG_DATA.update(mapping)
        # self.tagger = Tagger(mapping_url=mapping_url)
        # self.tagger.expand()

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
        yield from super()._bootstrap()

        # for entity in list(POIEntitiesEnum):
        #     yield "get_data", [], {
        #         "kind": "poi",
        #         "path": "/poi",
        #         "entity": entity.value,
        #     }

        # yield self.get_data, [], {
        # "kind": "attraction",
        # "path": "/attraction",
        # "entity": "attraction",
        # }
