#!/bin/sh
#docker exec -w /iptv/epg/scripts/commands/epg/ kodi_all npm run grab -- --site=chaines-tv.orange.fr
#docker exec -w /iptv/epg/scripts/commands/epg/ kodi_all npm run grab -- --site=tvheute.at
docker exec -w /iptv/epg/scripts/commands/epg/ kodi_all npm run grab -- --site=tv.blue.ch
