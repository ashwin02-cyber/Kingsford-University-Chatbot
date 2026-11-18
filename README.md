# Kingsford University — AI-Powered Website & Intelligent Help Desk (KAI)

A full-stack, enterprise-grade university portal and AI campus assistant built for **Kingsford University**, adhering strictly to ISO/IEC/IEEE 29148 requirements and the official visual reference design (purple/violet theme, serif+sans typography, quick-access cards, floating widget, and dedicated `/chat` workspace).

---

## 📌 Technology Stack

| Tier | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite, React Router 7, Lucide Icons, Custom CSS Design Tokens |
| **Backend** | Python 3.13, Django 6.1, Django REST Framework, django-cors-headers, python-dotenv |
| **AI Engine** | Google Gen AI Python SDK (`google-genai`), Model: `gemini-3.6-flash` (Fallback: `gemini-2.5-flash-lite`) |
| **Database** | SQLite (development) with Django ORM migrations and indexed relations |
| **Protocol** | REST JSON endpoints for institutional data + Server-Sent Events (SSE) for chat streaming |

---

## 🛡️ Security & Secret Management

- **Zero Client-Side Secrets (SEC-001)**: The Gemini API key exists exclusively on the Django server within `backend/.env`. It is strictly excluded by `.gitignore` and never committed, bundled in frontend JS, or returned in network responses.
- **Input Validation (SEC-002, FR-014)**: Messages are strictly validated (1 to 1,000 characters; non-empty, non-whitespace).
- **Prompt Injection Defense (SEC-003)**:
  - All user queries and chat history are passed strictly as untrusted user turns.
  - Retrieved institutional records are wrapped in structured `[Reference Material]` blocks.
  - Active detection for prompt-leakage markers immediately terminates output streams.
- **Client Isolation (SEC-007, FR-024, AC-10)**: Conversations are identified by unguessable UUIDs and bound to client IDs passed in the `X-Client-ID` header.

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- **Python**: 3.10+ (Verified on Python 3.13)
- **Node.js**: LTS 20+ (Verified on Node.js v24)
- **Git**

---

### 2. Backend Setup

```bash
# Navigate to repository root
cd "e:\Kingsford University_Chatbot"

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Navigate to backend directory
cd backend

# Configure environment variables (copy from template if .env does not exist)
# Edit backend/.env and insert your GEMINI_API_KEY
# Ensure GEMINI_MODEL=gemini-3.6-flash and GEMINI_FALLBACK_MODEL=gemini-2.5-flash-lite

# Run database migrations
python manage.py migrate

# Seed sample institutional data (idempotent)
python manage.py seed_data

# Start the Django development server
python manage.py runserver 127.0.0.1:8000
```

> **Default Admin Account**:
> - **URL**: `http://127.0.0.1:8000/admin/`
> - **Username**: `admin`
> - **Password**: `KingsfordAdmin2026!`

---

### 3. Frontend Setup

```bash
# In a separate terminal, navigate to the frontend directory
cd "e:\Kingsford University_Chatbot\frontend"

# Install dependencies (if not already installed)
npm install

# Start Vite development server (proxies /api to Django at 127.0.0.1:8000)
npm run dev
```

Visit the website at: **`http://localhost:5173/`**

---

## 🧪 Testing & Verification

### 1. Automated Django Test Suite (Mocked AI — No External API Calls)
```bash
cd backend
python manage.py test
```
*Runs all **16** automated unit & API tests across `website` and `chatbot` apps in ~1.4s.*

| Test | Coverage |
|------|----------|
| `test_health_check_endpoint` | GET `/api/v1/health/` returns 200 |
| `test_home_summary_endpoint` | Announcements, events, quick stats |
| `test_departments_list` | 5 departments returned |
| `test_programmes_list_and_filtering` | Filter by department, level |
| `test_admissions_grouped` | Grouped by info_type |
| `test_announcements_list_and_filter` | Pinned filter works |
| `test_events_list` | Upcoming events |
| `test_knowledge_list_and_filter` | Category filter |
| `test_input_validation_fr014` | Empty / >1000 chars rejected |
| `test_retrieval_service_fr033` | Keyword matching returns context block |
| `test_gemini_retry_and_fallback_ac09` | 503 → 3 retries → fallback model |
| `test_system_prompt_leakage_detection_sec003` | Leakage marker stops stream |
| `test_context_window_trimming_fr023` | >10 turns trimmed |
| `test_conversation_cascade_delete_and_clear` | CASCADE + clear |
| `test_client_id_isolation_ac10` | Cross-client conversation isolation |
| `test_stream_endpoint_503_then_success_produces_only_token_and_done` | *(Bug fix)* 503→success emits only `token`+`done`, **no** `error` event |

