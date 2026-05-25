---
name: api-endpoints
description: REST API endpoints and configuration
metadata:
  type: technical
  priority: 2
---

# API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/meetings` | List meetings |
| GET | `/api/meetings/<id>` | Get meeting details |
| POST | `/api/meetings` | Create new meeting |
| PUT | `/api/meetings/<id>` | Update meeting |
| DELETE | `/api/meetings/<id>` | Delete meeting |
| POST | `/api/meetings/transcribe` | Upload audio and process with AI |
| POST | `/api/meetings/test-ai` | Test AI with sample text (no audio needed) |

Health check: `GET /health`

## Testing AI

```bash
# Test AI với text mẫu
curl -X POST http://localhost:3000/api/meetings/test-ai \
  -H "Content-Type: application/json" \
  -d '{"text":"Cuoc hop hom nay thao luan ve du an. Anh Minh se hoan thanh UI truoc ngay 25."}'

# Test với audio file
curl -X POST http://localhost:3000/api/meetings/transcribe \
  -F "audio=@recording.webm" \
  -F "meetingId=test-001"
```

## Configuration

Environment variables (see `.env.example`):
- `MONGODB_URI` - MongoDB Atlas connection string
- `OPENAI_API_KEY` - OpenAI API key for Whisper
- `GEMINI_API_KEY` - Google Gemini API key
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET` - S3 credentials
- `PORT` - Server port (default: 3000)

## Development Notes

- Python backend automatically falls back to in-memory storage when MongoDB is not configured
- Audio is captured in WebM format (Opus codec)
- Backend accepts large payloads (`50mb` limit)