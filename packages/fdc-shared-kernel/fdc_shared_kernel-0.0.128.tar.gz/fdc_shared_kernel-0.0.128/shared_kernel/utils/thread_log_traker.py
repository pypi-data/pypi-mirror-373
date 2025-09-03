from threading import Lock, current_thread


class LogStorage:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.logs = []
                    cls._instance.thread_logs = {}
        return cls._instance

    def add_log(self, log_data, track_id=None):
        thread_name = current_thread().name

        with self._lock:
            self.logs.append(log_data)

            # Maintain thread-specific logs
            if track_id not in self.thread_logs:
                self.thread_logs[track_id] = {
                    "logs": []
                }
            self.thread_logs[track_id]["logs"].append(log_data)

    def get_logs(self, track_id=None):
        with self._lock:
            if track_id:
                return self.thread_logs.get(track_id, {}).get("logs", []).copy()
            return self.logs.copy()

    def get_threads(self):
        with self._lock:
            return {
                tid: info["thread_name"]
                for tid, info in self.thread_logs.items()
            }

    def clean_log(self, track_id=None):
        with self._lock:
            if track_id:
                self.thread_logs.pop(track_id, None)
