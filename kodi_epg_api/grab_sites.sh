#!/bin/sh
# docker exec -w /iptv/epg/scripts/commands/epg/ kodi_epg_api npm run grab -- --site=chaines-tv.orange.fr
# docker exec -w /iptv/epg/scripts/commands/epg/ kodi_epg_api npm run grab -- --site=tvheute.at
docker exec -w /iptv/epg/scripts/commands/epg/ kodi_epg_api npm run grab -- --site=tv.blue.ch
