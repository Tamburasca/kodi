#!/bin/sh

if [ "$DEBUG" = "true" ] ; then debug="--debug" ; fi

# Start the REST APIs
cd /iptv/iptv/src/ || exit
# start fastAPI at port=3003
python3 -u webAPI_IPTV_SimpleClient_v24.py --iptv_url "${IPTV_URL}" ${debug} &

cd /iptv/epg/scripts/commands/epg/ || exit
# start the JavaScript server, EPG available at port=3000
npx serve &
# Rest API throws an exception if not at least one site is loaded
npm run grab --- --site=tv.blue.ch --days=3 --maxConnections=3 \
--output=/iptv/iptv/src/data/guide.xml

# Wait for any process to exit
wait
# Exit with status of process that exited first
exit $?