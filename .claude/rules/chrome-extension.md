---
name: chrome-extension
description: Chrome Extension structure and permissions
metadata:
  type: technical
  priority: 2
---

# Chrome Extension

- Manifest V3 uses service worker (`background.js`) instead of background page
- `content.js` injects into Google Meet pages to capture audio
- `popup.js` provides the recording UI controls

## Required Permissions

- `activeTab` - Access current tab
- `scripting` - Inject content scripts
- `tabs` - Read tab information
- `*://meet.google.com/*` - Access Google Meet
- `tabCapture` - Capture audio from tabs (requires user gesture)