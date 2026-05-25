# Chrome Extension Setup

## Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select the `chrome-extension` folder

## Development

- `manifest.json` - Extension configuration (Manifest V3)
- `src/popup.html/js` - Extension popup UI
- `src/background.js` - Service worker (recording logic)
- `src/content.js` - Injected script for Google Meet

## Testing

1. Open Google Meet in a tab
2. Click the extension icon
3. Click "Start Recording"
4. Grant microphone/tab capture permissions when prompted

## Permissions Required

- `activeTab` - Access current tab
- `scripting` - Inject content scripts
- `tabs` - Read tab information
- `*://meet.google.com/*` - Access Google Meet

## Notes

- Manifest V3 requires service worker (background.js) instead of background page
- Audio capture uses chrome.tabCapture API
- Files are saved as WebM format (opus codec)