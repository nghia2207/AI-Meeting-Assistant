"""
Meetings Routes - API endpoints cho quản lý cuộc họp
"""
from flask import Blueprint, request, jsonify
from models.meeting import Meeting
import datetime
import os
import sys
import traceback

meetings_bp = Blueprint('meetings', __name__)

# GET /api/meetings - Lấy danh sách cuộc họp
@meetings_bp.route('', methods=['GET'])
def get_meetings():
    try:
        status = request.args.get('status')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))

        query = {'status': status} if status else {}

        meetings = Meeting.find(query, limit=limit, offset=offset, sort_by='createdAt', sort_order=-1)
        total = Meeting.count(query)

        # Exclude only transcript (large) for list view, keep summary for preview
        meetings_data = [m.to_dict(exclude_fields=['transcript']) for m in meetings]

        return jsonify({'meetings': meetings_data, 'total': total})
    except Exception as e:
        print(f'Error fetching meetings: {e}')
        return jsonify({'error': 'Failed to fetch meetings'}), 500

# GET /api/meetings/<meeting_id> - Lấy chi tiết cuộc họp
@meetings_bp.route('/<meeting_id>', methods=['GET'])
def get_meeting(meeting_id):
    try:
        meeting = Meeting.find_by_meeting_id(meeting_id)

        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404

        return jsonify({'meeting': meeting.to_dict()})
    except Exception as e:
        print(f'Error fetching meeting: {e}')
        return jsonify({'error': 'Failed to fetch meeting'}), 500

# POST /api/meetings - Tạo cuộc họp mới
@meetings_bp.route('', methods=['POST'])
def create_meeting():
    try:
        data = request.get_json()
        meeting_id = data.get('meetingId')
        title = data.get('title', 'Untitled Meeting')
        meeting_url = data.get('meetingUrl', '')

        meeting = Meeting({
            'meetingId': meeting_id,
            'title': title,
            'meetingUrl': meeting_url,
            'status': Meeting.STATUS_RECORDING
        })

        meeting.save()
        return jsonify({'meeting': meeting.to_dict()}), 201
    except Exception as e:
        print(f'Error creating meeting: {e}')
        return jsonify({'error': 'Failed to create meeting'}), 500

# PUT /api/meetings/<meeting_id> - Cập nhật cuộc họp
@meetings_bp.route('/<meeting_id>', methods=['PUT'])
def update_meeting(meeting_id):
    try:
        data = request.get_json()
        meeting = Meeting.find_by_meeting_id(meeting_id)

        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404

        # Update fields
        for key, value in data.items():
            if hasattr(meeting, key):
                setattr(meeting, key, value)

        meeting.save()

        return jsonify({'meeting': meeting.to_dict()})
    except Exception as e:
        print(f'Error updating meeting: {e}')
        return jsonify({'error': 'Failed to update meeting'}), 500

