"""
Meeting Model - Lưu trữ thông tin cuộc họp và kết quả
"""
from datetime import datetime, timezone
from config.database import get_meetings_collection, is_using_memory, _in_memory_store

class Meeting:
    """Meeting Model tương đương với Mongoose model"""

    STATUS_RECORDING = 'recording'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    collection_name = 'meetings'

    def __init__(self, data=None):
        data = data or {}
        self._id = data.get('_id') if data else None
        self.meetingId = data.get('meetingId') if data else None
        self.title = data.get('title', 'Untitled Meeting')
        self.meetingUrl = data.get('meetingUrl', '')
        self.duration = data.get('duration', 0)
        self.audioUrl = data.get('audioUrl', '')
        self.audioDuration = data.get('audioDuration', 0)
        self.transcript = data.get('transcript', '')
        self.transcriptLanguage = data.get('transcriptLanguage', 'vi')
        self.summary = data.get('summary', '')
        self.tasks = data.get('tasks', [])
        self.status = data.get('status', self.STATUS_RECORDING)
        self.errorMessage = data.get('errorMessage', '')
        self.startedAt = data.get('startedAt', datetime.now(timezone.utc))
        self.completedAt = data.get('completedAt', None)
        self.createdAt = data.get('createdAt', datetime.now(timezone.utc))
        self.updatedAt = data.get('updatedAt', datetime.now(timezone.utc))

    @staticmethod
    def get_collection():
        return get_meetings_collection()

    @staticmethod
    def use_memory():
        return is_using_memory()

    def save(self):
        """Lưu meeting vào database"""
        now = datetime.now(timezone.utc)
        data = {
            'meetingId': self.meetingId,
            'title': self.title,
            'meetingUrl': self.meetingUrl,
            'duration': self.duration,
            'audioUrl': self.audioUrl,
            'audioDuration': self.audioDuration,
            'transcript': self.transcript,
            'transcriptLanguage': self.transcriptLanguage,
            'summary': self.summary,
            'tasks': self.tasks,
            'status': self.status,
            'errorMessage': self.errorMessage,
            'startedAt': self.startedAt,
            'completedAt': self.completedAt,
            'createdAt': self.createdAt,
            'updatedAt': now
        }

        if self.use_memory():
            # In-memory storage
            if self._id:
                for i, m in enumerate(_in_memory_store['meetings']):
                    if m.get('_id') == self._id:
                        _in_memory_store['meetings'][i] = {**data, '_id': self._id}
                        return True
            else:
                import uuid
                self._id = str(uuid.uuid4())
                _in_memory_store['meetings'].append({**data, '_id': self._id})
            return True
        else:
            # MongoDB storage
            collection = self.get_collection()
            if self._id:
                result = collection.update_one(
                    {'_id': self._id},
                    {'$set': data}
                )
                return result.modified_count > 0
            else:
                result = collection.insert_one(data)
                self._id = result.inserted_id
                return True

    @staticmethod
    def find_one(query):
        """Tìm một meeting"""
        if Meeting.use_memory():
            for m in _in_memory_store['meetings']:
                match = True
                for k, v in query.items():
                    if m.get(k) != v:
                        match = False
                        break
                if match:
                    return Meeting(m)
            return None
        else:
            collection = get_meetings_collection()
            data = collection.find_one(query)
            if data:
                return Meeting(data)
            return None

    @staticmethod
    def find(query=None, limit=20, offset=0, sort_by='createdAt', sort_order=-1):
        """Tìm nhiều meetings"""
        query = query or {}

        if Meeting.use_memory():
            results = _in_memory_store['meetings']
            # Filter
            filtered = []
            for m in results:
                match = True
                for k, v in query.items():
                    if m.get(k) != v:
                        match = False
                        break
                if match:
                    filtered.append(m)
            # Sort
            reverse = sort_order == -1
            filtered.sort(key=lambda x: x.get(sort_by, datetime.min), reverse=reverse)
            # Limit/offset
            return [Meeting(m) for m in filtered[offset:offset+limit]]
        else:
            collection = get_meetings_collection()
            cursor = collection.find(query)\
                .sort(sort_by, sort_order)\
                .skip(offset)\
                .limit(limit)
            return [Meeting(doc) for doc in cursor]

    @staticmethod
    def count(query=None):
        """Đếm số lượng meetings"""
        query = query or {}

        if Meeting.use_memory():
            results = _in_memory_store['meetings']
            if not query:
                return len(results)
            count = 0
            for m in results:
                match = True
                for k, v in query.items():
                    if m.get(k) != v:
                        match = False
                        break
                if match:
                    count += 1
            return count
        else:
            collection = get_meetings_collection()
            return collection.count_documents(query)

    @staticmethod
    def find_by_meeting_id(meeting_id):
        """Tìm meeting theo meetingId"""
        return Meeting.find_one({'meetingId': meeting_id})

    def delete(self):
        """Xóa meeting"""
        if self._id:
            if Meeting.use_memory():
                for i, m in enumerate(_in_memory_store['meetings']):
                    if m.get('_id') == self._id:
                        _in_memory_store['meetings'].pop(i)
                        return True
                return False
            else:
                collection = self.get_collection()
                result = collection.delete_one({'_id': self._id})
                return result.deleted_count > 0
        return False

    def to_dict(self, exclude_fields=None):
        """Chuyển đổi thành dictionary"""
        exclude_fields = exclude_fields or []
        data = {
            '_id': self._id,
            'meetingId': self.meetingId,
            'title': self.title,
            'meetingUrl': self.meetingUrl,
            'duration': self.duration,
            'audioUrl': self.audioUrl,
            'audioDuration': self.audioDuration,
            'transcript': self.transcript,
            'transcriptLanguage': self.transcriptLanguage,
            'summary': self.summary,
            'tasks': self.tasks,
            'status': self.status,
            'errorMessage': self.errorMessage,
            'startedAt': self.startedAt.isoformat() if self.startedAt else None,
            'completedAt': self.completedAt.isoformat() if self.completedAt else None,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None
        }

        # Remove excluded fields
        for field in exclude_fields:
            if field in data:
                del data[field]

        return data