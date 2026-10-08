# Adaptive Learning & Artifact API

This starter turns uploaded material into a reusable learning workspace. The same normalized document layer can produce **summaries, flashcards, quizzes, mind maps, flowcharts, notes, timelines, tables, outlines, study guides, grounded chat answers, and personalized courses**. It now uses a persistent **Chroma vector database** for semantic retrieval across large documents.

The API also includes lightweight bearer-token authentication. Documents, vector search, courses, artifacts, and learner progress are scoped to the authenticated user's library.

Generated courses can be exported as **PDF** or **SCORM 1.2-compatible ZIP packages**. Review scheduling uses a persisted SM-2-style algorithm with quality scores from 0 to 5, repetitions, intervals, and easiness factors.

## Architecture

```text
PDF / DOCX / PPTX / TXT / IMAGE
              |
              v
       Ingestion + extraction
              |
              v
      Normalized document + chunks
              |
       +------+----------------+
       |                       |
       v                       v
  Chroma vector DB       Course engine
        |                       |
        v                       |
  semantic retrieval           |
        |                       |
        +----------+------------+
                   v
             RAG / artifact engine
       |                       |
 summary, cards,        modules, lessons,
 quiz, mind map,        prerequisites,
 flowchart, etc.        mastery, next lesson
```

The LLM is optional. Without `OPENAI_API_KEY`, deterministic fallback generators make the API locally runnable. With an API key, the application uses one model with different structured task prompts. Chroma's default embedding function is used for semantic search; if Chroma is unavailable, the app falls back to SQLite lexical retrieval.

## Run

```bash
cd adaptive-learning
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI.

Optional LLM configuration:

```bash
export OPENAI_API_KEY="your-key"
export LLM_MODEL="gpt-5-mini"
```

## Main workflow

1. Register or sign in with `/auth/signup` or `/auth/login` and keep the returned bearer token.
2. Upload source material with `POST /documents/upload`; chunks are embedded and persisted under `data/chroma`.
3. Search semantically across the entire user library with `GET /library/search?q=...`, or within one document with `/documents/{document_id}/search`.
4. Generate any artifact with `POST /documents/{document_id}/artifacts/{kind}`; artifact generation retrieves relevant chunks first.
5. Render returned JSON in the frontend using Mermaid, React Flow, tables, cards, or custom components.
6. If the user clicks **Create Course**, call `POST /documents/{document_id}/create-course` with the learner's goal, daily time, and level.
7. Use `/courses/{course_id}/next`, `/progress`, and `/courses/{course_id}/progress` for persistent adaptive learning.
8. Use `POST /documents/{document_id}/chat` for RAG-based source-grounded questions.
9. Export courses using `/courses/{course_id}/export/pdf` or `/courses/{course_id}/export/scorm`.
10. Export generated artifacts, including mind maps, using `/artifacts/{artifact_id}/export/pdf`.

Supported artifact kinds:

```text
summary, flashcards, quiz, mindmap, flowchart,
notes, timeline, table, outline, study_guide
```

## Example requests

Upload:

```bash
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@biology.pdf"
```

Authentication:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","password":"strong-password"}' | jq -r .access_token)
```

Pass `Authorization: Bearer $TOKEN` to all user-scoped endpoints.

Create a mind map:

```bash
curl -X POST http://127.0.0.1:8000/documents/DOCUMENT_ID/artifacts/mindmap \
  -H 'Content-Type: application/json' \
  -d '{"instruction":"Show the major concepts and their relationships"}'
```

Create a personalized course:

```bash
curl -X POST http://127.0.0.1:8000/documents/DOCUMENT_ID/create-course \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"alice","goal":"prepare for an exam","daily_minutes":30,"level":2}'
```

Ask a grounded question:

```bash
curl -X POST http://127.0.0.1:8000/documents/DOCUMENT_ID/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"alice","question":"Explain the most important process in this material"}'
```

Semantic search:

```bash
curl 'http://127.0.0.1:8000/documents/DOCUMENT_ID/search?q=TCP%20congestion%20control&k=5'
```

Cross-document library search:

```bash
curl 'http://127.0.0.1:8000/library/search?q=security%20and%20reliable%20communication&k=8' \
  -H "Authorization: Bearer $TOKEN"
```

Course exports:

```bash
curl -L http://127.0.0.1:8000/courses/COURSE_ID/export/pdf \
  -H "Authorization: Bearer $TOKEN" -o course.pdf

curl -L http://127.0.0.1:8000/courses/COURSE_ID/export/scorm \
  -H "Authorization: Bearer $TOKEN" -o course-scorm.zip
```

The SCORM package contains `imsmanifest.xml` and an `index.html` SCO that can be uploaded to an LMS supporting SCORM 1.2.

SM-2 progress submission:

```json
{
  "concept_id": "CONCEPT_ID",
  "correct": true,
  "quality": 4,
  "confidence": 0.8
}
```

`quality` follows the SM-2 scale: `0` is a complete failure and `5` is a perfect response. Scores below `3` reset repetitions and schedule a one-day review. Successful repetitions advance through one day, six days, and then easiness-adjusted intervals.

## Frontend rendering

- Render `mindmap`, `flowchart`, and graph-like `outline` artifacts with **React Flow** or Mermaid.
- Render `flashcards` as flip cards.
- Render `quiz` as interactive questions that submit to `/progress` after grading.
- Render `timeline` as ordered events.
- Render `table` as a sortable data table.
- Render course modules as a progressive learning path.

For production, replace SQLite with PostgreSQL, queue long-running generation jobs, add authentication, configure a dedicated embedding model, and add OCR/vision for scanned PDFs and images. Chroma persistence is appropriate for a single-service deployment; for horizontally scaled production, use a managed Chroma-compatible service or another shared vector database.
