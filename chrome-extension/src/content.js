/**
 * Content Script - Chạy trong context của Google Meet tab
 * Nhiệm vụ: Capture audio từ MediaStream và gửi về background script
 */

(function() {
  'use strict';

  // Chỉ chạy trên Google Meet
  if (!window.location.href.includes('meet.google.com')) {
    console.log('AI Meeting Assistant: Not on Google Meet');
    return;
  }

  console.log('📥 AI Meeting Assistant content script loaded');

  // ===== STATE =====
  let mediaRecorder = null;
  let audioChunks = [];
  let isRecording = false;
  let stream = null;

  // ===== UTILITY FUNCTIONS =====

  /**
   * Convert Blob to Base64 - để gửi qua message passing
   */
  function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  /**
   * Fallback: Tìm audio element trong DOM và capture stream
   */
  async function getAudioStreamFromDOM() {
    const audioElements = document.querySelectorAll('audio');
    for (const audio of audioElements) {
      try {
        if (audio.captureStream) {
          const stream = audio.captureStream();
          if (stream.getAudioTracks().length > 0) {
            console.log('Method DOM: Captured audio from DOM element');
            return stream;
          }
        }
        if (audio.srcObject && audio.srcObject.getAudioTracks().length > 0) {
          console.log('Method DOM: Using audio srcObject');
          return audio.srcObject;
        }
      } catch (err) {
        console.log('DOM capture failed:', err.message);
      }
    }
    throw new Error('No audio element found in DOM');
  }

  /**
   * Sử dụng getDisplayMedia - reliable nhất cho việc capture tab audio
   * User sẽ được hỏi chọn cửa sổ để share
   */
  async function getAudioStreamFromDisplayMedia() {
    console.log('Method DisplayMedia: Requesting screen/audio share...');

    const displayStream = await navigator.mediaDevices.getDisplayMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
      video: false, // Không cần video
    });

    // Lọc chỉ lấy audio tracks
    const audioTracks = displayStream.getAudioTracks();

    if (audioTracks.length === 0) {
      displayStream.getTracks().forEach(track => track.stop());
      throw new Error('No audio track in display media');
    }

    // Tạo stream mới chỉ với audio
    const audioStream = new MediaStream(audioTracks);

    // Cleanup video tracks nếu có
    displayStream.getVideoTracks().forEach(track => track.stop());

    console.log('Method DisplayMedia: Captured audio, tracks:', audioTracks.length);
    return audioStream;
  }

  /**
   * Fallback cuối cùng: Microphone (không capture được meeting audio)
   */
  async function getAudioStreamFromMicrophone() {
    console.log('Method Microphone: Using system microphone...');
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });
    return stream;
  }

  // ===== RECORDING FUNCTIONS =====

  /**
   * Bắt đầu thu âm
   */
  async function startRecording() {
    if (isRecording) {
      console.log('Already recording');
      return { success: false, error: 'Already recording' };
    }

    try {
      console.log('🎙️ Starting audio capture...');

      let stream = null;
      let method = '';

      // Thứ tự ưu tiên: getDisplayMedia → DOM → Microphone
      // getDisplayMedia là reliable nhất cho tab audio

      // Method 1: getDisplayMedia (user chọn tab Meet)
      try {
        stream = await getAudioStreamFromDisplayMedia();
        method = 'getDisplayMedia';
      } catch (err) {
        console.log('getDisplayMedia failed:', err.message);

        // Method 2: DOM audio element
        try {
          stream = await getAudioStreamFromDOM();
          method = 'DOM';
        } catch (err2) {
          console.log('DOM method failed:', err2.message);

          // Method 3: Microphone (fallback cuối cùng)
          try {
            stream = await getAudioStreamFromMicrophone();
            method = 'microphone';
          } catch (err3) {
            throw new Error('All capture methods failed: ' + err3.message);
          }
        }
      }

      // Kiểm tra stream có audio không
      if (!stream || stream.getAudioTracks().length === 0) {
        throw new Error('No audio tracks available');
      }

      console.log('✅ Got audio stream via:', method, '- Tracks:', stream.getAudioTracks().length);

      // Xác định mimeType hỗ trợ
      let mimeType = 'audio/webm';
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus';
      } else if (MediaRecorder.isTypeSupported('audio/webm;codecs=vp9')) {
        mimeType = 'audio/webm;codecs=vp9';
      }

      console.log('Using mimeType:', mimeType);

      // Khởi tạo MediaRecorder
      mediaRecorder = new MediaRecorder(stream, {
        mimeType,
        audioBitsPerSecond: 128000,
      });

      audioChunks = [];

      // Xử lý khi có dữ liệu audio mới
      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunks.push(event.data);
          console.log('📦 Audio chunk received, size:', event.data.size);
        }
      };

      // Xử lý khi dừng recording
      mediaRecorder.onstop = async () => {
        console.log('Recording stopped, processing audio...');
        console.log('Total chunks:', audioChunks.length);

        if (audioChunks.length === 0) {
          console.error('No audio chunks recorded');
          return;
        }

        // Tạo Blob từ các chunks
        const audioBlob = new Blob(audioChunks, { type: mimeType });
        console.log('Audio blob size:', audioBlob.size);

        // Convert sang base64
        const audioBase64 = await blobToBase64(audioBlob);
        console.log('Base64 length:', audioBase64.length);

        // Gửi về background script
        chrome.runtime.sendMessage({
          type: 'AUDIO_DATA',
          audio: audioBase64,
          mimeType: mimeType,
          timestamp: Date.now(),
        });

        // Cleanup
        if (stream) {
          stream.getTracks().forEach((track) => track.stop());
          stream = null;
        }
        audioChunks = [];
      };

      // Xử lý lỗi MediaRecorder
      mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event);
      };

      // Bắt đầu thu âm - thu mỗi 1 giây để đảm bảo có dữ liệu
      mediaRecorder.start(1000);
      isRecording = true;

      console.log('✅ Recording started successfully');
      return { success: true, method };
    } catch (error) {
      console.error('❌ Failed to start recording:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Dừng thu âm
   */
  async function stopRecording() {
    if (!isRecording || !mediaRecorder) {
      return { success: false, error: 'Not recording' };
    }

    try {
      mediaRecorder.stop();
      isRecording = false;
      console.log('⏹️ Recording stopped');
      return { success: true };
    } catch (error) {
      console.error('Failed to stop recording:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Lấy thông tin cuộc họp
   */
  function getMeetingInfo() {
    const url = window.location.href;
    let meetingId = 'meeting-' + Date.now();

    const match = url.match(/[a-z]{3}-[a-z]{4}-[a-z]{3}/);
    if (match) {
      meetingId = match[0];
    }

    return {
      meetingId,
      url,
      title: document.title,
    };
  }

  // ===== MESSAGE HANDLER =====

  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    handleMessage(message)
      .then(sendResponse)
      .catch((err) => sendResponse({ success: false, error: err.message }));
    return true;
  });

  async function handleMessage(message) {
    switch (message.type) {
      case 'START_RECORDING':
        return await startRecording();

      case 'STOP_RECORDING':
        return await stopRecording();

      case 'GET_MEET_INFO':
        return getMeetingInfo();

      default:
        return { success: false, error: 'Unknown message type' };
    }
  }

  console.log('📥 Content script ready');
})();