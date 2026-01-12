# Mode-Based Agent Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION LAYER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────────────────┐  │
│  │              │      │              │      │                          │  │
│  │  CLI (REPL)  │      │  REST API    │      │  Programmatic Usage      │  │
│  │              │      │              │      │                          │  │
│  │ main_travel  │      │   api.py     │      │  from agents import ...  │  │
│  │     .py      │      │              │      │                          │  │
│  │              │      │              │      │                          │  │
│  └──────┬───────┘      └──────┬───────┘      └──────────┬───────────────┘  │
│         │                     │                         │                   │
│         └─────────────────────┴─────────────────────────┘                   │
│                                 │                                           │
└─────────────────────────────────┼───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AGENT CREATION LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                   create_travel_agent_for_query(query, mode?)               │
│                          [agents/travel_agent.py]                            │
│                                                                              │
│         ┌────────────────────────────┬────────────────────────────┐         │
│         │                            │                            │         │
│         ▼                            ▼                            ▼         │
│  ┌─────────────┐             ┌──────────────┐           ┌─────────────┐    │
│  │   Manual    │             │  Classify    │           │   Direct    │    │
│  │   Mode      │             │    Query     │           │   Factory   │    │
│  │  Override   │             │              │           │    Call     │    │
│  └──────┬──────┘             └──────┬───────┘           └──────┬──────┘    │
│         │                           │                          │            │
│         │                           ▼                          │            │
│         │              classify_generation_mode(query)         │            │
│         │                   [utils/intent.py]                  │            │
│         │                           │                          │            │
│         │                           ▼                          │            │
│         │               ┌───────────────────────┐              │            │
│         │               │   LLM Classification  │              │            │
│         │               │  (Groq llama-3.3-70b) │              │            │
│         │               └───────────┬───────────┘              │            │
│         │                           │                          │            │
│         │                           ▼                          │            │
│         │                  {"generation_mode": "...",          │            │
│         │                   "days": ...}                       │            │
│         │                           │                          │            │
│         └───────────────────────────┴──────────────────────────┘            │
│                                     │                                       │
│                                     ▼                                       │
│                       get_mode_from_string(mode_str)                        │
│                          [agents/factory.py]                                │
│                                     │                                       │
│                                     ▼                                       │
│                           GenerationMode enum                               │
│                                     │                                       │
└─────────────────────────────────────┼───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGENT FACTORY LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                   create_agent_for_mode(mode, deployment)                   │
│                          [agents/factory.py]                                │
│                                     │                                       │
│                                     ▼                                       │
│                            MODE_CONFIGS[mode]                               │
│                                     │                                       │
│         ┌───────────────────────────┼───────────────────────────┐           │
│         │                           │                           │           │
│         ▼                           ▼                           ▼           │
│   ┌─────────┐               ┌──────────────┐           ┌──────────────┐    │
│   │  Tools  │               │ Instructions │           │  Max Steps   │    │
│   │  List   │               │   (Prompts)  │           │   Setting    │    │
│   └────┬────┘               └──────┬───────┘           └──────┬───────┘    │
│        │                           │                          │            │
│        └───────────────────────────┴──────────────────────────┘            │
│                                    │                                       │
│                                    ▼                                       │
│                          ToolCallingAgent()                                │
│                       [smolagents library]                                 │
│                                    │                                       │
└────────────────────────────────────┼───────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MODE-SPECIFIC AGENTS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Itinerary   │  │   Suggest    │  │  Describe    │  │  Activity    │   │
│  │    Agent     │  │    Places    │  │    Place     │  │   Focused    │   │
│  │              │  │    Agent     │  │    Agent     │  │    Agent     │   │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤   │
│  │ Tools: 2     │  │ Tools: 2     │  │ Tools: 2     │  │ Tools: 2     │   │
│  │ Steps: 8     │  │ Steps: 6     │  │ Steps: 6     │  │ Steps: 8     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │                 │            │
│         └─────────────────┴─────────────────┴─────────────────┘            │
│                                    │                                       │
│                      ┌──────────────┴──────────────┐                       │
│                      │                             │                       │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐       │
│  │      Comparison Agent        │  │      (Future modes...)       │       │
│  │                              │  │                              │       │
│  ├──────────────────────────────┤  └──────────────────────────────┘       │
│  │ Tools: 2                     │                                         │
│  │ Steps: 6                     │                                         │
│  └──────────────┬───────────────┘                                         │
│                 │                                                          │
└─────────────────┼──────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TOOL EXECUTION LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────┐  ┌────────────────────────┐                    │
│  │  extract_travel_query  │  │  Mode-Specific Tool    │                    │
│  │   (Always included)    │  │  (Based on mode)       │                    │
│  └───────────┬────────────┘  └────────┬───────────────┘                    │
│              │                        │                                     │
│              ▼                        ▼                                     │
│  ┌─────────────────────────────────────────────────────┐                   │
│  │        Database & RAG Operations                    │                   │
│  │  [database/*, utils/rag.py, utils/intent.py]       │                   │
│  └────────────────────┬────────────────────────────────┘                   │
│                       │                                                     │
│                       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐                   │
│  │        LLM Generation (Groq/Azure OpenAI)          │                   │
│  │           [core/llm.py, core/models.py]            │                   │
│  └────────────────────┬────────────────────────────────┘                   │
│                       │                                                     │
└───────────────────────┼─────────────────────────────────────────────────────┘
                        │
                        ▼
                  Final Response


┌─────────────────────────────────────────────────────────────────────────────┐
│                       MODE CONFIGURATION DETAILS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  itinerary          → [extract, generate_itinerary]     (40% token savings) │
│  suggest_places     → [extract, suggest_places]         (44% token savings) │
│  describe_place     → [extract, describe_place]         (44% token savings) │
│  activity_focused   → [extract, plan_activity_trip]     (35% token savings) │
│  comparison         → [extract, compare_places]         (40% token savings) │
│                                                                              │
│  All modes use specialized instructions from config/prompts.py              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Flow Example: "Plan a 3-day trip to Chiang Mai"

```
1. User → CLI/API → create_travel_agent_for_query(query)
                              ↓
2. classify_generation_mode("Plan a 3-day trip to Chiang Mai")
                              ↓
3. LLM → {"generation_mode": "itinerary", "days": 3}
                              ↓
4. get_mode_from_string("itinerary") → GenerationMode.ITINERARY
                              ↓
5. create_agent_for_mode(GenerationMode.ITINERARY)
                              ↓
6. MODE_CONFIGS[ITINERARY] → {
     tools: [extract_travel_query, generate_travel_itinerary],
     instructions: ITINERARY_MODE_INSTRUCTIONS,
     max_steps: 8
   }
                              ↓
7. ToolCallingAgent created with 2 tools (not all 6)
                              ↓
8. agent.run("Plan a 3-day trip to Chiang Mai")
                              ↓
9. Tool 1: extract_travel_query → fetch places from DB
10. Tool 2: generate_travel_itinerary → create day-by-day plan
                              ↓
11. Final Response → User
```

## Key Benefits Illustrated

```
Traditional Approach:
┌────────────────────────────┐
│   Single Agent (6 tools)   │  → Higher token cost
│   Generic instructions     │  → Slower execution
│   All queries use same     │  → Less focused
└────────────────────────────┘

Mode-Based Approach:
┌────────────────────────────┐
│ Mode-Specific Agent (2 t.) │  → 40-44% less tokens
│ Focused instructions       │  → 29-34% faster
│ Optimized for query type   │  → More accurate
└────────────────────────────┘
```
