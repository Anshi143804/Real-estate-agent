# Nova — AI Voice Real Estate Agent

A production-ready, browser-based AI voice agent for real estate that engages with potential buyers through natural conversation, collects their property requirements, performs intelligent property searches, compares listings, schedules viewings, and generates detailed call summaries.

Built with **FastAPI**, **Pipecat** (voice pipelines + WebRTC), **Google Gemini**, **Deepgram** (speech-to-text), **Cartesia** (text-to-speech), and **PostgreSQL**.

---

## Overview

**Nova** automates the initial buyer engagement workflow in real estate:

1. **Greets prospects** – Natural phone conversation with a human-like voice
2. **Collects requirements** – Understands buyer preferences (budget, location, property type, features)
3. **Searches properties** – Queries the property database based on buyer criteria
4. **Discusses listings** – Explains property details, pricing, and availability
5. **Compares options** – Side-by-side comparison of properties the buyer is interested in
6. **Schedules viewings** – Books property viewings with buyer availability
7. **Analyzes calls** – Extracts insights and conversation summaries
8. **Generates reports** – Delivers structured call records and buyer profiles

---

## Key Features

- ✅ **Real-time voice interaction** – Bidirectional audio with human-like responses
- ✅ **Natural language understanding** – Powered by Google Gemini 2.5 Flash
- ✅ **Property database integration** – PostgreSQL backend with buyer/property/viewing models
- ✅ **Multi-step conversation flows** – Pipecat flow manager for conversation state management
- ✅ **Tool calling & actions** – LLM-driven property searches, comparisons, viewing scheduling
- ✅ **Web UI** – Simple, responsive HTML/CSS/JS frontend with transcript and activity logs
- ✅ **Call analysis** – Automated post-call summaries and buyer lead scoring
- ✅ **Extensible architecture** – Modular services and tools for custom workflows

---

## Tech Stack

| Component | Technology |
|---|---|
| **Web Framework** | FastAPI 0.116+ |
| **Voice Pipeline** | Pipecat 1.5+ (WebRTC, VAD, LLM context) |
| **LLM** | Google Gemini 2.5 Flash |
| **Speech-to-Text** | Deepgram Nova-2 |
| **Text-to-Speech** | Cartesia AI |
| **Database** | PostgreSQL 14+ |
| **ORM** | SQLAlchemy 2.0 |
| **Package Manager** | uv |
| **Frontend** | HTML5, CSS3, vanilla JavaScript (no build step) |

---

## Project Structure

