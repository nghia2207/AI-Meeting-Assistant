# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Sprint Progress

### Sprint 1: Chrome Extension - ✅ COMPLETED
- Chrome Extension (Manifest V3) đã có sẵn và hoạt động
- Audio capture từ Google Meet qua MediaRecorder API
- Popup UI với Start/Stop recording

### Sprint 2: Backend API + Whisper - ✅ COMPLETED
- Python Flask backend với in-memory fallback (không cần MongoDB)
- Node.js backend cũng đã update in-memory support
- API endpoints: `/api/meetings`, `/api/meetings/:id`, `/api/meetings/transcribe`
- **✅ S3 integration** đã tích hợp vào transcribe route

### Sprint 3: Gemini AI + Prompt Engineering - ✅ COMPLETED
- Gemini 2.5 Flash tích hợp và hoạt động
- Whisper service đã upgrade để transcribe audio
- **✅ Data Masking** - Anonymize tên người tham gia trước khi gửi lên AI

### Sprint 4: Dashboard + Deploy - ✅ COMPLETED
- Dashboard UI tại http://localhost:3000
- Hiển thị transcript, summary, action items
- Responsive design

---

## Important Decisions & Changes

| Decision | Reason |
|----------|--------|
| Gemini model: `gemini-2.5-flash` | Model `gemini-1.5-pro` deprecated, 2.5-flash là model mới nhất và nhanh hơn |
| OpenAI upgrade: 1.12.0 → 2.37.0 | Fix lỗi `proxies` argument conflict với httpx |
| In-memory fallback | Cho phép development không cần MongoDB |
| Python backend là primary | Đã có đầy đủ services (Whisper, Gemini, S3) |

---

## 🚀 Hướng dẫn chạy dự án

### Bước 1: Cài đặt dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Bước 2: Cấu hình API Keys

Tạo file `.env` trong thư mục `backend/`:

```env
# OpenAI Whisper API (for Speech-to-Text)
OPENAI_API_KEY=sk-your-openai-key-here

# Google Gemini API (for Summarization & Task Extraction)
GEMINI_API_KEY=your-gemini-key-here

# AWS S3 (optional - for audio storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=ai-meeting-audio

# Backend Server
PORT=3000
```

### Bước 3: Chạy Backend

```bash
cd backend
python app.py
```

Server sẽ chạy tại http://localhost:3000

### Bước 4: Mở Dashboard

Mở trình duyệt và truy cập: http://localhost:3000

### Bước 5: Load Chrome Extension

1. Mở `chrome://extensions/`
2. Enable Developer mode
3. Click "Load unpacked" → chọn thư mục `chrome-extension/`

### Bước 6: Test AI (tùy chọn)

```bash
curl -X POST http://localhost:3000/api/meetings/test-ai \
  -H "Content-Type: application/json" \
  -d '{"text":"Cuoc hop hom nay thao luan ve du an. Anh Minh se hoan thanh UI truoc ngay 25."}'
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/meetings` | List meetings |
| GET | `/api/meetings/<id>` | Get meeting details |
| POST | `/api/meetings` | Create new meeting |
| PUT | `/api/meetings/<id>` | Update meeting |
| DELETE | `/api/meetings/<id>` | Delete meeting |
| POST | `/api/meetings/transcribe` | Upload audio and process with AI |
| POST | `/api/meetings/test-ai` | Test AI with sample text |

Health check: `GET /health`

---

## Quick Commands

```bash
# Chạy Python Backend (primary)
cd backend && python app.py

# Test AI (text sample)
curl -X POST http://localhost:3000/api/meetings/test-ai \
  -H "Content-Type: application/json" \
  -d '{"text":"Cuoc hop hom nay..."}'

# Load Extension trên Cốc Cốc
# 1. coccoc://extensions
# 2. Enable Developer mode
# 3. Load unpacked → chrome-extension/
```

---

For detailed guidance, see rules in `.claude/rules/`:

- **project-overview** - Tech stack and project description
- **running-project** - Commands to run and develop
- **architecture** - System architecture and data flow
- **api-endpoints** - REST API endpoints and configuration
- **chrome-extension** - Chrome Extension structure and permissions