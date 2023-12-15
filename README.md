# Kodi Rest API

serves as a wrapper for the IPTV SimpleClient 
as IPTV and EPG sources in order to filter and 
rename attributes. This is required - for a few channels - 
in order to match channels and their program guide.

1. Channel sources (filtered & unfiltered) for all sites that are 
provided in .env (separated by comma). Returns a text/plain response to 
serve a m3u file format. Filtering and reformating is defined in 
[iptv_corrected.json](https://github.com/Tamburasca/kodi/blob/63b8967e152d43200b7169c17d566f78c9708959/kodi_epg_api/src/data/iptv_corrected.json)

Provided endpoints:


    http://localhost:3003/iptv/read

    http://localhost:3003/iptv/unfiltered

2. Electronic program guide (epg), renames channel names as provided from 
https://github.com/iptv-org/epg via http://localhost:3000/guide.xml The channel
site is defined in 
[wrapper.sh](https://github.com/Tamburasca/kodi/blob/69187c86d9edc0eaa648434f28c417774f76dc01/kodi_epg_api/wrapper.sh).
Renaming is defined in [epg_corrected.json](https://github.com/Tamburasca/kodi/blob/63b8967e152d43200b7169c17d566f78c9708959/kodi_epg_api/src/data/epg_corrected.json)

Provided endpoint:

    http://localhost:3003/guide.xml

Note: the EPG is cached after the javascript server is started, such it can
be utilized in case grabbing the site is still active.

If you need to call the KODI Web API via, here a few examples:
    
    curl --data-binary '{"jsonrpc": "2.0", "method": "PVR.GetChannelGroups", "params": {"channeltype" : "tv"}, "id": 1 }' -H 'content-type: application/json;' http://localhost:8080/jsonrpc
    curl --data-binary '{"jsonrpc": "2.0", "method": "System.GetProperties", "params": {"properties": ["canreboot"]}, "id": 1 }' -H 'content-type: application/json;' http://localhost:8080/jsonrpc
    curl --data-binary '{"jsonrpc": "2.0", "method": "Input.executeaction", "params": {"action": "reloadkeymaps"}, "id": 1 }' -H 'content-type: application/json;' http://localhost:8080/jsonrpc

Update the EPG via

      $ docker exec -w <working dir> <container id | name> npm run grab -- --site=<web site>, e.g
      $ docker exec -w /iptv/epg/scripts/commands/epg/ kodi_all npm run grab -- --site=chaines-tv.orange.fr


## Installation on a Raspberry PI 4

Install - under PVR-Clients - the IPTV SimpleClient and configure it for
the following menu items:

1. General:

    URL for M3U-List: http://localhost:3003/iptv/read


2. EPG:

    URL for XMLTV: http://localhost:3003/guide.xml


Since the docker container may not yet be up when the playlist is loaded 
KODI's start needs to be delayed. 

    systemctl edit kodi-autostart.service

Add the following line:

    [Service]
    ExecStartPre=/bin/sleep 10
