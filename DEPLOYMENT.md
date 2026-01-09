# Deployment Guide

This guide explains how to deploy the Travel Agent AI System using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- 10GB+ disk space

## Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/ktds13/travel-agent-v1.git
cd travel-agent-v1
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your actual API keys and configuration
```

3. **Start the services**
```bash
# Start with PostgreSQL
docker-compose up -d

# Or start with SQL Server
docker-compose --profile sqlserver up -d
```

4. **Verify services are running**
```bash
docker-compose ps
```

5. **Access the API**
```
http://localhost:8000
```

## Service Profiles

### Default Profile (PostgreSQL)
```bash
docker-compose up -d
```
Includes:
- PostgreSQL with pgvector
- Travel Agent API

### SQL Server Profile
```bash
docker-compose --profile sqlserver up -d
```
Includes:
- SQL Server 2022
- Travel Agent API (configured for SQL Server)

### Data Ingestion Profile
```bash
docker-compose --profile data-ingestion up
```
Runs the data ingestion service for batch processing.

## Configuration

### Environment Variables

Edit `.env` file with your configuration:

**Required:**
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint
- `GROQ_API_KEY` - Your Groq API key

**Optional:**
- `DB_HOST` - Database host (default: postgres)
- `DB_PORT` - Database port (default: 5432)
- `DB_NAME` - Database name (default: travel_db)
- `DB_USER` - Database user (default: postgres)
- `DB_PASSWORD` - Database password (default: postgres)
- `EMBEDDING_MODEL` - Embedding model (default: sentence-transformers/LaBSE)

## Database Initialization

The database is automatically initialized with the schema on first start.

### PostgreSQL
- Creates tables with pgvector extension
- Seeds common countries and aliases
- Creates indexes for optimal performance

### SQL Server
- Creates tables with VARBINARY for embeddings
- Includes foreign key constraints
- Optimized for similarity search

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Travel Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "I want to visit beaches in Thailand"}'
```

### Data Ingestion
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"text": "The Merlion is the iconic symbol of Singapore..."}'
```

## Monitoring

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f postgres
```

### Check container status
```bash
docker-compose ps
```

### Resource usage
```bash
docker stats
```

## Scaling

### Scale the application
```bash
docker-compose up -d --scale app=3
```

### Add a load balancer
Add nginx service to `docker-compose.yml` for load balancing multiple app instances.

## Backup and Restore

### Backup PostgreSQL
```bash
docker exec travel-agent-db pg_dump -U postgres travel_db > backup.sql
```

### Restore PostgreSQL
```bash
docker exec -i travel-agent-db psql -U postgres travel_db < backup.sql
```

### Backup SQL Server
```bash
docker exec travel-agent-sqlserver /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P 'YourPassword' \
  -Q "BACKUP DATABASE TravelAgentDB TO DISK='/var/opt/mssql/backup.bak'"
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs app

# Rebuild image
docker-compose build --no-cache app
docker-compose up -d
```

### Database connection issues
```bash
# Check database is healthy
docker-compose ps postgres

# Test connection
docker exec travel-agent-db psql -U postgres -d travel_db -c "SELECT 1"
```

### Out of memory
```bash
# Increase Docker memory limit in Docker Desktop settings
# Or add memory limits to docker-compose.yml
```

## Production Deployment

### Security Recommendations

1. **Use secrets management**
   - Use Docker secrets or environment variable encryption
   - Never commit `.env` file

2. **Enable HTTPS**
   - Add nginx reverse proxy with SSL/TLS
   - Use Let's Encrypt for certificates

3. **Database security**
   - Use strong passwords
   - Enable SSL connections
   - Restrict network access

4. **Resource limits**
   - Set CPU and memory limits in docker-compose.yml
   - Monitor resource usage

5. **Regular updates**
   - Keep Docker images updated
   - Update Python dependencies regularly

### Example Production docker-compose.yml snippet
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

## Cloud Deployment

### AWS ECS
1. Push images to Amazon ECR
2. Create ECS task definitions
3. Deploy with ECS service

### Azure Container Instances
```bash
az container create \
  --resource-group travel-agent-rg \
  --name travel-agent \
  --image your-registry/travel-agent:latest \
  --environment-variables $(cat .env)
```

### Google Cloud Run
```bash
gcloud run deploy travel-agent \
  --image gcr.io/project/travel-agent:latest \
  --platform managed \
  --env-vars-file .env.yaml
```

## Maintenance

### Stop services
```bash
docker-compose down
```

### Remove volumes (CAUTION: deletes data)
```bash
docker-compose down -v
```

### Update application
```bash
git pull
docker-compose build
docker-compose up -d
```

### Clean up
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune
```
