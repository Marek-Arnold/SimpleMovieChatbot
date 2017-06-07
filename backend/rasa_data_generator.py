from .imdb_sql.imdb import IMDB
import json
import logging
import random
import http.client
import urllib.request
import urllib.parse
import urllib.error
import base64

years = ['2016', '2017']

movies_by_skeletons = ['Show me movies by {first_name} {last_name}',
                       'movies by {first_name} {last_name}',
                       'show me the movies by {first_name} {last_name}',
                       'movies directed by {first_name} {last_name}',
                       'Which movies are directed by {first_name} {last_name}',
                       'Which movies have been directed by {first_name} {last_name}',
                       'Which films are directed by {first_name} {last_name}']

movies_by_and_genre_skeletons = ['Show me {genre} movies by {first_name} {last_name}',
                       '{genre} movies by {first_name} {last_name}',
                       'show me the {genre} movies by {first_name} {last_name}',
                       '{genre} movies directed by {first_name} {last_name}',
                       'Which {genre} movies are directed by {first_name} {last_name}',
                       'Which {genre} movies have been directed by {first_name} {last_name}',
                       'Which {genre} films are directed by {first_name} {last_name}']

movies_with_skeletons = ['Show me movies with {first_name} {last_name}',
                         'Movies with {first_name} {last_name}',
                         'Movies starring {first_name} {last_name}',
                         'Flicks with {first_name} {last_name}',
                         '{first_name} {last_name} movies']

movies_with_and_genre_skeletons = ['Show me {genre} movies with {first_name} {last_name}',
                                 '{genre} movies with {first_name} {last_name}',
                                 '{genre} movies starring {first_name} {last_name}',
                                 '{genre} flicks with {first_name} {last_name}',
                                 '{first_name} {last_name} {genre} movies']
movies_with_and_genre_skeletons_genre_last = ['{first_name} {last_name} {genre} movies']

starring_in_skeletons = ['Who star in {movie_name}',
                         'Who is starring in {movie_name}',
                         'Who starred in {movie_name}',
                         'Who is in the cast of {movie_name}',
                         'Who plays in {movie_name}',
                         'Who has a role in {movie_name}']

director_of_skeletons = ['Who directed {movie_name}?',
                         'Who was the director of {movie_name}?',
                         'Who made {movie_name}']

movies_of_genre_skeletons = ['List me some {genre} movies',
                             'Show me some {genre} movies',
                             'Show me {genre} movies',
                             '{genre} movies',
                             'Some {genre} movies']

