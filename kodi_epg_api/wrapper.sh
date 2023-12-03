# Start the REST APIs
cd /iptv/iptv/src/ || exit
# start fastAPI at port=3003
python3 -u epg_extractor.py --iptv_url "$IPTV_URL" &

cd /iptv/epg/scripts/commands/epg/
# Rest API throws an exception if not at least one site is loaded
npm run grab -- --site=tv.blue.ch --days 3 --maxConnections=3
# start the JavaScript server, guide availabla at port=3000
npm run serve &

# Wait for any process to exit
wait
# Exit with status of process that exited first
exit $?