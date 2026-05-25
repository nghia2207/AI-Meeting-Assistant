# Chrome Extension - AI Meeting Assistant 🎙️

[![Manifest](https://img.shields.io/badge/Manifest-V3-blue.svg)](https://developer.chrome.com/docs/extensions/mv3/intro/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![API](https://img.shields.io/badge/Chrome_API-tabCapture-green.svg)](https://developer.chrome.com/docs/extensions/reference/tabCapture/)

*English / [Tiếng Việt](#hướng-dẫn-tiếng-việt)*

This Chrome Extension is the crucial audio capture module for the **AI Meeting Assistant**. It natively integrates with Google Meet to record meetings directly from the browser tab using the `chrome.tabCapture` API, bypassing the need for an external bot to join the call.

---

## 🌟 Architecture & Core Features

- **Manifest V3 Architecture:** Built entirely on the modern and secure Chrome Manifest V3 standard.
- **Native Audio Capture:** Uses `tabCapture` for high-quality audio extraction without capturing background noise from the user's physical environment.
- **Service Worker Integration:** The `background.js` service worker handles the lifecycle of the recording and communicates securely with the Flask Backend.
- **Seamless Uploads:** Automatically converts the audio buffer into `.webm` (Opus codec) and uploads it directly to the local AI backend upon completion.

## 📂 Directory Structure

- `manifest.json`: Configuration and permissions (Manifest V3).
- `src/popup.html` & `src/popup.js`: The user interface for the extension toolbar popup.
- `src/background.js`: The Service Worker handling state management and API uploads.
- `src/content.js`: The injected script interacting with the active Google Meet DOM.

## 🚀 Installation Guide

1. Open Google Chrome or Cốc Cốc.
2. Navigate to `chrome://extensions/` (or `coccoc://extensions/`).
3. Toggle **Developer mode** ON (top right corner).
4. Click **Load unpacked** and select this `chrome-extension` directory.
5. Pin the extension to your toolbar for easy access!

## 🔐 Permissions Explained

- `activeTab` & `tabs`: Required to identify the active Google Meet tab.
- `scripting`: Needed to inject the recording logic (`content.js`) into the meeting page.
- `*://meet.google.com/*`: Restricts the extension to only operate on Google Meet URLs for privacy and security.

---

<br>

<h1 id="hướng-dẫn-tiếng-việt"> Hướng Dẫn Tiếng Việt 🇻🇳 </h1>

Đây là module thu âm cốt lõi của hệ thống **AI Meeting Assistant**. Tiện ích này tích hợp trực tiếp vào Google Meet để ghi âm cuộc họp ngay trên trình duyệt mà không cần sử dụng bất kỳ con bot nào tham gia vào phòng họp.

## 🌟 Kiến trúc & Tính năng nổi bật

- **Chuẩn Manifest V3:** Được xây dựng trên tiêu chuẩn bảo mật và hiện đại nhất của Chrome.
- **Thu âm Native (Tab Capture):** Lấy trực tiếp luồng âm thanh kỹ thuật số của cuộc họp (không thu tạp âm từ loa ngoài hay môi trường).
- **Service Worker:** Quản lý toàn bộ vòng đời thu âm và tương tác ngầm với Backend thông qua `background.js`.
- **Tự động Upload:** Tự động nén âm thanh thành định dạng `.webm` (Opus) và đẩy thẳng lên Backend AI để xử lý.

## 🚀 Hướng dẫn Cài đặt

1. Mở trình duyệt Google Chrome hoặc Cốc Cốc.
2. Truy cập vào địa chỉ `chrome://extensions/` (hoặc `coccoc://extensions/`).
3. Bật công tắc **Developer mode** (Chế độ dành cho nhà phát triển) ở góc trên bên phải.
4. Bấm nút **Load unpacked** (Tải tiện ích đã giải nén) và chọn thư mục `chrome-extension` này.
5. Đừng quên ghim (pin) tiện ích lên thanh công cụ để dễ dàng sử dụng nhé!

## 🔐 Chi tiết Quyền hạn (Permissions)

- `activeTab` & `tabs`: Cần thiết để nhận diện tab Google Meet đang mở.
- `scripting`: Cho phép nhúng mã thu âm vào trong trang web.
- `*://meet.google.com/*`: Giới hạn hoạt động của tiện ích chỉ trên trang Google Meet để đảm bảo tính riêng tư và bảo mật tối đa cho người dùng.