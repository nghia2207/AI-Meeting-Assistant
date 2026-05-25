// popup.js - UI Logic for Chrome Extension Popup
// Handles user interactions and communicates with background/service worker

const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const statusBadge = document.getElementById('statusBadge');
const statusText = document.getElementById('statusText');
const errorDiv = document.getElementById('error');
const durationEl = document.getElementById('duration');
const audioSizeEl = document.getElementById('audioSize');
const meetingListEl = document.getElementById('meetingList');
const emptyStateEl = document.getElementById('emptyState');

let isRecording = false;
let recordingStartTime = null;
let audioSize = 0;
let timerInterval = null;

// Initialize: check current recording state and load meetings
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'GET_STATE' });
    if (response?.isRecording) {
      recordingStartTime = response.startTime || Date.now();
      updateUI('recording');
      startTimer();
    }
  } catch (err) {
    console.log('Extension just loaded');
  }

  // Load recent meetings
  loadMeetings();
});

// Start Recording Button
recordBtn.addEventListener('click', async () => {
  try {
    showError(null);
    recordBtn.disabled = true;
    updateStatusText('Connecting to meeting...');

    const response = await chrome.runtime.sendMessage({
      type: 'START_RECORDING'
    });

    if (response.success) {
      recordingStartTime = Date.now();
      audioSize = 0;
      updateUI('recording');
      startTimer();
    } else {
      showError(response.error || 'Failed to start recording');
      recordBtn.disabled = false;
    }
  } catch (err) {
    showError('Cannot connect to extension');
    recordBtn.disabled = false;
  }
});

// Stop Recording Button
stopBtn.addEventListener('click', async () => {
  try {
    showError(null);
    stopBtn.disabled = true;
    updateStatusText('Processing audio...');
    updateUI('processing');
    stopTimer();

    const response = await chrome.runtime.sendMessage({
      type: 'STOP_RECORDING'
    });

    if (response.success) {
      updateStatusText('Processing complete!');
      updateUI('ready');
      loadMeetings();
    } else {
      showError(response.error || 'Processing failed');
      updateUI('ready');
    }
  } catch (err) {
    showError('Failed to process recording');
    updateUI('ready');
  }
});

// Update UI state
function updateUI(state) {
  recordBtn.disabled = false;
  stopBtn.disabled = false;
  statusBadge.className = 'status-badge';

  switch (state) {
    case 'recording':
      isRecording = true;
      recordBtn.innerHTML = '<span>⏸️</span> Recording...';
      recordBtn.classList.add('recording');
      recordBtn.disabled = true;
      stopBtn.disabled = false;
      statusBadge.classList.add('recording');
      statusText.textContent = 'Recording';
      break;

    case 'processing':
      isRecording = false;
      recordBtn.innerHTML = '<span>🎙️</span> Start Recording';
      recordBtn.classList.remove('recording');
      recordBtn.disabled = true;
      stopBtn.disabled = true;
      statusBadge.classList.add('processing');
      statusBadge.style.background = '#fef3c7';
      statusBadge.style.color = '#92400e';
      statusText.textContent = 'Processing';
      break;

    case 'ready':
    default:
      isRecording = false;
      recordBtn.innerHTML = '<span>🎙️</span> Start Recording';
      recordBtn.classList.remove('recording');
      recordBtn.disabled = false;
      stopBtn.disabled = true;
      statusBadge.classList.add('ready');
      statusBadge.style.background = '#d1fae5';
      statusBadge.style.color = '#065f46';
      statusText.textContent = 'Ready';
      break;
  }
}

// Timer functions
function startTimer() {
  timerInterval = setInterval(() => {
    if (recordingStartTime) {
      const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
      durationEl.textContent = formatTime(elapsed);
      // Simulate audio size growth
      audioSize = (elapsed * 0.1).toFixed(1);
      audioSizeEl.textContent = audioSize + ' MB';
    }
  }, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function formatTime(seconds) {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function updateStatusText(text) {
  statusText.textContent = text;
}

// Show error message
function showError(message) {
  if (message) {
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
  } else {
    errorDiv.classList.remove('show');
  }
}

// Load meetings from API
async function loadMeetings() {
  try {
    const response = await fetch('http://localhost:3000/api/meetings');
    const data = await response.json();

    if (data.meetings && data.meetings.length > 0) {
      emptyStateEl.style.display = 'none';
      meetingListEl.innerHTML = '';

      data.meetings.slice(0, 5).forEach(meeting => {
        const item = createMeetingItem(meeting);
        meetingListEl.appendChild(item);
      });
    } else {
      emptyStateEl.style.display = 'block';
      meetingListEl.innerHTML = '';
    }
  } catch (err) {
    console.log('Could not load meetings:', err);
  }
}

function createMeetingItem(meeting) {
  const div = document.createElement('div');
  div.className = 'meeting-item';

  const statusClass = meeting.status === 'completed' ? 'completed' : 'processing';
  const statusText = meeting.status === 'completed' ? 'Done' : 'Processing';

  const date = new Date(meeting.createdAt);
  const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

  div.innerHTML = `
    <div class="meeting-icon">📝</div>
    <div class="meeting-details">
      <div class="meeting-title">${meeting.title || 'Untitled Meeting'}</div>
      <div class="meeting-meta">${dateStr}</div>
    </div>
    <span class="meeting-status ${statusClass}">${statusText}</span>
  `;

  return div;
}