```
Real estate agent/
├── app/                           # Main application package
│   ├── main.py                    # FastAPI app entry point, WebRTC endpoints
│   ├── bot.py                     # Pipecat pipeline setup, voice agent logic
│   ├── config.py                  # Environment variable validation & config
│   ├── db/                        # Database layer
│   │   ├── database.py            # SQLAlchemy session & connection
│   │   ├── create_tables.py       # Schema initialization
│   │   ├── schema.sql             # Raw SQL schema (buyers, properties, viewings, etc.)
│   │   ├── models/                # SQLAlchemy ORM models
│   │   │   ├── buyer.py           # Buyer entity, demographics, preferences
│   │   │   ├── property.py        # Property listing, details, status
│   │   │   ├── conversation.py    # Call records, transcript, duration
│   │   │   ├── viewing.py         # Scheduled viewings, status, timestamps
│   │   │   ├── evaluation.py      # Property valuations & assessments
│   │   │   ├── valuation.py       # Valuation records & price estimates
│   │   │   ├── seller.py          # Seller info for sold properties
│   │   │   └── enums.py           # Shared enums (PropertyType, Status, etc.)
│   │   └── crud/                  # Database CRUD operations
│   │       ├── buyer.py           # Create/read buyer records
│   │       ├── property.py        # Query properties, filter, search
│   │       ├── viewing.py         # Create/update viewing bookings
│   │       ├── conversation.py    # Log calls, retrieve call history
│   │       ├── evaluation.py      # Manage property evaluations
│   │       ├── valuation.py       # Record & retrieve valuations
│   │       ├── seller.py          # Seller record operations
│   │       └── common.py          # Shared DB utilities
│   ├── flows/                     # Conversation flow orchestration
│   │   ├── buyer_flow.py          # Multi-node conversation graph (greeting → closing)
│   │   ├── handlers.py            # Handler functions mapped to flow actions
│   │   ├── prompts.py             # System prompts for each conversation stage
│   │   └── schemas.py             # Pydantic schemas for tool outputs & validation
│   ├── services/                  # Business logic services
│   │   ├── logger.py              # Pipecat event logging & transcript capture
│   │   ├── event_bridge.py        # Event observer for pipeline events
│   │   ├── call_analysis.py       # Post-call analysis, lead scoring
│   │   ├── call_usage.py          # Track API usage (Gemini, Deepgram, Cartesia)
│   │   ├── evaluation_service.py  # Property evaluation scoring
│   │   └── logger.py              # Logging configuration
│   ├── tools/                     # LLM tool definitions for Pipecat
│   │   ├── registry.py            # Tool registration & manifest
│   │   └── buyer/                 # Buyer-facing tools
│   │       ├── property_search.py     # Tool: search properties by criteria
│   │       ├── property_details.py    # Tool: fetch property information
│   │       ├── property_comparison.py # Tool: compare 2+ properties
│   │       ├── schedule_viewing.py    # Tool: book property viewing
│   │       └── finalise_conversation.py # Tool: end call, generate summary
│   ├── schemas/                   # Pydantic models for API & LLM
│   │   └── buyer/
│   │       ├── property_search.py     # Property search criteria & results
│   │       ├── property_details.py    # Structured property info
│   │       ├── property_comparison.py # Multi-property comparison
│   │       ├── lead_summary.py        # Post-call lead summary
│   │       ├── conversation_report.py # Full call transcript & metadata
│   │       └── viewing.py             # Viewing request/confirmation schema
│   ├── frontend/                  # Web UI (served by FastAPI)
│   │   ├── index.html             # Main page with voice orb, transcript, properties
│   │   ├── app.js                 # WebRTC client, call control, UI interactivity
│   │   ├── config.js              # Frontend configuration (API endpoints)
│   │   ├── style.css              # UI styling
│   │   └── frontend.py            # Utility script (optional)
│   └── pyproject.toml             # uv project config
├── db.py                          # Root database utility script
├── request_handler.py             # External request handling (optional)
├── requirements.txt               # Legacy pip requirements
├── pyproject.toml                 # Root project config

```

---

## 1. Prerequisites

## 1. Prerequisites

Install these before you start:

