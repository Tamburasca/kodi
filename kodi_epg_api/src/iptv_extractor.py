#!/usr/bin/env python3
"""
example url
    # url = "https://raw.githubusercontent.com/jnk22/kodinerds-iptv/master/iptv/kodi/kodi.m3u"
    # url = "http://bit.ly/kn-kodi"
"""
from ipytv import playlist
from ipytv.playlist import M3UPlaylist
from ipytv.channel import IPTVAttr
import json
import argparse
import os
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn


def main(urls: str) -> str:
    pl_add = M3UPlaylist()
    pl_new = M3UPlaylist()
    channel_list = list()

    with open("channel_corrected.json", "r") as f:
        channel_dict = json.load(f)

    for url in urls.split(","):
        for channel in playlist.loadu(url.split()[0]).get_channels():
            # add channel if not already in program list, first come, first
            # served
            if channel.name not in channel_list:
                channel_list.append(channel.name)
                pl_add.append_channel(channel)
    all_channels = pl_add.get_channels()
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

    return pl_new.to_m3u_plus_playlist()

#    with open('my-fixed-playlist.m3u',
#              'w',
#              encoding='utf-8'
#              ) as out_file:
#        content = pl_new.to_m3u_plus_playlist()
#        out_file.write(content)


app = FastAPI(
    title="IPTV Api",
#    version=__version__,
    description="Ingests data from all URL provided and filters/corrects "
                "channels as verified in a JSON file."
)


@app.get(
    "/iptv/read",
    summary="Outputs a filtered & corrected response type in M3U format",
    response_class=PlainTextResponse
)
async def read() -> PlainTextResponse:
    return main(
        urls=argparser.parse_args().url
    )


argparser = argparse.ArgumentParser(
    description="Rest API for IPTV client")
argparser.add_argument(
    '--url',
    required=True,
    help='url of provider'
)
argparser.add_argument(
    '--host',
    required=False,
    help='IP address for REST API (default: "127.0.0.1")',
    default='127.0.0.1'
)
argparser.add_argument(
    '--port',
    required=False,
    type=int,
    help='Port (default: 3002)',
    default=3002
)
print("PID: {0}".format(os.getpid()))
print("Host: {0}, Port: {1}".format(
    argparser.parse_args().host,
    argparser.parse_args().port)
)

uvicorn.run(app,
            host=argparser.parse_args().host,
            port=argparser.parse_args().port)