# DELETE /api/meetings/<meeting_id> - Xóa cuộc họp
@meetings_bp.route('/<meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    try:
        meeting = Meeting.find_by_meeting_id(meeting_id)

        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404

        meeting.delete()
        return jsonify({'message': 'Meeting deleted successfully'})
    except Exception as e:
        print(f'Error deleting meeting: {e}')
        return jsonify({'error': 'Failed to delete meeting'}), 500

# POST /api/meetings/test-ai - Test AI với text mẫu (không cần audio)
@meetings_bp.route('/test-ai', methods=['POST'])
def test_ai():
    """Route test AI - Demo Whisper + Gemini without real audio"""
    try:
        data = request.get_json()
        test_text = data.get('text', '''Trong cuộc họp hôm nay, chúng ta đã thảo luận về dự án mới.
Anh Minh sẽ hoàn thành phần thiết kế UI trước ngày 25 tháng 5.
Chị Lan phụ trách tích hợp API với hệ thống CRM.
Chúng ta cần họp lại vào thứ Hai tuần sau để review tiến độ.
Anh Tuấn sẽ prepare bản demo cho khách hàng.''')

        from services.gemini_service import get_gemini_service

        # Vì là text mẫu, dùng trực tiếp Gemini (không mask vì là test)
        print('[TEST AI] Processing with Gemini...')
        gemini = get_gemini_service()
        result = gemini.process_meeting(test_text, language='vi', mask_data=False)

        # Save as a meeting so it shows up in the dashboard
        meeting_id = f'test_{int(datetime.datetime.now().timestamp())}'
        meeting = Meeting({
            'meetingId': meeting_id,
            'title': f'Test AI - {datetime.datetime.now().strftime("%H:%M %d/%m/%Y")}',
            'transcript': test_text,
            'summary': result['summary'],
            'tasks': result['tasks'],
            'status': Meeting.STATUS_COMPLETED
        })
        meeting.save()
        print(f'[TEST AI] Meeting saved: {meeting_id}')

        return jsonify({
            'message': 'Test AI success',
            'meetingId': meeting_id,
            'input_text': test_text,
            'summary': result['summary'],
            'tasks': result['tasks']
        }), 200

    except Exception as e:
        print(f'Test AI error: {e}')
        return jsonify({'error': str(e)}), 500

# POST /api/meetings/transcribe - Upload audio và xử lý (Whisper + Gemini)
@meetings_bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    try:
        import base64
        import tempfile

        audio_data = None
        meeting_id = None

        # Use system temp directory (cross-platform: works on Windows, Linux, macOS)
        temp_dir = tempfile.gettempdir()

        # Check if audio file is in request (multipart/form-data)
        if 'audio' in request.files:
            audio_file = request.files['audio']
            meeting_id = request.form.get('meetingId', f'meeting_{int(datetime.datetime.now().timestamp())}')

            # Save to temp file
            temp_path = os.path.join(temp_dir, f'audio_{meeting_id}.webm')
            audio_file.save(temp_path)
            audio_data = temp_path

        # Check if it's base64 encoded (JSON)
        elif request.is_json and 'audio' in request.json:
            data = request.json
            audio_base64 = data['audio']
            meeting_id = data.get('meetingId', f'meeting_{int(datetime.datetime.now().timestamp())}')

            # Decode base64 to temp file
            audio_bytes = base64.b64decode(audio_base64)
            temp_path = os.path.join(temp_dir, f'audio_{meeting_id}.webm')
            with open(temp_path, 'wb') as f:
                f.write(audio_bytes)
            audio_data = temp_path
        else:
            return jsonify({'error': 'No audio file provided'}), 400

        # Create or update meeting
        meeting = Meeting.find_by_meeting_id(meeting_id)
        if not meeting:
            meeting = Meeting({
                'meetingId': meeting_id,
                'title': request.form.get('title', 'Untitled Meeting'),
                'status': Meeting.STATUS_PROCESSING
            })
            meeting.save()
        else:
            meeting.status = Meeting.STATUS_PROCESSING
            meeting.save()

        # ========== AI PROCESSING ==========
        try:
            # Import services
            from services.whisper_service import get_whisper_service
            from services.gemini_service import get_gemini_service

            # ===== S3 UPLOAD =====
            s3_url = None
            try:
                from services.s3_service import get_s3_service
                s3 = get_s3_service()

                # Read audio file and upload to S3
                with open(audio_data, 'rb') as f:
                    audio_bytes = f.read()

                s3_key = f"recordings/{meeting_id}/{datetime.datetime.now().isoformat()}.webm"
                s3_url = s3.upload_audio(audio_bytes, s3_key)
                print(f'[S3] Audio uploaded: {s3_url}')

                # Update meeting with S3 URL
                meeting.audioUrl = s3_url
                meeting.save()
            except Exception as s3_error:
                print(f'[S3 WARNING] Upload failed, continuing without S3: {s3_error}')
                # Continue without S3 - not critical

            # Step 1: Transcribe with Whisper
            print('[AI] Transcribing audio with Whisper...')
            whisper = get_whisper_service()
            transcript = whisper.transcribe(audio_data, language='vi')
            print(f'[AI] Transcript length: {len(transcript)} chars')

            # Step 2: Process with Gemini (summary + tasks)
            print('[AI] Processing with Gemini...')
            gemini = get_gemini_service()
            result = gemini.process_meeting(transcript, language='vi', mask_data=True)

            summary = result['summary']
            tasks = result['tasks']
            print(f'[AI] Generated summary and {len(tasks)} tasks')

            # Update meeting with results
            meeting.transcript = transcript
            meeting.summary = summary
            meeting.tasks = tasks
            meeting.status = Meeting.STATUS_COMPLETED
            meeting.save()

            # Clean up temp file
            if os.path.exists(audio_data):
                os.remove(audio_data)

            return jsonify({
                'message': 'Audio processed successfully',
                'meetingId': meeting_id,
                'status': 'completed',
                'audioUrl': s3_url,
                'transcript': transcript,
                'summary': summary,
                'tasks': tasks
            }), 200

        except Exception as ai_error:
            print(f'[AI ERROR] {ai_error}', flush=True)
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
            meeting.status = Meeting.STATUS_FAILED
            meeting.save()
            return jsonify({
                'error': 'AI processing failed',
                'details': str(ai_error)
            }), 500

    except Exception as e:
        print(f'[TRANSCRIBE ERROR] {e}', flush=True)
        traceback.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()
        return jsonify({'error': f'Failed to process audio: {str(e)}'}), 500