docker stop kodi_all
docker rm kodi_all
docker build -t kodi_all:0.1 -f Dockerfile_ubuntu_all .
docker image prune -f
docker run -d -p 0.0.0.0:3003:3003 -p 0.0.0.0:3001:3000 --restart unless-stopped --name kodi_all \
--env-file .env -v "$(pwd)"/src/data:/iptv/iptv/src/data --log-opt max-size=10m kodi_all:0.1
# locally
# docker run -d -p 127.0.0.1:3003:3003 -p 127.0.0.1:3001:3000 --restart unless-stopped --name kodi_all \
# --env-file .env -v "$(pwd)"/src/data:/iptv/iptv/src/data kodi_all:0.1