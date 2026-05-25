---
name: project-overview
description: AI Meeting Assistant - project overview and tech stack
metadata:
  type: project
  priority: 1
---

# Project Overview

AI Meeting Assistant is a Chrome Extension that records Google Meet calls, transcribes audio with OpenAI Whisper, and generates summaries/action items with Google Gemini.

## Tech Stack

- **Chrome Extension**: Manifest V3, Vanilla JS, Service Workers
- **Backend**: Python Flask (primary), Node.js Express (alternative)
- **AI**: OpenAI Whisper (transcription), Google Gemini 2.5 Flash (summarization & task extraction)
- **Database**: MongoDB Atlas (with in-memory fallback for development)
- **Storage**: AWS S3

## Current Status

- **Sprint 1**: ✅ Complete - Chrome Extension ready
- **Sprint 2**: ✅ Partial - Backend API ready, S3 pending
- **Sprint 3**: ✅ Complete - AI services working
- **Sprint 4**: ⏳ Pending - Dashboard & Deploy