def generate_json_data(output_file='/home/user/swisstext/chatbot/train_data.json', train_data_per_sentence_skeleton=120):
    random.seed(1)

    imdb = IMDB()
    print('Get all actors names.')
    actors = imdb.get_all_actor_names()
    print(actors[:10])
    print('Get all directros names.')
    directors = imdb.get_all_director_names()
    print(directors[:10])
    print('Get all movie titles.')
    movies = imdb.get_all_movie_names()
    print(movies[:10])
    print('Get all genres.')
    genres = imdb.get_all_genres()
    print(genres[:10])

    print('Got\t{0}\tactors\n{1}\tdirectors\n{2}\tmovies\n{3}\tgenres'.format(len(actors), len(directors), len(movies), len(genres)))
    rasa_nlu_data = {}
    common_examples = []
    rasa_nlu_data['common_examples'] = common_examples

    for movies_by_skeleton in movies_by_skeletons:
        for i in range(train_data_per_sentence_skeleton):
            director = random.choice(directors)
            example = dict()
            example['text'] = movies_by_skeleton.format(first_name=director[0], last_name=director[1])
            example['intent'] = 'movie_name'
            example['entities'] = []

            start = movies_by_skeleton.find('{first_name}')
            end = start + len(director[0])
            first_name_entity = {'start': start, 'end': end, 'value': director[0], 'entity': 'foaf:name'}

            start = movies_by_skeleton.format(first_name=director[0], last_name='{last_name}').find('{last_name}')
            end = start + len(director[1])
            last_name_entity = {'start': start, 'end': end, 'value': director[1], 'entity': 'foaf:familyName'}

            example['entities'].append(first_name_entity)
            example['entities'].append(last_name_entity)

            common_examples.append(example)
            print(example['text'])

    for movies_by_and_genre_skeleton in movies_by_and_genre_skeletons:
        for i in range(train_data_per_sentence_skeleton):
            director = random.choice(directors)
            genre = random.choice(genres)
            example = dict()
            example['text'] = movies_by_and_genre_skeleton.format(first_name=director[0], last_name=director[1], genre=genre)
            example['intent'] = 'movie_name'
            example['entities'] = []

            start = movies_by_and_genre_skeleton.find('{genre}')
            end = start + len(genre)
            genre_entity = {'start': start, 'end': end, 'value': genre, 'entity': 'dbpprop:genre'}

            start = movies_by_and_genre_skeleton.format(genre=genre, first_name='{first_name}', last_name='{last_name}').find('{first_name}')
            end = start + len(director[0])
            first_name_entity = {'start': start, 'end': end, 'value': director[0], 'entity': 'foaf:name'}

            start = movies_by_and_genre_skeleton.format(genre=genre, first_name=director[0], last_name='{last_name}').find('{last_name}')
            end = start + len(director[1])
            last_name_entity = {'start': start, 'end': end, 'value': director[1], 'entity': 'foaf:familyName'}

            example['entities'].append(genre_entity)
            example['entities'].append(first_name_entity)
            example['entities'].append(last_name_entity)

            common_examples.append(example)
            print(example['text'])

    for movies_with_skeleton in movies_with_skeletons:
        for i in range(train_data_per_sentence_skeleton):
            actor = random.choice(actors)
            example = dict()
            example['text'] = movies_with_skeleton.format(first_name=actor[0], last_name=actor[1])
            example['intent'] = 'movie_name'
            example['entities'] = []

            start = movies_with_skeleton.find('{first_name}')
            end = start + len(actor[0])
            first_name_entity = {'start': start, 'end': end, 'value': actor[0], 'entity': 'foaf:name'}

            start = movies_with_skeleton.format(first_name=actor[0], last_name='{last_name}').find('{last_name}')
            end = start + len(actor[1])
            last_name_entity = {'start': start, 'end': end, 'value': actor[1], 'entity': 'foaf:familyName'}

            example['entities'].append(first_name_entity)
            example['entities'].append(last_name_entity)

            common_examples.append(example)

    for movies_with_and_genre_skeleton in movies_with_and_genre_skeletons:
        for i in range(train_data_per_sentence_skeleton):
            actor = random.choice(actors)
            genre = random.choice(genres)
            example = dict()
            example['text'] = movies_with_and_genre_skeleton.format(first_name=actor[0], last_name=actor[1], genre=genre)
            example['intent'] = 'movie_name'
            example['entities'] = []

            start = movies_with_and_genre_skeleton.find('{genre}')
            end = start + len(genre)
            genre_entity = {'start': start, 'end': end, 'value': genre, 'entity': 'dbpprop:genre'}

            start = movies_with_and_genre_skeleton.format(genre=genre, first_name='{first_name}', last_name='{last_name}').find('{first_name}')
            end = start + len(actor[0])
            first_name_entity = {'start': start, 'end': end, 'value': actor[0], 'entity': 'foaf:name'}

            start = movies_with_and_genre_skeleton.format(genre=genre, first_name=actor[0], last_name='{last_name}').find('{last_name}')
            end = start + len(actor[1])
            last_name_entity = {'start': start, 'end': end, 'value': actor[1], 'entity': 'foaf:familyName'}

            example['entities'].append(genre_entity)
            example['entities'].append(first_name_entity)
            example['entities'].append(last_name_entity)

            common_examples.append(example)
            print(example['text'])

    for movies_of_genre_skeleton in movies_of_genre_skeletons:
        for i in range(train_data_per_sentence_skeleton):
            genre = random.choice(genres)
            example = dict()
            example['text'] = movies_of_genre_skeleton.format(genre=genre)
            example['intent'] = 'movie_name'
            example['entities'] = []

            start = movies_of_genre_skeleton.find('{genre}')
            end = start + len(genre)
            genre_entity = {'start': start, 'end': end, 'value': genre, 'entity': 'dbpprop:genre'}
            example['entities'].append(genre_entity)
            common_examples.append(example)
            print(example['text'])

    for starring_in_skeleton in starring_in_skeletons:
        for i in range(train_data_per_sentence_skeleton):
            movie = random.choice(movies)
            example = dict()
            example['text'] = starring_in_skeleton.format(movie_name=movie)
            example['intent'] = 'actor_name'
            example['entities'] = []

            start = starring_in_skeleton.find('{movie_name}')
            end = start + len(movie)
            movie_entity = {'start': start, 'end': end, 'value': movie, 'entity': 'dbp-owl:Film'}

            example['entities'].append(movie_entity)

            common_examples.append(example)
            print(example['text'])

    json_string = json.dumps(rasa_nlu_data)

    with open(output_file, 'w') as of:
        of.write(json_string)

    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': '257d6d68f1e74e069abb2dcc7cd61aab',
        'Content-Type': 'application/json'
    }

    params = urllib.parse.urlencode({
    })

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/luis/v1.0/prog/apps/80521fe9-f569-4d78-8110-b1a9c742d236/train?%s" % params, json_string, headers)

        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        logging.exception(e)



