class Extra(object):

    def __init__(self):
        self.satisfaction = -1
        self.expected_type = None
        self.creator = None
        self.classification = None
        self.parameters = []
        self.time_required = 0
        self.query = ''
        self.context = None
        self.intents = []
        self.entities = []

    def serialize(self):
        return {
            'satisfaction':   self.satisfaction,
            'expectedType':   self.expected_type,
            'creator':        self.creator,
            'classification': self.classification,
            'parameters':     self.parameters,
            'timeRequired':   self.time_required,
            'query':          self.query,
            'context':        self.context,
            'intents':        self.intents,
            'entities':       self.entities
        }
