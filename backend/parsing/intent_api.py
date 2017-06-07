from luis_sdk import LUISClient


class IntentAPI():
    def __init__(self):
        self.api = LUISClient('80521fe9-f569-4d78-8110-b1a9c742d236', '257d6d68f1e74e069abb2dcc7cd61aab', True)

    def parse(self, question):
        print("Sending question '{0}' to luis.".format(question))
        response = self.api.predict(question)

        intents = response.get_intents()
        entities = response.get_entities()

        print(intents)
        print(entities)

        return intents, entities