| Requirement | Notes |
|---|---|
| **Python 3.12+** | `python3 --version` to check |
| **[uv](https://docs.astral.sh/uv/)** | Package manager used by this project. Install: `curl -LsSf https://astral.sh/uv/install.sh \| sh` (macOS/Linux) or see the uv docs for Windows |
| **PostgreSQL 14+** | Local install, Docker container, or a hosted instance (Supabase, RDS, etc.) |
| **A modern browser** | Chrome, Edge, or Firefox — needs microphone + WebRTC support |
| **API keys** (see below) | Google Gemini, Deepgram, Cartesia — all have free tiers |

### API Keys Required

You'll need accounts / API keys from:
- **Google AI Studio** → Gemini API key → https://aistudio.google.com/apikey
- **Deepgram** (speech-to-text) → https://console.deepgram.com/
- **Cartesia** (text-to-speech) → https://play.cartesia.ai/

All three services offer **free-tier credits** for development.

---

## 2. Get the Code

Unzip the project, then open a terminal in the project root — the folder
that contains `pyproject.toml` and the `app/` directory:

```bash
cd "Real estate agent"
```

---

## 3. Install Dependencies

This project uses `uv` and includes a lockfile, so this one command sets
up an isolated virtual environment and installs everything pinned in
`uv.lock`:

```bash
uv sync
```

This creates a `.venv/` folder in the project root. You don't need to
activate it manually — `uv run ...` (used below) does that automatically.

<details>
<summary>Prefer plain pip / venv instead of uv?</summary>

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Every `uv run <command>` in this README then becomes just `<command>` with
the venv activated.
</details>

---

## 4. Set up PostgreSQL

You need an empty PostgreSQL database, plus the schema in
`app/db/schema.sql` loaded into it.

**Option A — you already have Postgres running locally:**

```bash
createdb estate_ai
psql -d estate_ai -f app/db/schema.sql
```

**Option B — spin up Postgres with Docker (no local install needed):**

```bash
docker run --name nova-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=estate_ai \
  -p 5432:5432 \
  -d postgres:16

psql -h localhost -U postgres -d estate_ai -f app/db/schema.sql
```

`schema.sql` creates tables for properties, buyers, viewings, conversations, evaluations, and valuations. It requires the `uuid-ossp` Postgres extension — the script enables it for you (`CREATE EXTENSION IF NOT EXISTS "uuid-ossp"`).

### Load Sample Properties

The agent has nothing to search until the `properties` table has rows. Insert test properties:

```sql
INSERT INTO properties (listing_id, title, description, price, currency,
  property_type, listing_type, status, bedrooms, bathrooms, address, city, postcode)
VALUES 
  ('LST-001', 'Modern 3-bed apartment', 'Bright apartment near the park.',
    450000, 'GBP', 'apartment', 'sale', 'available', 3, 2,
    '12 Riverside Rd', 'London', 'SW1A 1AA'),
  ('LST-002', 'Victorian 4-bed house', 'Spacious period home with garden.',
    650000, 'GBP', 'house', 'sale', 'available', 4, 3,
    '45 Oak Street', 'London', 'SW1A 2AA'),
  ('LST-003', 'Cosy 2-bed flat', 'Modern flat in city centre.',
    350000, 'GBP', 'flat', 'sale', 'available', 2, 1,
    '78 High Street', 'London', 'EC1A 1BB');
```

---

## 5. Configure Environment Variables

Create a `.env` file in the project root (same folder as `pyproject.toml`):

```bash
cp .env.example .env    # if a .env.example exists
# otherwise, create .env manually with the content below
```

Fill in `.env`:

```ini
# --- Database Connection ---
DB_HOST=localhost
DB_PORT=5432
DB_NAME=estate_ai
DB_USER=postgres
DB_PASSWORD=postgres

# --- Google Gemini (LLM) ---
GEMINI_API_KEY=your_gemini_api_key_here

# --- Deepgram (Speech-to-Text) ---
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# --- Cartesia (Text-to-Speech) ---
CARTESIA_API_KEY=your_cartesia_api_key_here
CARTESIA_VOICE_ID=79a125e8-cd45-4c13-8a67-188112f4dd22   # Optional, has a default

# --- Optional ---
OPENAI_API_KEY=                # Fallback (not required)
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
```

**Required keys:** `GEMINI_API_KEY`, `DEEPGRAM_API_KEY`, `CARTESIA_API_KEY`  
The app will fail startup with a clear error if any are missing.

---

## 6. Run the Server

```bash
uv run python -m app.main
```

You should see log output similar to:

```
Starting Real Estate Voice Agent FastAPI server on http://0.0.0.0:7860
Uvicorn running on http://0.0.0.0:7860 (Press CTRL+C to quit)
```

Leave this running in the terminal.

---

## 7. Open the App in Your Browser

Navigate to:

```
http://localhost:7860
```

**Important:** Use `http://localhost:7860`, NOT a `file://` path or direct `index.html` open. The browser needs to be served by the FastAPI app for WebRTC and the `/offer` endpoint to work.

You should see the Nova UI with:
- A voice orb animation on the left
- An empty transcript panel on the right
- A **Start call** button

### Making Your First Call

1. **Click Start call** and allow microphone access when prompted
2. **Listen** — Nova greets you with a human-like voice
3. **Respond naturally** — describe what you're looking for
4. **Watch live** — Your words and Nova's replies appear in the Transcript tab; tool calls show in Activity; matching properties display as cards
5. **End the call** — Click the **End call** button (now red) to finish; a summary screen appears with conversation highlights and an option to download the call report

### Example Conversation Flow

```
Nova:  "Hello! Are you looking to buy, rent, or sell a property today?"
You:   "I'm looking to buy a 3-bedroom apartment in London under 500,000 pounds."
Nova:  "Great! Let me search for 3-bedroom apartments in London within your budget."
[Nova performs property search]
Nova:  "I found 3 apartments that match your criteria. The first is a modern 3-bed in Riverside..."
You:   "Can you compare it with other options?"
Nova:  "Of course! Here's how they compare..."
[Nova displays property comparison]
You:   "I'd like to schedule a viewing for the first one."
Nova:  "Perfect! What time works best for you?"
[Viewing is booked, summary generated]
```

---

## 8. Architecture & Data Flow

### High-Level Flow

```
Browser (WebRTC) 
    ↓
FastAPI (/offer, /connect endpoints)
    ↓
Pipecat Pipeline (VAD → STT → LLM → TTS)
    ↓
AI Services (Deepgram, Gemini, Cartesia)
    ↓
Tools (property_search, property_details, etc.)
    ↓
PostgreSQL (buyers, properties, viewings, etc.)
    ↓
EventBridge (sends events back to browser)
    ↓
Browser UI (transcript, properties, activity log)
```

### Key Components

| Component | Purpose |
|---|---|
| **app/main.py** | FastAPI server, serves frontend, handles WebRTC `/offer` and `/connect` endpoints |
| **app/bot.py** | Instantiates Pipecat pipeline: STT + LLM context + TTS + flow manager |
| **app/flows/buyer_flow.py** | Conversation state machine with nodes (greeting, requirements, discussion, comparison, viewing, closing) |
| **app/tools/buyer/\*.py** | Tool implementations called by LLM (property_search, schedule_viewing, etc.) |
| **app/db/** | SQLAlchemy models and CRUD operations for database access |
| **app/services/event_bridge.py** | Observes pipeline events, streams them to browser (live transcript, tool calls) |
| **app/frontend/** | HTML/CSS/JS UI (no build step, served as static assets) |

---

## 9. Troubleshooting

| Symptom | Cause & Solution |
|---|---|
| **Startup error:** `Missing required environment variables` | `.env` missing a required key or not in project root. Verify `GEMINI_API_KEY`, `DEEPGRAM_API_KEY`, `CARTESIA_API_KEY` are set. |
| **Startup error:** `psycopg.OperationalError: could not connect to server` | Postgres not running or connection details wrong. Check `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` in `.env`. Run `pg_isready` or `docker ps` to verify. |
| **Page loads but is unstyled/blank** | You opened `index.html` directly instead of navigating to `http://localhost:7860`. Always use the full URL. |
| **"Please allow microphone access" toast, call won't start** | Browser blocked the microphone prompt. Check site permissions in the address bar and allow microphone access. |
| **Call connects but Nova never speaks** | API error (invalid/rate-limited key). Check terminal output for Gemini/Deepgram/Cartesia errors. Verify API keys in `.env`. |
| **Nova speaks but finds no properties** | `properties` table is empty. Run the sample data INSERT statements from step 4. |
| **Port 7860 already in use** | Stop the process using port 7860, or change the port in `app/main.py` (search for `uvicorn.run`) and update `BACKEND_URL` in `app/frontend/config.js` to match. |
| **No properties appear in the UI** | Ensure browser DevTools are not blocking console errors, and check the browser console for JavaScript errors. |
| **Transcript appears but no tool calls** | Check that property records exist in the database and that the LLM is correctly routing to tool calls. Review server logs for Pipecat pipeline events. |

---

## 10. Development Workflow

### Adding a New Conversation Node

1. **Define prompts & schema** → Add to `app/flows/prompts.py` and `app/flows/schemas.py`
2. **Create a node config** → Add to `app/flows/buyer_flow.py` (returns `NodeConfig`)
3. **Implement handler** → Add handler function to `app/flows/handlers.py`, register in `HANDLERS` dict in `app/bot.py`
4. **Test** → Start the server and verify the flow transitions in the browser

### Adding a New Tool

1. **Create tool file** → `app/tools/buyer/my_tool.py` with a tool class inheriting from Pipecat's tool base
2. **Register the tool** → Add to tool registry in `app/tools/registry.py`
3. **Add schema** → Define Pydantic schema in `app/schemas/buyer/`
4. **Link to handler** → Create handler in `app/flows/handlers.py`, wire to flow node
5. **Test** → Verify tool is called correctly by the LLM

### Database Migrations

- **Schema changes** → Edit `app/db/schema.sql` and re-run against a test database
- **ORM model changes** → Update models in `app/db/models/` and corresponding CRUD in `app/db/crud/`
- **New tables** → Add table definition to `schema.sql`, create model + CRUD files

### Running Tests

```bash
uv run pytest tests/
```

Check [test_event_bridge_transcript.py](tests/test_event_bridge_transcript.py) for examples.

---

## 11. Production Deployment

### Environment Setup

- Use a cloud-hosted PostgreSQL instance (AWS RDS, Supabase, etc.)
- Store API keys securely (AWS Secrets Manager, environment variables, etc.)
- Deploy FastAPI app to a container runtime (Docker, Kubernetes, Cloud Run, etc.)
- Configure WebRTC ICE servers for peer discovery (update `app/frontend/config.js` if needed)

### Deployment Checklist

- [ ] Use production-grade database
- [ ] Rotate and secure all API keys
- [ ] Enable HTTPS for WebRTC connections
- [ ] Set appropriate `LOG_LEVEL` (INFO or WARNING)
- [ ] Configure CORS origins to your domain only
- [ ] Monitor API usage and costs (Gemini, Deepgram, Cartesia)
- [ ] Set up logging aggregation (CloudWatch, Stackdriver, etc.)
- [ ] Test WebRTC on target platforms (Chrome, Firefox, Safari)

### Docker Example

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
ENV PYTHONUNBUFFERED=1
CMD ["uv", "run", "python", "-m", "app.main"]
```

Build and run:

```bash
docker build -t nova-agent .
docker run -e GEMINI_API_KEY=... -e DEEPGRAM_API_KEY=... -e CARTESIA_API_KEY=... -p 7860:7860 nova-agent
```

---

## 12. API Reference

### REST Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Serves `index.html` |
| `/style.css` | GET | Serves stylesheet |
| `/app.js` | GET | Serves frontend JavaScript |
| `/config.js` | GET | Serves frontend config |
| `/offer` | POST | WebRTC offer handshake (starts voice call) |
| `/connect` | POST | Alternative connection endpoint |

### WebRTC Flow

1. Browser sends `/offer` with SDP offer
2. Server processes with Pipecat, returns SDP answer
3. WebRTC connection established
4. Audio frames flow bidirectionally
5. Browser receives transcript & event updates via EventBridge

---

## 13. Common Questions

**Q: Can I customize the conversation flow?**  
A: Yes! Modify `app/flows/buyer_flow.py` to add/remove nodes, change prompts in `prompts.py`, and update handlers in `handlers.py`.

**Q: How do I add more properties to the database?**  
A: Insert rows into the `properties` table using SQL `INSERT` or a script. Use CRUD functions in `app/db/crud/property.py`.

**Q: Can I use a different LLM instead of Gemini?**  
A: Yes, Pipecat supports multiple LLM providers. Update `app/bot.py` to use a different service (e.g., OpenAI, Anthropic).

**Q: What's included in the call summary?**  
A: The summary includes buyer preferences collected, properties discussed, comparisons made, viewings scheduled, and overall call duration. See `app/schemas/buyer/conversation_report.py`.

**Q: How do I debug a failed tool call?**  
A: Check server terminal logs for Pipecat pipeline events, browser console for JavaScript errors, and EventBridge output for tool execution status.

**Q: Is this production-ready?**  
A: The architecture is production-ready, but you should test WebRTC latency, API rate limits, error handling, and security before going live.

---

## 14. Support & Contributing

For issues, questions, or contributions:
- Check the troubleshooting section above
- Review server logs (`uv run python -m app.main`)
- Inspect browser console (F12) for client-side errors
- Review Pipecat documentation: https://github.com/dailyio/pipecat
- Check individual API service docs (Gemini, Deepgram, Cartesia)

---

## License

[Add your license here]

## Authors

Nova Real Estate Agent - Built with FastAPI, Pipecat, and modern AI voice technology.
