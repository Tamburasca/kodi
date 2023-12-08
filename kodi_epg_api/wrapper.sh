# Start the REST APIs
cd /iptv/iptv/src/ || exit
# start fastAPI at port=3003
python3 -u webAPI_IPTV_SimpleClient.py --iptv_url "$IPTV_URL" --epg_cached "$EPG_CACHED" --debug &

cd /iptv/epg/scripts/commands/epg/ || exit
# Rest API throws an exception if not at least one site is loaded
npm run grab -- --site=tv.blue.ch --days 3 --maxConnections=3
# start the JavaScript server, EPG available at port=3000
npm run serve &
# save EPG to cache
sleep 30; \
cd /iptv/iptv/src/data; \
curl localhost:3000/guide.xml > "$EPG_CACHED"; \
chmod 666 "$EPG_CACHED"

# Wait for any process to exit
wait
# Exit with status of process that exited first
exit $?