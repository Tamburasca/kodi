# Start the REST APIs
# ToDo: a list of url multiple addresses is appreciated
cd /iptv/iptv/src/ || exit
# python3 -u iptv_extractor.py --url http://bit.ly/kn-kodi --host 0.0.0.0 --port 3002 &
python3 -u iptv_extractor.py --url "$URL" --host 0.0.0.0 --port 3002 &

cd /iptv/epg/scripts/commands/epg/
# must fill at least one site for method to show up!
npm run grab -- --site=tv.blue.ch
npm run serve &

# Wait for any process to exit
wait
# Exit with status of process that exited first
exit $?