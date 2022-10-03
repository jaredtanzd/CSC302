# CSC302
CSC302 Project 

### Documentation

### Meeting Notes


### How to Run

1. Install docker from https://docs.docker.com/get-docker/
2. Verify docker version and login
    docker version
    docker login
3. Pull image from docker repository
    docker pull jared2812/csc302:latest
4. Run docker image
    docker run -p 8050:8050 -d jared2812/csc302:latest
5. View Dashboard at http://0.0.0.0:8050/
6. View containers 
    docker ps
7. Stop container
    docker stop [container id]
 
    
