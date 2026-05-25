---
name: architecture
description: System architecture, data flow, and services
metadata:
  type: technical
  priority: 1
---

# Architecture

## Data Flow

1. **Recording**: Content script (`content.js`) captures audio via `chrome.tabCapture` API
2. **State Management**: Background service worker (`background.js`) manages recording state
3. **UI**: Popup (`popup.js`) provides start/stop controls and meeting list
4. **API**: Backend receives audio, calls Whisper for transcription, then Gemini for summary/tasks

## Dual Backend Implementation

The project has **two parallel backend implementations**:
- `backend/app.py` - Python Flask (primary, recommended)
- `backend/src/index.js` - Node.js Express (alternative)

Both implement the same API endpoints. The Python version has fallback in-memory storage when MongoDB is unavailable.

## Key Services (`backend/services/`)

- `whisper_service.py` - Audio transcription via OpenAI Whisper API
- `gemini_service.py` - Meeting summarization and action item extraction
- `s3_service.py` - Audio file storage

## Meeting Status Flow

`recording` → `processing` → `completed` (or `failed`)