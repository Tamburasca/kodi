#!/usr/bin/env python3

from ipytv import playlist
from ipytv.playlist import M3UPlaylist
from ipytv.channel import IPTVAttr
from ipytv.exceptions import MalformedPlaylistException
import requests
from xml.etree import ElementTree as ET
import json
import argparse
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, PlainTextResponse
from fastapi import status
from fastapi.openapi.utils import get_openapi
import uvicorn
import logging
from typing import Dict, Any

__author__ = "Dr. Ralf Antonius Timmermann"
__copyright__ = ("Copyright (C) Ralf Antonius Timmermann, "
                 "AIfA, University Bonn")
__credits__ = ""
__license__ = "BSD 3-Clause"
__version__ = "0.0.4"
__maintainer__ = "Dr. Ralf Antonius Timmermann"
__email__ = "rtimmermann@astro.uni-bonn.de"
__status__ = "QA"

myformat = ("%(asctime)s.%(msecs)03d :: %(levelname)s: %(filename)s - "
            "line %(lineno)s - function: %(funcName)s() :: %(message)s")
logging.basicConfig(format=myformat,
                    level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S")
# suppress debug & info logs from ipytv module
logging.getLogger("ipytv").setLevel(logging.WARNING)

URL_EPG = "http://localhost:3000/guide.xml"  # from inside docker container
HOST = '0.0.0.0'
PATH_GUIDE = "/guide.xml"


class MyException(Exception):
    def __init__(
            self,
            *,
            status_code,
            detail
    ):
        super().__init__(
            status_code,
            detail
        )
        self.status_code: int = status_code
        self.detail: str = detail


def my_openapi_schema() -> Dict[str, Any]:
    """
    see blog, e.g.
    https://www.linode.com/docs/guides/documenting-a-fastapi-app-with-openapi/
    :return: modified openapi schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Kodi Web Rest API",
        version=__version__,
        description="API to process IPTV and EPG data",
        routes=app.routes
    )
    openapi_schema["paths"][PATH_GUIDE]["get"]["responses"]["200"] = {
            "description": "Return an EPG in xml format.",
            "content": {
                "application/xml": {
                    "schema": {}
                }
            }
        }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def logging_debug(
        *,
        debug: bool
) -> None:
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        for loggers, log_obj in logging.Logger.manager.loggerDict.items():
            if not loggers.startswith("ipytv"):
                log_obj.disabled = True


def get_iptv(
        *,
        urls: str,
        filtered: bool,
        debug: bool
) -> str:

    logging_debug(debug=debug)

    pl_add, pl_new = M3UPlaylist(), M3UPlaylist()
    channel_list = list()
    tmp_dict = dict()

    with open("data/iptv_corrected.json", "r") as f:
        channel_dict = json.load(f)

    try:
        for url in urls.split(","):
            for channel in playlist.loadu(url.split()[0]).get_channels():
                # add channel if not in program list, first come, first served
                tmp_dict.update({channel.name: {}})  # tmp dict for entire list
                if channel.name not in channel_list:
                    channel_list.append(channel.name)
                    pl_add.append_channel(channel)
        all_channels = pl_add.get_channels()
    except (AttributeError, IndexError) as e:
        raise MyException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except MalformedPlaylistException as e:
        raise MyException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    logging.info("{} channels read from IPTV source.".format(len(tmp_dict)))
    logging.debug("\n" + json.dumps(tmp_dict,
                                    ensure_ascii=False,
                                    indent=2))

    for item in all_channels:
        c = item.copy()
        try:
            new_a = channel_dict[c.name]
        except KeyError:
            continue
        # fetch values, otherwise None
        if new_a.get("name"):
            c.name = new_a.get("name")
        if new_a.get("extras"):
            c.extras = new_a.get("extras")
        if new_a.get("tvg-name"):
            c.attributes[IPTVAttr.TVG_NAME.value] = new_a.get("tvg-name")
        if new_a.get("tvg-id"):
            c.attributes[IPTVAttr.TVG_ID.value] = new_a.get("tvg-id")
        if new_a.get("group-title"):
            c.attributes[IPTVAttr.GROUP_TITLE.value] = new_a.get("group-title")
        if new_a.get("tvg-shift"):
            c.attributes[IPTVAttr.TVG_SHIFT.value] = new_a.get("tvg-shift")
        if new_a.get("tvg_chno"):
            c.attributes[IPTVAttr.TVG_CHNO.value] = new_a.get("tvg_chno")

        pl_new.append_channel(c)

    logging.info("{} channels selected from IPTV sources."
                 .format(pl_new.length()))

    return pl_new.to_m3u_plus_playlist() if filtered \
        else pl_add.to_m3u_plus_playlist()


def get_guide(
        *,
        debug: bool
) -> str:

    logging_debug(debug=debug)

    with open("data/epg_corrected.json", "r") as f:
        channel_dict = json.load(f)

    try:
        response = requests.get(URL_EPG)
        response.raise_for_status()
    except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            ConnectionRefusedError
    ) as e:
        raise MyException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    tree = ET.fromstring(response.content)
    for channel in tree.findall('channel'):
        for display_name in channel.findall("display-name"):
            try:
                display_name.text = channel_dict[display_name.text]  # remap
            except KeyError:
                pass

    return ET.tostring(
        tree,
        encoding="unicode",
        xml_declaration=True,
        method='xml'
    )


app = FastAPI()


@app.get(
    PATH_GUIDE,
    summary="Outputs a corrected EPG response in xml format"
)
async def epg() -> Response:
    try:
        return Response(
            status_code=status.HTTP_200_OK,
            content=get_guide(debug=argparser.parse_args().debug),
            media_type="application/xml",
        )
    except MyException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail="Resource Unavailable: {}".format(e)
        )


@app.get(
    "/iptv/read",
    summary="Filtered & corrected list of channels with response in M3U format",
    response_class=PlainTextResponse
)
async def read() -> PlainTextResponse:
    try:
        return get_iptv(
            urls=argparser.parse_args().iptv_url,
            filtered=True,
            debug=argparser.parse_args().debug
        )
    except MyException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail)


@app.get(
    "/iptv/unfiltered",
    summary="Unfiltered list of channels with response in M3U format",
    response_class=PlainTextResponse
)
async def unfiltered() -> PlainTextResponse:
    try:
        return get_iptv(
            urls=argparser.parse_args().iptv_url,
            filtered=False,
            debug=argparser.parse_args().debug
        )
    except MyException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail)

# custom schema
app.openapi = my_openapi_schema

argparser = argparse.ArgumentParser(
    description="Rest API for IPTV & EPG client")

argparser.add_argument(
    '--api_port',
    required=False,
    type=int,
    help='Port (default: 3003)',
    default=3003  # change docker run command appropriately
)
argparser.add_argument(
    '--iptv_url',
    required=False,
    type=str,
    help='url of iptv providers (separated by comma)'
)
argparser.add_argument(
    '--debug',
    required=False,
    help='Debug Mode (default: False)',
    action="store_true"
)

logging.info("Accepting requests on port {}"
             .format(argparser.parse_args().api_port))

uvicorn.run(app,
            host=HOST,
            port=argparser.parse_args().api_port)
