docker stop kodi_v24
docker rm kodi_v24
docker build -t kodi_v24:0.1 -f Dockerfile_ubuntu_v24 . # --no-cache
docker image prune -f
docker run -d -p 0.0.0.0:3003:3003 --restart unless-stopped --name kodi_v24 \
--env-file .env -v "$(pwd)"/src/data:/iptv/iptv/src/data kodi_v24:0.1