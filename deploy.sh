docker stop arashub
docker rm arashub
docker rmi arashub
docker build -t arashub .
docker run -d --name arashub -p 80:80 arashub