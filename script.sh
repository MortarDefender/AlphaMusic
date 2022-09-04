docker rm alphamusic
docker rmi alpha
docker build -t alpha .
docker run -p 8000:8000 --name alphamusic alpha