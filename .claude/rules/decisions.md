---
name: decisions
description: Important technical decisions and rationale
metadata:
  type: technical
  priority: 1
---

# Technical Decisions

## AI Model Selection

### Gemini Model
- **Decision**: Use `gemini-2.5-flash` instead of `gemini-1.5-pro`
- **Reason**: Model `gemini-1.5-pro` returns 404 (deprecated/not found)
- **Verified**: `gemini-2.5-flash` is the latest model supporting generateContent
- **Note**: Flash is faster and cheaper than Pro for this use case

### OpenAI Version
- **Decision**: Upgrade openai package from 1.12.0 to 2.37.0
- **Reason**: Fix error `Client.__init__() got an unexpected keyword argument 'proxies'`
- **Root Cause**: Conflict between openai 1.12.0 and httpx 0.28.1

## Database Strategy

### In-Memory Fallback
- **Decision**: Use in-memory storage when MongoDB not configured
- **Reason**: Allow development without MongoDB Atlas setup
- **Files Updated**:
  - `backend/src/config/database.js` (Node.js)
  - `backend/config/database.py` (Python)
  - `backend/src/routes/meetings.js` (Node.js)
  - `backend/routes/meetings.py` (Python)

## Backend Choice

### Python as Primary
- **Decision**: Recommend Python Flask over Node.js
- **Reason**: Already has complete services (Whisper, Gemini, S3) implemented
- **Node.js**: Available but less complete

---

# Next Steps

## Immediate (Sprint 2 continuation)

1. **Integrate S3** into transcribe route
   - Upload audio to S3 before transcription
   - Use S3 URL for long audio files

2. **Fix Chrome Extension audio capture**
   - Common issue: `tabCapture` permission denied
   - Alternative: Use getDisplayMedia

3. **Test with real audio**
   - Record from Chrome Extension
   - Upload to `/api/meetings/transcribe`

## Sprint 3 continuation

4. **Data Masking**
   - Anonymize participant names before sending to AI
   - Replace with "[Person 1]", "[Person 2]", etc.

5. **Enhanced Prompt Engineering**
   - Add language detection
   - Improve task extraction accuracy

## Sprint 4

6. **Dashboard UI**
   - React or vanilla HTML/CSS/JS
   - Display transcript, summary, tasks

7. **Resilience Features**
   - Queue system for processing
   - Circuit breaker for API failures
   - Retry with exponential backoff

8. **Deploy to Vercel**
   - Serverless deployment
   - Environment configuration