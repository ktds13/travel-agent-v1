# Quick Reference: Mode-Based Agents

## Import Statements

```python
# For automatic mode detection
from agents import create_travel_agent_for_query

# For direct mode creation
from agents import create_agent_for_mode
from agents.factory import GenerationMode

# For mode classification only
from utils.intent import classify_generation_mode

# For listing modes
from agents.factory import list_available_modes
```

## Usage Patterns

### Pattern 1: Auto-Detect Mode (Recommended)
```python
agent, mode = create_travel_agent_for_query(query)
result = agent.run(query)
print(f"Used mode: {mode}")
```

### Pattern 2: Explicit Mode Selection
```python
agent = create_agent_for_mode(GenerationMode.ITINERARY)
result = agent.run(query)
```

### Pattern 3: Manual Override
```python
agent, mode = create_travel_agent_for_query(
    query="Tell me about Thailand",
    mode="suggest_places"  # Override detection
)
```

### Pattern 4: Classify Only
```python
classification = classify_generation_mode(query)
mode = classification["generation_mode"]
days = classification.get("days")
```

## Mode Cheat Sheet

| Query Type | Mode | Example |
|------------|------|---------|
| "Plan a X-day trip" | `itinerary` | "Plan a 3-day trip to Chiang Mai" |
| "What/Which places" | `suggest_places` | "What beaches should I visit?" |
| "Tell me about X" | `describe_place` | "Tell me about Doi Suthep" |
| "Where can I [activity]" | `activity_focused` | "Where can I go hiking?" |
| "Compare X and Y" | `comparison` | "Compare Phuket and Krabi" |

## API Endpoints

### POST /query
```bash
# Auto-detect
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Plan a 3-day trip to Chiang Mai"}'

# With mode override
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Thailand", "mode": "suggest_places"}'
```

### GET /modes
```bash
curl http://localhost:8000/modes
```

### GET /tools
```bash
curl http://localhost:8000/tools
```

## CLI Commands

```bash
# Run interactive mode
python main_travel.py

# Run tests
python test_modes.py

# Start API server
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## Mode Configurations

| Mode | Tools (2) | Max Steps | Token Savings |
|------|-----------|-----------|---------------|
| itinerary | extract + generate_itinerary | 8 | ~40% |
| suggest_places | extract + suggest_places | 6 | ~44% |
| describe_place | extract + describe_place | 6 | ~44% |
| activity_focused | extract + plan_activity | 8 | ~35% |
| comparison | extract + compare_places | 6 | ~40% |

## Common Scenarios

### Scenario 1: CLI Interactive Session
```
You: Plan a 5-day trip to Chiang Mai with hiking
Mode detected: itinerary
[Agent creates day-by-day plan]

You: What temples should I visit?
Mode detected: suggest_places
[Agent suggests temples]
```

### Scenario 2: API Integration
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "Plan a 3-day trip to Chiang Mai"}
)

data = response.json()
print(f"Mode: {data['mode']}")
print(f"Response: {data['response']}")
```

### Scenario 3: Custom Application
```python
from agents import create_travel_agent_for_query

queries = [
    "Plan a 3-day trip to Chiang Mai",
    "What beaches are in Thailand?",
    "Tell me about Doi Suthep"
]

for query in queries:
    agent, mode = create_travel_agent_for_query(query)
    print(f"\nQuery: {query}")
    print(f"Mode: {mode}")
    result = agent.run(query)
    print(f"Result: {result[:100]}...")
```

## Troubleshooting

### Issue: Wrong mode detected
**Solution:** Use explicit mode override
```python
agent, mode = create_travel_agent_for_query(query, mode="itinerary")
```

### Issue: Import error
**Solution:** Ensure you're in the project root
```bash
cd d:\ktds\AI\travel_agent
python -c "from agents import create_travel_agent_for_query; print('OK')"
```

### Issue: LLM classification fails
**Solution:** Check .env file for API keys
```bash
cat .env | grep GROQ_API_KEY
```

## Performance Tips

1. **Reuse agents** for same mode if processing multiple queries
2. **Use explicit mode** when you know the query type (skips classification)
3. **Cache agents** by mode for high-traffic applications
4. **Monitor token usage** with API logging

## Files Reference

| File | Purpose |
|------|---------|
| [agents/factory.py](agents/factory.py) | Agent factory & configurations |
| [utils/intent.py](utils/intent.py) | Mode classification logic |
| [config/prompts.py](config/prompts.py) | Mode-specific instructions |
| [agents/travel_agent.py](agents/travel_agent.py) | Helper functions |
| [test_modes.py](test_modes.py) | Test suite & examples |
| [MODE_BASED_AGENTS.md](MODE_BASED_AGENTS.md) | Full documentation |

---
For detailed documentation, see [MODE_BASED_AGENTS.md](MODE_BASED_AGENTS.md)
