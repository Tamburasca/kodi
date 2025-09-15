#!/usr/bin/env python3
# coding: utf-8

"""
An ASGI Web Server providing a Rest API serving as a wrapper for the
IPTV SimpleClient as IPTV and EPG sources in order to filter and
rename attributes. This is required - for a few channels - in order
to match channels with their program guide.

See also https://github.com/Tamburasca/kodi
"""

import argparse
import json
import logging
from typing import Any
from xml.etree import ElementTree as Et

# import requests  # Node.js v21
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.openapi.utils import get_openapi
from fastapi.responses import Response, PlainTextResponse
from ipytv import playlist
from ipytv.exceptions import MalformedPlaylistException
from ipytv.playlist import M3UPlaylist

__author__ = "Dr. Ralf Antonius Timmermann"
__copyright__ = "Copyright (C) Ralf Antonius Timmermann"
__credits__ = ""
__license__ = "BSD 3-Clause"
__version__ = "0.4.0"
__maintainer__ = "Dr. Ralf Antonius Timmermann"
__email__ = "rtimmermann@gmx.de"
__status__ = "Prod"

myformat = ("%(asctime)s.%(msecs)03d :: %(levelname)s: %(filename)s - "
            "line %(lineno)s - function: %(funcName)s() :: %(message)s")
logging.basicConfig(format=myformat,
                    level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S")
# suppress debug & info logs from ipytv module
logging.getLogger("ipytv").setLevel(logging.WARNING)

# URL_EPG = "http://localhost:3000/guide.xml"  # Node.js v21
API_HOST = '0.0.0.0'
API_PORT = 3003
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


def my_openapi_schema() -> dict[str, Any]:
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
        debug: bool = False
) -> None:
    """
    Set logging to debug level
    :param debug:
    :return:
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        for loggers, log_obj in logging.Logger.manager.loggerDict.items():
            if not loggers.startswith(
                    ("ipytv", "uvicorn")
            ):
                log_obj.disabled = True


def get_iptv(
        *,
        urls: str,
        filtered: bool
) -> str:
    """
    read IPTV source(s)
    return playlist in M3U format
    1. if filtered is True, filter and correct channel names
    2. if filtered is False, return unfiltered list of channels
    :param urls:
    :param filtered:
    :return:
    """
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
    if filtered:
        for item in all_channels:
            c = item.copy()
            try:
                new_a = channel_dict[c.name]
            except KeyError:
                continue
            if new_a.get("disable",
                         False): continue  # just skip, serve as placeholder
            # supersede attribute if provided
            if v := new_a.get("name"): c.name = v
            if v := new_a.get("extras"): c.extras = v
            if v := new_a.get("tvg-name"): c.attributes["tvg-name"] = v
            if v := new_a.get("tvg-id"): c.attributes["tvg-id"] = v
            if v := new_a.get("group-title"): c.attributes["group-title"] = v
            if v := new_a.get("tvg-shift"): c.attributes["tvg-shift"] = v
            if v := new_a.get("tvg_chno"): c.attributes["tvg_chno"] = v
            if v := new_a.get("tvg-logo"): c.attributes["tvg-logo"] = v

            pl_new.append_channel(c)

        logging.info("{} channels selected from IPTV sources."
                     .format(pl_new.length()))

        return pl_new.to_m3u_plus_playlist()

    else:

        return pl_add.to_m3u_plus_playlist()


def get_guide(
        original: bool = False
) -> str:
    """
    read EPG source and correct channel names
    return EPG in xml format
    :param original: if True, do not correct channel names
    :return:
    """

    # Node.js v21 restAPI method /guide.xml seems not available
    #    try:
    #        response = requests.get(URL_EPG)
    #        response.raise_for_status()
    #        tree = Et.fromstring(response.content)
    #        logging.debug("Pulled EPG from internet.")
    #    except (
    #            requests.exceptions.HTTPError,
    #            requests.exceptions.ConnectionError,
    #            ConnectionRefusedError
    #    ):
    try:
        with open(f"/iptv/epg{PATH_GUIDE}", "r") as g:
            tree = Et.fromstring(g.read())
    except (IOError, Et.ParseError):
        raise MyException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="EPG is not available or error in xml parser."
        )
    if not original:
        with open("data/epg_corrected.json", "r") as f:
            channel_dict = json.load(f)
        for channel in tree.findall('channel'):
            for display_name in channel.findall("display-name"):
                if v := channel_dict.get(display_name.text):
                    display_name.text = v

    return Et.tostring(
        tree,
        encoding="unicode",
        xml_declaration=True,
        method='xml'
    )


def main():
    """
    Start the ASGI web server
    :return:
    """
    uvicorn.run(app,
                host=API_HOST,
                port=argparser.parse_args().api_port)


app = FastAPI()


@app.get(
    "/original" + PATH_GUIDE,
    summary="Outputs the original EPG response in xml format"
)
async def original_epg() -> Response:
    try:
        return Response(
            status_code=status.HTTP_200_OK,
            content=get_guide(original=True),
            media_type="application/xml",
        )
    except MyException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail="Resource Unavailable: {}".format(e)
        )


@app.get(
    PATH_GUIDE,
    summary="Outputs a corrected EPG response in xml format"
)
async def epg() -> Response:
    try:
        return Response(
            status_code=status.HTTP_200_OK,
            content=get_guide(original=False),
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
            filtered=True
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
            filtered=False
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
    help="Port (default: {})".format(API_PORT),
    default=API_PORT  # change docker run command appropriately
)
argparser.add_argument(
    '--iptv_url',
    required=False,
    type=str,
    help="URL of IPTV providers (separated by comma)"
)
argparser.add_argument(
    '--debug',
    help="Debug Mode",
    action="store_true"
)

logging_debug(debug=argparser.parse_args().debug)
logging.info("Accepting requests on port {}"
             .format(argparser.parse_args().api_port))

if __name__ == "__main__":
    main()
