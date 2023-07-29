docker stop arashub

docker rm arashub

docker rmi arashub

docker build -t arashub .

docker run -d --name arashub -p 55688:55688 --restart unless-stopped arashub