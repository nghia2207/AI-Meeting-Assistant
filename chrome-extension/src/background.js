/**
 * background.js - Chrome Extension Service Worker (Manifest V3)
 * Xử lý: Nhận audio từ content.js, upload lên backend API
 */

const STATE = {
  isRecording: false,
  meetingId: null,
  currentTabId: null,
  audioBuffer: [],
  streamId: null, // Lưu tab stream ID
};

// ===== MESSAGE HANDLER =====

// Lắng nghe messages từ popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender)
    .then(sendResponse)
    .catch((err) => sendResponse({ success: false, error: err.message }));
  return true; // Async response
});

async function handleMessage(message, sender) {
  switch (message.type) {
    case 'GET_STATE':
      return { success: true, isRecording: STATE.isRecording };

    case 'START_RECORDING':
      return await startRecording();

    case 'STOP_RECORDING':
      return await stopRecording();

    case 'GET_TAB_STREAM':
      return await getTabStream();

    case 'AUDIO_DATA':
      // Nhận audio data từ content.js
      return await handleAudioData(message);

    default:
      return { success: false, error: 'Unknown message type' };
  }
}

/**
 * Lấy tab stream ID sử dụng chrome.tabCapture API
 * Đây là cách đúng để capture audio từ tab trong Manifest V3
 */
async function getTabStream() {
  try {
    // Kiểm tra nếu đã có stream ID và còn hoạt động
    if (STATE.streamId) {
      // Verify stream vẫn còn hoạt động bằng cách thử lấy lại
      return { success: true, streamId: STATE.streamId };
    }

    // Lấy tab đang hoạt động
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab) {
      throw new Error('No active tab found');
    }

    // Kiểm tra quyền tabCapture
    if (!chrome.tabCapture) {
      throw new Error('tabCapture API not available');
    }

    // Lấy stream ID với quyền audio only
    const streamId = await chrome.tabCapture.getMediaStreamId({
      targetTabId: tab.id,
      audioConstraints: {
        mandatory: {
          chromeMediaSource: 'tab',
        },
      },
    });

    STATE.streamId = streamId;
    console.log('📺 Got tab stream ID:', streamId);

    return { success: true, streamId };
  } catch (error) {
    console.error('getTabStream error:', error);
    return { success: false, error: error.message };
  }
}

// ===== RECORDING FUNCTIONS =====

/**
 * Bắt đầu thu âm - Inject content script vào Google Meet tab
 */
async function startRecording() {
  try {
    // Tìm tab Google Meet đang hoạt động
    const tabs = await chrome.tabs.query({ url: '*://meet.google.com/*' });
    const meetTab = tabs.find((tab) => tab.id && tab.url.includes('meet.google.com'));

    if (!meetTab) {
      return { success: false, error: 'No Google Meet tab found. Please open a meeting first.' };
    }

    STATE.currentTabId = meetTab.id;
    STATE.isRecording = true;
    STATE.audioBuffer = [];
    STATE.streamId = null; // Reset stream ID

    // Inject content script để bắt đầu thu âm
    await chrome.scripting.executeScript({
      target: { tabId: meetTab.id },
      files: ['src/content.js'],
    });

    // Gửi message yêu cầu bắt đầu thu âm
    const response = await chrome.tabs.sendMessage(meetTab.id, {
      type: 'START_RECORDING',
    });

    if (response && response.success) {
      // Lấy meeting info
      const meetingInfo = await chrome.tabs.sendMessage(meetTab.id, {
        type: 'GET_MEET_INFO',
      });
      STATE.meetingId = meetingInfo.meetingId;

      console.log('✅ Recording started for meeting:', STATE.meetingId);
      return { success: true, meetingId: STATE.meetingId };
    }

    return { success: false, error: response?.error || 'Failed to start recording' };
  } catch (error) {
    console.error('Start recording error:', error);
    STATE.isRecording = false;
    return { success: false, error: error.message };
  }
}

/**
 * Dừng thu âm - Yêu cầu content.js dừng và nhận audio
 * Sau đó upload lên backend để xử lý AI
 */
async function stopRecording() {
  if (!STATE.currentTabId) {
    return { success: false, error: 'No active recording' };
  }

  try {
    // Gửi message yêu cầu dừng thu âm và lấy audio data
    const response = await chrome.tabs.sendMessage(STATE.currentTabId, {
      type: 'STOP_RECORDING',
    });

    // Lấy pending audio từ storage
    const { pendingAudio } = await chrome.storage.local.get('pendingAudio');

    if (pendingAudio && pendingAudio.length > 0) {
      // Upload audio to backend
      console.log('📤 Uploading audio to backend...');

      for (const audioData of pendingAudio) {
        await uploadAudioToBackend(audioData);
      }

      // Clear pending audio
      await chrome.storage.local.set({ pendingAudio: [] });
    }

    STATE.isRecording = false;
    STATE.streamId = null; // Clear stream ID
    console.log('⏹️ Recording stopped and uploaded');

    return { success: true };
  } catch (error) {
    console.error('Stop recording error:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Xử lý audio data nhận được từ content.js
 * Lưu tạm vào storage để đợi khi stop recording
 */
async function handleAudioData(audioMessage) {
  try {
    const { audio, mimeType, timestamp } = audioMessage;

    console.log('📦 Received audio data, size:', audio ? audio.length : 0);

    // Lưu vào local storage tạm thời (cho phép recovery)
    const { pendingAudio } = await chrome.storage.local.get('pendingAudio');
    const audioQueue = pendingAudio || [];

    audioQueue.push({
      audio,
      mimeType,
      timestamp,
      meetingId: STATE.meetingId,
    });

    await chrome.storage.local.set({ pendingAudio: audioQueue });

    return { success: true, queued: true };
  } catch (error) {
    console.error('Handle audio data error:', error);
    return { success: false, error: error.message };
  }
}

// ===== AUTO-SAVE / UPLOAD FUNCTIONS =====

/**
 * Upload audio lên backend API
 * Được gọi khi có đủ dữ liệu hoặc user dừng recording
 */
async function uploadAudioToBackend(audioData) {
  try {
    const { backendUrl } = await chrome.storage.local.get('backendUrl');
    const apiUrl = backendUrl || 'http://localhost:3000';

    // Tạo FormData
    const formData = new FormData();
    const blob = await fetch(audioData.audio).then((r) => r.blob());
    const filename = `meeting_${audioData.meetingId || Date.now()}.webm`;
    formData.append('audio', blob, filename);
    formData.append('meetingId', audioData.meetingId || STATE.meetingId);

    const response = await fetch(`${apiUrl}/api/meetings/transcribe`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    const result = await response.json();
    console.log('✅ Audio uploaded and processed:', result);
    return { success: true, result };
  } catch (error) {
    console.error('Upload error:', error);
    return { success: false, error: error.message };
  }
}

// ===== CLEANUP =====

// Cleanup khi extension bị tắt
chrome.runtime.onSuspend.addListener(() => {
  if (STATE.isRecording) {
    console.warn('Extension suspended while recording');
  }
});

console.log('📥 AI Meeting Assistant background service worker loaded');