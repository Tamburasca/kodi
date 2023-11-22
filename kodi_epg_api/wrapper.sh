# Start the REST APIs
cd /iptv/iptv/src/ || exit
python3 -u epg_extractor.py &

cd /iptv/epg/scripts/commands/epg/
# must fill at least one site for method to show up!
npm run grab -- --site=tv.blue.ch --maxConnections=2
npm run serve &

# Wait for any process to exit
wait
# Exit with status of process that exited first
exit $?