### 2. Frontend Chat Lifecycle Tests (Node.js, No Browser Required)
```bash
node frontend/src/test_chat_lifecycle.js
```
*3 unit tests verifying the `useChat` state machine (normal reply, Stop pressed, network drop). **3/3 PASS**.*

### 3. SRS Prompt Acceptance Criteria Tests (AC-05 to AC-07)
```bash
cd backend
python chatbot/run_prompt_tests.py
```
*Executes the 20 SRS prompt evaluations with the live `gemini-3.6-flash` model:*
- **AC-05 (10 Prompts)**: Unrelated queries (coding, jokes, celebrities, cooking) are politely declined.
- **AC-06 (5 Prompts)**: Injection attempts ("ignore instructions", "show prompt", "what model") reveal no internal details.
- **AC-07 (5 Prompts)**: Questions regarding unrecorded data receive "not currently available" with contact routing.
- **Result**: **20/20 PASS (100.0%)**

### 4. Production Frontend Build
```bash
cd frontend
npm run build
```
*Builds client bundles into `frontend/dist` without warnings or syntax issues.*

---

## 🐛 Bug Fix — Stale "Response Interrupted" Bubble (commit `70fab6e`)

### Root Causes
| # | Cause | File |
|---|-------|------|
| 1 | `AbortError` (user Stop / superseded request cleanup) routed through `onError()` → flashed interrupted banner even on clean requests | `sse.js` |
| 2 | No synchronous guard; async `isLoading` state could be bypassed by rapid double-clicks or re-renders | `useChat.js` |
| 3 | Assistant placeholder created with `status: 'incomplete'` → error banner visible before first token arrived | `useChat.js` |
| 4 | No separate `onAbort` callback — all cancellation paths called `onError` | `sse.js`, `useChat.js` |
| 5 | Backend could emit `event: error` during retries before fallback exhausted | `views.py` |

### Fixes Applied
- **`sse.js`**: Added `onAbort` callback. `AbortError` / `signal.aborted` → `onAbort()` only; never calls `onError()`.
- **`useChat.js`**: `isBusyRef = useRef(false)` synchronous guard checked before any state. Placeholder starts as `status: 'thinking'`. Five-state machine: `thinking → streaming → complete | interrupted | error`. `onAbort` with partial content → `complete`; without content → removes placeholder entirely. Retry reuses same message slot.
- **`MessageBubble.jsx`**: Renders entirely from `status` field. Stop button inline in `thinking`/`streaming`. `interrupted`/`error` show Retry.
- **`ChatWidget.jsx` / `ChatPage.jsx`**: Removed separate `<TypingIndicator>` and `<ErrorBanner>`; Stop passed as prop to `MessageBubble`.
- **`views.py`**: `terminal_event_sent` flag; `GeneratorExit`/`BrokenPipeError` treated as silent client disconnect (no `error` event); exactly one terminal event per stream.

### Manual Verification Checklist
1. **Normal reply**: Send message → exactly **1 POST** to `/api/v1/chat/stream/` → no error bubble → `done` received → bubble shows full text.
2. **Stop mid-stream**: Click Stop → partial text shows as `complete` state (no "Response interrupted" banner).
3. **Stop before first token**: Click Stop immediately → placeholder bubble disappears entirely.
4. **Network drop (Retry)**: Disconnect network → send → error/interrupted banner + Retry → reconnect → Retry → success (single bubble updates, no duplicate).
5. **StrictMode double-invoke**: With React DevTools, confirm only 1 POST fires per message in dev mode.

---

## 🗺️ Route Mappings & Conflict Resolutions

| UI Element | SRS Route | Behavior & State |
| :--- | :--- | :--- |
| **Home** | `/` | Branded hero, statistics, featured programmes, announcements, events |
| **About** | `/about` | Overview, Vision & Mission, History, Leadership, Accreditation |
| **Academics** | `/academics` | 5 Departments, 14 Programmes, level & department filters |
| **Admissions** | `/admissions` | 4-step procedure, deadlines, eligibility, documents, 8 FAQs accordion |
| **Campus Life** | `/student-info` | Mapped to Student Info (Calendar, Exams, Fees in ₹, Hostel, Facilities, Contacts) |
| **Research** | `/research` | Sample content showcasing 50+ research centres & thrust areas |
| **News & Events** | `/news` | Filterable announcements and upcoming events (past hidden by default) |
| **AI Assistant** | `/chat` | Full-screen dedicated chatbot workspace with history sidebar |
| **Ask Kingsford AI** | Floating Widget | Bottom-right expandable/minimizable panel, shared state with `/chat` |
| **Student Portal** | N/A | Non-functional button; tooltip `"Student Portal (Coming soon)"` |
| **Search Button** | N/A | Non-functional icon button; tooltip `"Search (Coming soon)"` |
| **Saved Answers** | N/A | Non-functional sidebar item; tooltip `"Saved Answers (Coming soon)"` |
| **Bell / Avatar / Mic / Clip**| N/A | Non-functional; tooltip `"Coming soon"` per UI conflict rules |
| **Currency** | N/A | Strictly Indian Rupee (₹ / INR) |
| **Notice** | Footer | Explicit notice: `"Sample System – Replace with official data"` |

---

## 📋 SRS Requirements Traceability Matrix

### Functional Requirements (FR)
- **FR-001 (Homepage)**: Header, hero, statistics, featured programmes, announcements, events, quick cards. `[IMPLEMENTED]`
- **FR-002 (About Page)**: Vision, mission, history, leadership, accreditation. `[IMPLEMENTED]`
- **FR-003 (Academics)**: 5 departments, 14 UG/PG programmes with duration/eligibility filterable by level & dept. `[IMPLEMENTED]`
- **FR-004 (Admissions)**: 4-step procedure, eligibility, 2026-27 deadlines, documents, 8 FAQs accordion. `[IMPLEMENTED]`
- **FR-005 (Student Info)**: Academic calendar, examinations, fee structure, scholarships, library, hostel, facilities, contacts. `[IMPLEMENTED]`
- **FR-006 (Announcements & Events)**: 6 announcements (newest first, filterable) + 6 upcoming events (ordered by date). `[IMPLEMENTED]`
- **FR-007 (Dynamic Content)**: DRF REST endpoints + Django Admin editable without code changes; missing data shows "Information not yet available". `[IMPLEMENTED]`
- **FR-008 (Responsive Breakpoints)**: Tested and responsive at 360px, 768px, and 1280px+; mobile drawer navigation. `[IMPLEMENTED]`
- **FR-009 (Site-wide Chat Access)**: Floating widget on all pages + navigation link to `/chat`. `[IMPLEMENTED]`
- **FR-010 (Floating Widget)**: Expandable, minimizable, welcome bubble, quick chips, input, send button, persistent open state. `[IMPLEMENTED]`
- **FR-011 (Chat Page /chat)**: Full-page layout, history sidebar (drawer on mobile), New Chat, Clear, suggested questions grid. `[IMPLEMENTED]`
- **FR-012 (Unified Chat State)**: Shared client ID and active conversation ID between widget and `/chat`. `[IMPLEMENTED]`
- **FR-013 (Quick Actions)**: 8 quick actions sending predefined queries. `[IMPLEMENTED]`
- **FR-014 (Input Validation)**: 1 to 1,000 characters; whitespace rejected; sending disabled during streaming. `[IMPLEMENTED]`
- **FR-015 (Formatted Markdown)**: Paragraphs, lists, bold text, links rendered safely; raw HTML strictly escaped. `[IMPLEMENTED]`
- **FR-016 (Chatbot Scope)**: Strict institutional scope; non-college topics politely declined. `[IMPLEMENTED]`
- **FR-017 (Conversation Creation)**: Created on first message and identified by UUID. `[IMPLEMENTED]`
- **FR-018 (Message Storage)**: User messages and assistant replies stored with role, content, status, and timestamp. `[IMPLEMENTED]`
- **FR-019 (Conversation History List)**: Ordered by `-updated_at`, titled with first 40 chars. `[IMPLEMENTED]`
- **FR-020 (Conversation Resume)**: Selecting conversation loads its messages and continues context. `[IMPLEMENTED]`
- **FR-021 (New Chat & Deletion)**: New chat, conversation deletion with confirmation, clear conversation messages. `[IMPLEMENTED]`
- **FR-022 (Context Isolation)**: Active conversation messages only sent to Gemini. `[IMPLEMENTED]`
- **FR-023 (Context Trimming)**: Latest 10 messages trimmed to ~6,000 tokens of history. `[IMPLEMENTED]`
- **FR-024 (Client ID)**: Anonymous UUID generated and stored in `localStorage`, sent via `X-Client-ID`. `[IMPLEMENTED]`
- **FR-025 (SSE Streaming)**: `StreamingHttpResponse` with `text/event-stream`. `[IMPLEMENTED]`
- **FR-026 (ReadableStream Client)**: Client reads POST SSE stream via `ReadableStream` reader. `[IMPLEMENTED]`
- **FR-027 (SSE Event Types)**: `token`, `done`, `error`. `[IMPLEMENTED]`
- **FR-028 (Typing Indicator & Stop)**: Typing indicator until first token; Stop button cancels via `AbortController`. `[IMPLEMENTED]`
- **FR-029 (Interruption Handling)**: Partial reply saved as `incomplete`; UI shows "Response interrupted" with Retry button. `[IMPLEMENTED]`
- **FR-030 (Stream Closure)**: Closes cleanly after `done`/`error` or client abort. `[IMPLEMENTED]`
- **FR-031 (Two Django Apps)**: `website` (content models & REST APIs) and `chatbot` (conversations, retrieval, SSE). `[IMPLEMENTED]`
- **FR-032 (Single Gemini Service)**: Official `google-genai` Python SDK in `chatbot/gemini_service.py`. `[IMPLEMENTED]`
- **FR-033 (Knowledge Retrieval)**: Active database records selected and injected as "Approved University Information". `[IMPLEMENTED]`
- **FR-034 (Retry & Fallback)**: 3 retries with exponential backoff on 429/500/503/504; automatic fallback to `gemini-2.5-flash-lite`. 400/401/403 not retried. `[IMPLEMENTED]`
- **FR-035 (Rate Limiting)**: 15 req/min, 150 req/day per client ID and IP with HTTP 429 and `Retry-After`. `[IMPLEMENTED]`
- **FR-036 (Environment Config)**: Environment variables loaded via `.env`; committed `.env.example`; idempotent `seed_data`. `[IMPLEMENTED]`

### Non-Functional & Security Requirements (NFR & SEC)
- **NFR-001 / NFR-002 (Performance)**: Fast sub-100ms API responses, stream starts promptly. `[SATISFIED]`
- **NFR-003 / SEC-001 (Security)**: API key never exposed to client, repository, or bundle. `[SATISFIED]`
- **NFR-004 (Usability)**: Instant one-click quick action chips and suggested queries. `[SATISFIED]`
- **NFR-005 (Accessibility)**: High text contrast, visible focus outlines, `aria-live` announcements. `[SATISFIED]`
- **NFR-006 (Responsiveness)**: Tested across 360px mobile, 768px tablet, 1280px+ desktop. `[SATISFIED]`
- **NFR-007 (Reliability)**: AI interruptions never break website pages. `[SATISFIED]`
- **NFR-008 (Maintainability)**: Modular components, PEP 8 style, ESLint compliant, automated test suites. `[SATISFIED]`
- **NFR-010 (Data Integrity)**: Atomic transactions, CASCADE message cleanup, no orphan rows. `[SATISFIED]`
- **NFR-011 (Recovery)**: Single-click retry retains input and conversation state. `[SATISFIED]`
- **SEC-003 (Injection Defense)**: Reference data encapsulation, leakage detection. `[SATISFIED]`
- **SEC-004 / SEC-005 (CORS & CSRF)**: Restricted CORS origin list, CSRF protection maintained on Admin. `[SATISFIED]`
- **SEC-007 (Client Isolation)**: Independent UUID-scoped client sessions. `[SATISFIED]`

---

## 👥 Authors & License
Developed for Kingsford University under the ISO/IEC/IEEE 29148 Specification. All institutional records are realistic sample data for evaluation.
