# 🏗️ CAPTURE — Technical Architecture & Formal Specification

## 1. Mathematical Formulas & Telemetry

### 1.1 Discrete Linear Authority Gate
Context chunks are ranked and filtered via a linear weighted sum of relevance and provenance authority:

$$\text{Final Score} = (\text{Cosine Similarity} \times 0.7) + (\text{Authority Weight} \times 0.3)$$

- **Threshold:** $\text{Final Score} \ge 0.45$ (survivors enter the token packing budget).
- **Authority Weight Scale:**
  - `0.95`: Confirmed official documentation (PDFs, calendar invites).
  - `0.85`: Team chats, approved meeting minutes.
  - `0.65`: Voice memos, raw screenshot OCR.
  - `0.50`: Unverified informal notes.

### 1.2 Mathematical Context Reduction Ratio
The exact percentage of prompt tokens saved by the narrowing engine:

$$\text{Reduction Ratio} = \left( \frac{\text{Raw Space Tokens} - \text{Packed Tokens}}{\text{Raw Space Tokens}} \right) \times 100\%$$

---

## 2. Master 8-Step Orchestration Pipeline

```
  [1] Goal Analysis Agent ───➔ Query Expansion & Keyword Signal Extraction
            │
  [2] Multi-Source Retrieval ──➔ Hybrid Search (Vector Cosine + Lexical BM25)
            │
  [3] Entity Resolution ──────➔ Batched .in_() Query + Semantic LLM Identity Reasoning
            │
  [4] Context Selection ──────➔ Discrete Linear Authority Gate
            │
  [5] Memory Profile ─────────➔ Static Persona + Dynamic Workspace Synthesis
            │
  [6] Contradiction Detector ──➔ 2-Stage LLM Collision Detection
            │
  [7] Dangling Ref Scan ──────➔ Edge-case Integrity & Orphan Protection
            │
  [8] Context Assembler ──────➔ Final ContextPack Assembly & Token Ledger Accounting
```

---

## 3. Database Schema (PostgreSQL + pgvector)

```sql
-- Core Captures
CREATE TABLE captures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    type VARCHAR(32) NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    preview TEXT,
    embedding vector(384),
    authority_weight FLOAT DEFAULT 0.75,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Canonical Resolved Entities
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    canonical_name TEXT NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    aliases TEXT[] DEFAULT '{}',
    embedding vector(384),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Coreference Entity Links
CREATE TABLE capture_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capture_id UUID REFERENCES captures(id) ON DELETE CASCADE,
    entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    entity_text TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0
);

-- Contradiction Ledger
CREATE TABLE contradictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    space_id UUID,
    capture_a_id UUID REFERENCES captures(id),
    capture_b_id UUID REFERENCES captures(id),
    conflicting_field TEXT NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(32) DEFAULT 'medium',
    status VARCHAR(32) DEFAULT 'open',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 4. MCP Tool Specification

The MCP Server implements the standard JSON-RPC 2.0 tool interface:
1. `get_context_pack`
2. `resolve_entity`
3. `report_contradiction`
4. `capture_add_memory`

Compatible out of the box with Claude Desktop, Cursor, and any MCP client.
