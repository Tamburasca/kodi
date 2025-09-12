#!/bin/sh
#docker exec -w /iptv/epg/scripts/commands/epg/ kodi_all npm run grab --- --site=chaines-tv.orange.fr --maxConnections=10
#docker exec -w /iptv/epg/scripts/commands/epg/ kodi_all npm run grab --- --site=tvheute.at --maxConnections=10
#docker exec -w /iptv/epg/scripts/commands/epg/ kodi_all npm run grab --- --site=hd-plus.de --maxConnections=2
docker exec -w /iptv/epg/scripts/commands/epg/ kodi_all npm run grab --- --site=tv.blue.ch --maxConnections=3
