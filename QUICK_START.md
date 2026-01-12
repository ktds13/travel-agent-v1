# Quick Start Guide - Travel Agent with Mode-Based Agents

## Prerequisites
- Docker Desktop running
- Python 3.11+ installed locally
- PostgreSQL database (via Docker)

## Option 1: Run Locally (Recommended for Development)

### 1. Start Database Only
```powershell
docker-compose up -d postgres
```

### 2. Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run the Application

#### CLI Mode (Interactive):
```powershell
python main_travel.py
```

#### API Mode:
```powershell
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

#### Test Mode-Based System:
```powershell
python test_modes.py
```

### 4. Check Database Status
```powershell
docker ps
# Should show travel-agent-db as healthy
```

### 5. Stop Database When Done
```powershell
docker-compose down
```

## Option 2: Full Docker Setup (Production)

**Note:** Building the full Docker image takes 10-15 minutes due to large dependencies (PyTorch, transformers, etc.)

### 1. Build and Run All Services
```powershell
docker-compose up -d
```

### 2. Check Logs
```powershell
docker-compose logs -f app
```

### 3. Access the Application
- API: http://localhost:8000
- Health Check: http://localhost:8000/health
- API Docs: http://localhost:8000/docs

### 4. Stop All Services
```powershell
docker-compose down
```

## Current Status

✅ **Database**: Running (PostgreSQL with pgvector)
```
Container: travel-agent-db
Status: healthy
Port: 5432
```

⏳ **Application**: Can be run locally or via Docker

## Quick Commands

```powershell
# Check what's running
docker ps

# View database logs
docker logs travel-agent-db

# Access database shell
docker exec -it travel-agent-db psql -U postgres -d travel_db

# Rebuild app only (if needed)
docker-compose build app

# Start app only (requires database running)
docker-compose up -d app

# View all services status
docker-compose ps

# Clean everything
docker-compose down -v
```

## Environment Variables

Key variables in `.env`:
- `DB_HOST=postgres` (for Docker) or `DB_HOST=localhost` (for local)
- `GROQ_API_KEY` - for LLM classification
- `AZURE_OPENAI_*` - for Azure OpenAI models
- `EMBEDDING_MODEL` - for sentence embeddings

## Mode-Based Agent Features

Once running, the system supports 5 modes:
1. **itinerary** - Day-by-day travel plans
2. **suggest_places** - Destination recommendations
3. **describe_place** - Detailed place information  
4. **activity_focused** - Activity-based planning
5. **comparison** - Side-by-side comparisons

The mode is automatically detected from your query!

## API Examples

```bash
# Auto-detect mode
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Plan a 3-day trip to Chiang Mai"}'

# List available modes
curl http://localhost:8000/modes

# Health check
curl http://localhost:8000/health
```

## Troubleshooting

### Database won't start
```powershell
docker-compose down -v
docker-compose up -d postgres
```

### Port 5432 already in use
Stop local PostgreSQL or change port in `.env`:
```
DB_PORT=5433
```

### Docker build too slow
Run locally instead (Option 1 above)

### Import errors
```powershell
pip install --upgrade -r requirements.txt
```

## Next Steps

1. ✅ Database is running
2. ⏭️ Choose: Run locally (fast) or Docker (isolated)
3. 📝 Test mode-based agents with `python test_modes.py`
4. 🚀 Try the API or CLI

For detailed documentation, see:
- [MODE_BASED_AGENTS.md](MODE_BASED_AGENTS.md) - Complete documentation
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference
