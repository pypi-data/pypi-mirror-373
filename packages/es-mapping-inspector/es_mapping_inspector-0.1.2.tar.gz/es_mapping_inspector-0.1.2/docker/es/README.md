# Elasticsearch & Kibana - Local Development Setup

This directory provides a modular Docker Compose setup for running a local Elasticsearch and Kibana stack for development and testing purposes.

---

## Contents

- `docker-compose.es.yml`: Docker Compose configuration for Elasticsearch and Kibana.
- `.env.es`: Environment variables controlling versioning, port mappings, and memory settings.
- `elasticsearch.yml` *(optional)*: Custom Elasticsearch configuration file (can be omitted if not needed).

---

## Getting Started

### 1. Clone and Navigate

Make sure you're in the `docker/es/` directory:
```bash
cd docker/es/
```

### 2. Start the Stack

Use Docker Compose with the `.env.es` file:
```bash
docker-compose --env-file .env.es -f docker-compose.es.yml up
```

This will:
- Start an Elasticsearch container accessible on `localhost:9200`
- Start a Kibana container accessible on `localhost:5601`

---

## Configuration

### `.env.es`
Controls versioning and ports:
```env
ES_VERSION=8.12.2
KIBANA_VERSION=8.12.2
ES_JAVA_OPTS=-Xms1g -Xmx1g
ES_PORT=9200
KIBANA_PORT=5601
```

### `elasticsearch.yml` (optional)
Use this file to extend low-level Elasticsearch config (e.g., custom log paths, cluster settings).

---

## Health Checks

Elasticsearch includes a built-in health check that waits for the cluster to be responsive on `/ _cluster /health`.

---

## Stopping & Cleaning Up

To stop and remove the containers:
```bash
docker-compose --env-file .env.es -f docker-compose.es.yml down
```
To also remove persistent volumes:
```bash
docker-compose --env-file .env.es -f docker-compose.es.yml down -v
```

---

## Tips for Integration Testing

- This stack is intended for **local development** only. It disables security (`xpack.security.enabled=false`) and enables permissive CORS.
- For integration with other services (e.g., Dagster), make sure they use the same Docker network (`elastic`).

---

## Troubleshooting

- **Port conflicts**: Ensure ports `9200` and `5601` are free.
- **Out of memory**: Adjust `ES_JAVA_OPTS` in `.env.es` to fit your system.
- **Permissions issues on mounted volumes**: Run Docker with appropriate user/group permissions on your system.

---

## Volume Location

Elasticsearch data is stored in the Docker volume `esdata1`. You can inspect or remove it with:
```bash
docker volume ls
docker volume rm docker_es_esdata1
```

---

## Security Disclaimer

**Do not reuse this configuration in production.** It disables authentication and uses open CORS headers for development flexibility.
