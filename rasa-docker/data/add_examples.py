import json
from sys import stdin

def main():
    with open('moviebot.json','r') as f:
        data = json.loads(f.read())

    data["rasa_nlu_data"]["entity_examples"] = []
    for line in stdin: # read a new title from the standard input
        title = line[:-1] # remove \n character
        example = {
                      "text": "what is the plot of %s" % title,
                      "entities": [
                        {
                          "start": 20,
                          "end": 20 + len(title),
                          "value": title,
                          "entity": "dbp-owl:Film"
                        }
                      ]
                    }
        data["rasa_nlu_data"]["entity_examples"].append(example)

    print(json.dumps(data, indent=2)) # write to the standard output

if __name__ == "__main__":
    main()
