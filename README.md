# Average Rates API

This project is a Flask-based API to fetch average prices between ports or regions.

## Prerequisites

- Docker
- Docker Compose
- **Dependency**: The project relies on the database and data schema provided by the [xeneta/ratestask](https://github.com/xeneta/ratestask) repository.

## Dependency Setup

### Cloning and Running the Required Database Container

This project depends on the database schema and data provided by the [xeneta/ratestask](https://github.com/xeneta/ratestask) repository. To set up the necessary database container:

1. **Clone the Repository and Build the Container**

    ```bash
    git clone https://github.com/xeneta/ratestask.git
    cd ratestask
    docker build -t ratestask .
    ```

2. **Run the Database Container**

    If the database container is not running yet:

    ```bash
    docker network create my_network
    docker run --network my_network -p 5432:5432 --name ratestask ratestask
    ```

    If the container is already running and needs to be connected to the network:

    ```bash
    docker network connect my_network ratestask
    ```

## Running the Application with Docker

### Steps

1. **Build and start the containers:**

    ```bash
    docker-compose up --build
    ```

2. **Access the API at** `http://127.0.0.1:5000`.

## API Endpoint

- **GET /rates**
  - **Parameters:**
    - `date_from`: The start date (YYYY-MM-DD).
    - `date_to`: The end date (YYYY-MM-DD).
    - `origin`: The origin port code or region slug.
    - `destination`: The destination port code or region slug.
  - **Response:**
    - A list of average prices for each day.

## Environment Variables

- `DATABASE_URL`: The database connection string. Example:

    ```
    DATABASE_URL=postgresql://postgres:ratestask@ratestask:5432/postgres
    ```

**Note**: For the sake of simplicity, the `DATABASE_URL` is provided directly in the `docker-compose.yml` file. However, in a production environment, it's recommended to store sensitive information like this in a `.env` file, which Docker Compose can automatically read.

**Example `.env` file**:

```
DATABASE_URL=postgresql://postgres@ratestask:5432/postgres
```

**Using `.env` in `docker-compose.yml`**:
```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    networks:
      - my_network
```

## Testing

To run tests inside the Docker container:

1. **Use Docker Compose to run tests:**

    ```bash
    docker-compose up test
    ```

This command starts a test service that runs `pytest` against the codebase.
