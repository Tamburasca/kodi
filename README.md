# Kodi Rest API

for
1. m3u channel sources (filtered & unfiltered) for sites provided in .env 
(separated by comma). Provided endpoints:


    http://localhost:3003/iptv/read

    http://localhost:3003/iptv/unfiltered


2. guide.xml for epg, renames channel names as provided from 
https://github.com/iptv-org/epg via http://localhost:3000/guide.xml


    http://localhost:3003/guide.xml