# LearnLoop — AI-Powered Learning Management System & Course Builder

> **"LearnLoop transforms fragmented materials like PDFs, textbooks, and notes into structured courses, interactive assessments, and personalized learning experiences."**

[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0+-purple.svg)](https://vitejs.dev/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

---

## Problem Statement

In today's fast-paced world, learners and educators are overwhelmed with unstructured information—raw PDFs, scattered notes, voice memos, and lengthy textbooks. Traditional Learning Management Systems (LMS) force users to manually build curricula, design quizzes, and track progress, which is incredibly time-consuming.

**LearnLoop** solves this by autonomously transforming fragmented unstructured inputs into **structured, AI-curated courses**, complete with interactive flashcards, spaced-repetition modules, and personalized assessments.

---

## Key Capabilities & Architecture

```
   RAW UNSTRUCTURED INPUTS
(Voice, PDF, Images, Chats, Notes)
               │
               ▼
┌───────────────────────────────┐
│     Multimodal Capture Hub    │ ➔ Groq Vision OCR + Whisper Audio
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│   Curriculum Generator AI     │ ➔ LLM Course Structuring (10 Levels)
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ Interactive Learning Modules  │ ➔ Flashcards, MCQs, and Study Guides
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│   Gamification & Analytics    │ ➔ XP, Streaks, and Progress Tracking
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│   Spatial Study Workspace     │ ➔ Spatial Canvas / Note Editor
└───────────────────────────────┘
```

### 1. AI-Powered Course Generation
- Transforms any topic or uploaded document into a beautifully structured **10-level course**.
- Seamlessly blends LLM-generated dynamic content with robust local templates for flawless generation.
- Automatically generates modules, lessons, and interactive blocks.

### 2. Interactive Assessments (MCQs & Flashcards)
- Automatically extracts key concepts from textbooks and generates **Multiple Choice Questions (MCQs)** and **Flashcards**.
- Provides rich explanations for wrong answers to reinforce learning.

### 3. Multimodal Capture Ingestion
- **Vision OCR:** Powered by Groq Vision for scanning receipts, textbook pages, and diagrams.
- **Audio Transcription:** Powered by Groq Whisper for voice memos and lectures.
- **Document Extractors:** Multi-format streaming extractors for `.pdf`, `.docx`, `.md`, and more.

### 4. Gamified Learning & XP System
- Keeps learners engaged with a dynamic progression system.
- Earn **+15 XP** for correct MCQ answers and **+10 Score** for completing levels.
- Track daily streaks and learning milestones directly on the dashboard.

### 5. Spatial Canvas & Study Workspace
- An interactive spatial whiteboard canvas embedded directly in the frontend for visual entity exploration and card grouping.
- Smooth, frictionless rich-text editor for taking notes side-by-side with course materials.

---

## Repository Structure

```
learnloop/
├── README.md                      # Comprehensive project overview & documentation
├── frontend/                      # React + TypeScript Frontend
│   ├── client/src/
│   │   ├── pages/                 # UI Views (Dashboard, CourseView, LessonView, Profile, Workspace)
│   │   ├── components/            # Reusable UI Components (Switch, Buttons, Modals)
│   │   ├── contexts/              # Global State (DarwinityStoreContext, ThemeContext)
│   │   ├── lib/                   # Utilities (courseGenerator, persistence)
│   │   └── types/                 # TypeScript interfaces and schema definitions
├── capture_api/                   # FastAPI Context Intelligence Backend
│   ├── main.py                    # API entrypoint and router registration
│   ├── routers/                   # API Endpoints (Course, Study, Retrieval)
│   ├── services/                  # Business Logic (AI Pipeline, Curriculum Generator)
│   └── ...
└── ...
```

---

## Getting Started

### Backend Setup (FastAPI + Python)
1. Navigate to the `capture_api` directory: `cd capture_api`
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the server: `python main.py` or `uvicorn main:app --reload --port 8080`

### Frontend Setup (React + Vite)
1. Navigate to the frontend directory: `cd frontend/client`
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`

Open your browser and navigate to the frontend URL to start building and taking your personalized AI courses!
