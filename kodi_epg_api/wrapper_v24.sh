if [ "$DEBUG" = "true" ] ; then debug="--debug" ; fi
if [ "$EPG_CACHED" = "true" ] ; then epg_cached="--epg_cached" ; fi

# Start the REST APIs
cd /iptv/iptv/src/ || exit
# start fastAPI at port=3003
python3 -u webAPI_IPTV_SimpleClient_v24.py --iptv_url "${IPTV_URL}" ${debug} ${epg_cached} &

cd /iptv/epg/scripts/commands/epg/ || exit
# start the JavaScript server, EPG available at port=3000
npx serve &
# Rest API throws an exception if not at least one site is loaded
npm run grab --- --site=tv.blue.ch --days=3 --maxConnections=3
# save EPG to cache
if [ "$EPG_CACHED" = "true" ]
then
  cp /iptv/epg/guide.xml /iptv/iptv/src/data/epg_cached.xml ; \
  chmod 666 /iptv/iptv/src/data/epg_cached.xml || true
else
  rm -f /iptv/iptv/src/data/epg_cached.xml || true
fi

# Wait for any process to exit
wait
# Exit with status of process that exited first
exit $?