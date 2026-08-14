import time


class SessionManager:

    def __init__(self):

        self.sessions = {}

    def add(self, track_id, person, timeout=30):

        self.sessions[track_id] = {

            "person": person,

            "expire": time.time() + timeout
        }

    def remove(self, track_id):

        self.sessions.pop(track_id, None)

    def get(self, track_id):

        session = self.sessions.get(track_id)

        if session is None:
            return None

        if session["expire"] < time.time():

            self.remove(track_id)

            return None

        return session["person"]

    def cleanup(self):

        now = time.time()

        expired = [

            track

            for track, session in self.sessions.items()

            if session["expire"] < now
        ]

        for track in expired:

            self.remove(track)

    def get_all(self):

        self.cleanup()

        return self.sessions