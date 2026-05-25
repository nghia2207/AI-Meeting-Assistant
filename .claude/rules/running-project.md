---
name: running-project
description: Commands to run and develop the project
metadata:
  type: developer
  priority: 1
---

# Running the Project

## Python Backend (primary)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

## Node.js Backend (alternative)

```bash
npm install
npm start
```

## Chrome Extension

1. Open `chrome://extensions/`
2. Enable Developer mode
3. Click "Load unpacked" → select `chrome-extension` folder

## Development Scripts

```bash
# Node.js backend
npm run dev        # Run with auto-reload (nodemon)
npm start           # Run production

# Python backend
npm run start:python   # python backend/app.py
npm run dev:python     # same as above

# Testing
npm test          # Run Jest tests
```