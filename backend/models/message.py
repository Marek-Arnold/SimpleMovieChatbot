from datetime import datetime
import json


class Message(object):
    def __init__(self):
        self.session_id = 0
        self.version = 0
        self.timestamp = datetime.now()
        self.lang = 'en'
        self.actor = None # from
        self.reset_context = False
        self.attachments = []
        self.terminated = False
        self.extra = None

    def serialize(self, include_extra=True):
        return {
            'sessionId':    self.session_id,
            'version':      self.version,
            'timestamp':    self.timestamp.isoformat(),
            'lang':         self.lang,
            'actor':        self.actor,
            'resetContext': self.reset_context,
            'attachments':  [a.serialize() for a in self.attachments],
            'terminated':   self.terminated,
            'extra':        self.extra.serialize() if (self.extra is not None and include_extra) else None
        }

    def to_string(self):
        return json.dumps(self.serialize())
