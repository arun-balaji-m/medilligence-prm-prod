from collections import defaultdict

class SessionStore:
    def __init__(self):
        self.sessions = defaultdict(list)

    def add(self, session_id, role, content):
        self.sessions[session_id].append({
            "role": role,
            "content": content
        })

    def get(self, session_id):
        return self.sessions[session_id]

session_store = SessionStore()
