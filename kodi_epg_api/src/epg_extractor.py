import requests
from xml.etree import ElementTree as ET
import json
import argparse
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import uvicorn

__author__ = "Dr. Ralf Antonius Timmermann"
__copyright__ = ("Copyright (C) Ralf Antonius Timmermann, "
                 "AIfA, University Bonn")
__credits__ = ""
__license__ = "BSD 3-Clause"
__version__ = "0.0.1"
__maintainer__ = "Dr. Ralf Antonius Timmermann"
__email__ = "rtimmermann@astro.uni-bonn.de"
__status__ = "Dev"

url = "http://localhost:3000/guide.xml"  # access inside docker container


def main() -> str:
    with open("epg_corrected.json", "r") as f:
        channel_dict = json.load(f)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError
    ) as err:
        raise SystemExit(err)
    tree = ET.fromstring(response.content)
    for channel in tree.findall('channel'):
        for display_name in channel.findall("display-name"):
            try:
                display_name.text = channel_dict[display_name.text]
            except KeyError:
                pass

    return ET.tostring(
        tree,
        encoding="unicode",
        xml_declaration=True,
        method='xml'
    )


app = FastAPI(
    title="EPG Api",
    version=__version__,
    description="Ingests data from all URL provided and filters/corrects "
                "channels as verified in a JSON file.",
)


@app.get(
    "/guide.xml",
    summary="Outputs a corrected epg response in xml format"
)
async def read() -> Response:
    try:
        return Response(
            content=main(),
            media_type="application/xml"
        )
    except SystemExit as e:
        raise HTTPException(
            status_code=503,
            detail="Resource Unavailable: {}".format(str(e))
        )

argparser = argparse.ArgumentParser(
    description="Rest API for EPG client")

argparser.add_argument(
    '--port',
    required=False,
    type=int,
    help='Port (default: 3003)',
    default=3003  # change docker run command appropriately
)
print("Accepting requests on port: {}".format(argparser.parse_args().port))

uvicorn.run(app,
            host='0.0.0.0',
            port=argparser.parse_args().port)
