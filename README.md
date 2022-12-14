# CSC302 Project

## Top-level directory layout

```
    .
    ├── .github/workflows           # Github action files
    ├── docs                        # Documentation files
    ├── src                         # Python source files
    └── README.md
```
### Key Links:
- **[Documentation](docs/Documentation.md)**
- **[Roadmap](docs/Roadmap/)**
- **[Collected Meeting Notes Folder](docs/Meeting-Notes/)**

### Testing:
- Testing is automated with python script to check application with dummy inputs
- Done every push with github actions

![Testing and Docker Workflow](https://github.com/jaredtanzd/CSC302/actions/workflows/docker-image.yml/badge.svg)

## How to Run

1. Install docker from https://docs.docker.com/get-docker/
2. Verify docker version and login
    ```sh
    docker version
    docker login
    ```
3. Pull image from docker repository
    ```sh
    docker pull jared2812/csc302:latest
    ```
4. Run docker image
    ```sh
    docker run -p 8050:8050 -d jared2812/csc302:latest
    ```
5. View Dashboard at http://0.0.0.0:8050/ (Wait for a few minutes for the model to generate the results)
6. View containers 
    ```sh
    docker ps
    ```
7. Stop container
    ```sh
    docker stop [container id]
    ```
    
