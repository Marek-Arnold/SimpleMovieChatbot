from time import time
from .command_helper import CommandHelper
from .imdb_sql.imdb import IMDB
from .models.message import Message
from .models.attachment import Attachment
from .models.extra import Extra
from .parsing import intent_api
import sys
import logging
import distance


class Bot(object):
    def __init__(self):
        self.command_helper = CommandHelper()
        self.imdb = IMDB()
        self.intent_api = intent_api.IntentAPI()

        self.logger = logging.getLogger('chat_bot_question_parsing')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('chat_bot_question_parsing.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.logger_questions = logging.getLogger('chat_bot_question_parsing_questions')
        self.logger_questions.setLevel(logging.DEBUG)
        fh = logging.FileHandler('chat_bot_question_parsing_questions_only.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger_questions.addHandler(fh)

        self.all_movie_titles = set(movie.lower() for movie in self.imdb.get_all_movie_names())
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz '

    def fix_spelling(self, word_to_fix, known_words):
        if word_to_fix in known_words:
            return word_to_fix

        possible_edits = []

        if 'the ' + word_to_fix in known_words:
            possible_edits.append('The ' + word_to_fix)

        if len(possible_edits) == 0:
            splits = [(word_to_fix[:i], word_to_fix[i:]) for i in range(len(word_to_fix) + 1)]
            deletes = [a + b[1:] for a, b in splits if b]
            transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
            replaces = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
            inserts = [a + c + b for a, b in splits for c in self.alphabet]

            possible_edits = set(deletes + transposes + replaces + inserts)
            possible_edits = [possible_edit for possible_edit in possible_edits if possible_edit in known_words]

        if len(possible_edits) > 0:
            print("Corrected spelling for '{0}' to '{1}'".format(word_to_fix, possible_edits[0]))
            return possible_edits[0]
        else:
            print('Unable to correct spelling for: {0}'.format(word_to_fix))
            return word_to_fix

    def query(self, message_question, session_id, last_query_message):
        log_message = '\nquery_plain:\n{query_plain}\n\nquery:\n{query}\n\nintents:\n{intents}\n\nentities:\n{entities}\n\nanswer_plain:\n{answer_plain}\n\nanswer:\n{answer}\n\n'
        start_time = int(time()*(10**6))  # in microseconds

        message_answer = self.command_helper.query(message_question, session_id)

        intents = []
        entities = []

        if message_answer is None:
            question = message_question.attachments[0].content

            intents, entities = self.intent_api.parse(question)
            intents = [(intent.get_name(), intent.get_score()) for intent in intents]
            entities = [(entity.get_name(), entity.get_score(), entity.get_type()) for entity in entities]

            print(intents)
            print(entities)

            entities_map = {}
            for entity in entities:
                if entity[0] not in entities_map:
                    entities_map[entity[2]] = []
                entities_map[entity[2]].append(entity)

            # fix names
            if any(key in entities_map for key in ['dir_ln', 'dir_fn', 'actor_fn', 'actor_ln', 'comp_ln', 'comp_fn']):
                if 'dir_ln' in entities_map:
                    ln = entities_map['dir_ln'][0][0]
                elif 'actor_ln' in entities_map:
                    ln = entities_map['actor_ln'][0][0]
                elif 'comp_ln' in entities_map:
                    ln = entities_map['comp_ln'][0][0]
                else:
                    ln = ''

                if 'dir_fn' in entities_map:
                    fn = entities_map['dir_fn'][0][0]
                elif 'actor_fn' in entities_map:
                    fn = entities_map['actor_fn'][0][0]
                elif 'comp_fn' in entities_map:
                    fn = entities_map['comp_fn'][0][0]
                else:
                    fn = ''

                if ln == '' or fn == '':
                    if ln == '':
                        ln = fn
                    fn = '%'

                director = {'first_name': fn, 'last_name': ln}
                directors = self.imdb.get_director_names_by_name(director)

                actor = {'first_name': fn, 'last_name': ln}
                actors = self.imdb.get_actor_names_by_name(actor)

                composer = {'first_name': fn, 'last_name': ln}
                composers = self.imdb.get_composer_names_by_name(composer)

                if ('dir_ln' or 'dir_fn' in entities_map) and len(directors) > 0:
                    full_name = directors[0][1]
                    first_name = full_name[full_name.find(',') + 2:]
                    last_name = full_name[:full_name.find(',')]
                    entities_map['dir_ln'] = [(last_name, 1.0)]
                    entities_map['dir_fn'] = [(first_name, 1.0)]
                    if 'comp_ln' in entities_map:
                        entities_map.pop('comp_ln')
                    if 'comp_fn' in entities_map:
                        entities_map.pop('comp_fn')
                    if 'actor_ln' in entities_map:
                        entities_map.pop('actor_ln')
                    if 'actor_fn' in entities_map:
                        entities_map.pop('actor_fn')
                elif ('actor_ln' or 'actor_fn' in entities_map) and len(actors) > 0:
                    full_name = actors[0][1]
                    first_name = full_name[full_name.find(',') + 2:]
                    last_name = full_name[:full_name.find(',')]
                    entities_map['actor_ln'] = [(last_name, 1.0)]
                    entities_map['actor_fn'] = [(first_name, 1.0)]
                    if 'comp_ln' in entities_map:
                        entities_map.pop('comp_ln')
                    if 'comp_fn' in entities_map:
                        entities_map.pop('comp_fn')
                    if 'dir_ln' in entities_map:
                        entities_map.pop('dir_ln')
                    if 'dir_fn' in entities_map:
                        entities_map.pop('dir_fn')
                elif ('comp_ln' or 'comp_fn' in entities_map) and len(composers) > 0:
                    full_name = composers[0][1]
                    first_name = full_name[full_name.find(',') + 2:]
                    last_name = full_name[:full_name.find(',')]
                    entities_map['comp_ln'] = [(last_name, 1.0)]
                    entities_map['comp_fn'] = [(first_name, 1.0)]
                    if 'actor_ln' in entities_map:
                        entities_map.pop('actor_ln')
                    if 'actor_fn' in entities_map:
                        entities_map.pop('actor_fn')
                    if 'dir_ln' in entities_map:
                        entities_map.pop('dir_ln')
                    if 'dir_fn' in entities_map:
                        entities_map.pop('dir_fn')
                elif len(directors) > 0:
                    full_name = directors[0][1]
                    first_name = full_name[full_name.find(',') + 2:]
                    last_name = full_name[:full_name.find(',')]
                    entities_map['dir_ln'] = [(last_name, 1.0)]
                    entities_map['dir_fn'] = [(first_name, 1.0)]
                    if 'comp_ln' in entities_map:
                        entities_map.pop('comp_ln')
                    if 'comp_fn' in entities_map:
                        entities_map.pop('comp_fn')
                    if 'actor_ln' in entities_map:
                        entities_map.pop('actor_ln')
                    if 'actor_fn' in entities_map:
                        entities_map.pop('actor_fn')
                elif len(actors) > 0:
                    full_name = actors[0][1]
                    first_name = full_name[full_name.find(',') + 2:]
                    last_name = full_name[:full_name.find(',')]
                    entities_map['actor_ln'] = [(last_name, 1.0)]
                    entities_map['actor_fn'] = [(first_name, 1.0)]
                    if 'comp_ln' in entities_map:
                        entities_map.pop('comp_ln')
                    if 'comp_fn' in entities_map:
                        entities_map.pop('comp_fn')
                    if 'dir_ln' in entities_map:
                        entities_map.pop('dir_ln')
                    if 'dir_fn' in entities_map:
                        entities_map.pop('dir_fn')
                elif len(composers) > 0:
                    full_name = composers[0][1]
                    first_name = full_name[full_name.find(',') + 2:]
                    last_name = full_name[:full_name.find(',')]
                    entities_map['comp_ln'] = [(last_name, 1.0)]
                    entities_map['comp_fn'] = [(first_name, 1.0)]
                    if 'actor_ln' in entities_map:
                        entities_map.pop('actor_ln')
                    if 'actor_fn' in entities_map:
                        entities_map.pop('actor_fn')
                    if 'dir_ln' in entities_map:
                        entities_map.pop('dir_ln')
                    if 'dir_fn' in entities_map:
                        entities_map.pop('dir_fn')
                else:
                    print('Unknown name!')

            # fix movie name
            if 'movie_name' in entities_map:
                movie_name = entities_map['movie_name'][0][0]
                movie_name = self.fix_spelling(movie_name, self.all_movie_titles)
                print('Searching similar movie names...')
                similar_names = self.imdb.get_similar_titles(movie_name)
                print('Find closest')
                if len(similar_names) == 0:
                    print('Unknown movie!')
                else:
                    similar_names = [(similar_name, distance.levenshtein(similar_name[1].lower(), movie_name.lower())) for similar_name in similar_names]
                    similar_names = sorted(similar_names, key=lambda x: x[1])
                    print("Closest name to: '{movie_name}' is '{new_name}' with distance {distance}".format(movie_name=movie_name, new_name=similar_names[0][0][1], distance=similar_names[0][1]))

                    entities_map['movie_name'] = [(similar_names[0][0][1], 1.0 / (similar_names[0][1] + 1))]

            intent = intents[0][0]
            message_answer = Message()

            try:
                if intent == 'movie_name':
                    print('Get movie name.')
                    if len(entities) == 0:
                        print('No entity detected!')
                        message_answer.attachments.append(Attachment('text', 'No entity detected!'))

                    elif 'dir_ln' in entities_map and 'dir_fn' in entities_map and 'movie_genre' in entities_map:
                        director = {'first_name': entities_map['dir_fn'][0][0], 'last_name': entities_map['dir_ln'][0][0]}
                        genre = entities_map['movie_genre'][0][0]

                        print('find {genre} movies directed by: {0}'.format(director, genre=genre))
                        movies = self.imdb.get_movies_of_director_and_genre(director, genre)

                        if len(movies) == 0:
                            message_answer.attachments\
                                .append(Attachment('text',
                                                   'No {genre} movies were directed by {first_name} {last_name}.'
                                        .format(first_name=director['first_name'], last_name=director['last_name'],
                                                genre=genre)))
                        else:
                            message_answer.attachments\
                                .append(Attachment('text', '{genre} movies directed by {first_name} {last_name}:'
                                        .format(first_name=director['first_name'], last_name=director['last_name'],
                                                genre=genre.capitalize())))
                            message_answer.attachments\
                                .append(Attachment('list', [movie[1] for movie in movies[:10]]))

                    elif 'dir_ln' in entities_map and 'dir_fn' in entities_map:
                            director = {'first_name': entities_map['dir_fn'][0][0], 'last_name': entities_map['dir_ln'][0][0]}

                            print('find movies directed by: {0}'.format(director))
                            movies = self.imdb.get_movies_of_director(director)
                            if len(movies) == 0:
                                message_answer.attachments\
                                    .append(Attachment('text', 'No movies were directed by {first_name} {last_name}.'
                                            .format(first_name=director['first_name'], last_name=director['last_name'])))
                            else:
                                message_answer.attachments\
                                    .append(Attachment('text', 'Movies directed by {first_name} {last_name}:'
                                            .format(first_name=director['first_name'], last_name=director['last_name'])))
                                message_answer.attachments\
                                    .append(Attachment('list', [movie[1] for movie in movies[:10]]))

                    elif 'actor_ln' in entities_map and 'actor_fn' in entities_map and 'movie_genre' in entities_map:
                        actor = {'first_name': entities_map['actor_fn'][0][0], 'last_name': entities_map['actor_ln'][0][0]}
                        genre = entities_map['movie_genre'][0][0]
                        print('find {genre} movies with: {0}'.format(actor, genre=genre))
                        movies = self.imdb.get_movies_of_actor_and_genre(actor, genre)

                        if len(movies) == 0:
                            message_answer.attachments\
                                .append(Attachment('text', '{first_name} {last_name} did not star in any {genre} movies.'
                                        .format(first_name=actor['first_name'], last_name=actor['last_name'], genre=genre)))
                        else:
                            message_answer.attachments\
                                .append(Attachment('text', '{genre} movies starring {first_name} {last_name}:'
                                                   .format(first_name=actor['first_name'], last_name=actor['last_name'],
                                                           genre=genre.capitalize())))
                            message_answer.attachments\
                                .append(Attachment('list', [movie[1] for movie in movies[:10]]))

                    elif 'actor_ln' in entities_map and 'actor_fn' in entities_map:
                        actor = {'first_name': entities_map['actor_fn'][0][0], 'last_name': entities_map['actor_ln'][0][0]}
                        print('find movies with: {0}'.format(actor))
                        movies = self.imdb.get_movies_of_actor(actor)

                        if len(movies) == 0:
                            message_answer.attachments\
                                .append(Attachment('text', '{first_name} {last_name} did not star in any movies.'
                                        .format(first_name=actor['first_name'], last_name=actor['last_name'])))
                        else:
                            message_answer.attachments\
                                .append(Attachment('text', 'Movies starring {first_name} {last_name}:'
                                                   .format(first_name=actor['first_name'], last_name=actor['last_name'])))
                            message_answer.attachments\
                                .append(Attachment('list', [movie[1] for movie in movies[:10]]))

                    elif 'comp_ln' in entities_map and 'comp_fn' in entities_map and 'movie_genre' in entities_map:
                        composer = {'first_name': entities_map['comp_fn'][0][0], 'last_name': entities_map['comp_ln'][0][0]}
                        genre = entities_map['movie_genre'][0][0]
                        print('find {genre} movies with: {0}'.format(composer, genre=genre))
                        movies = self.imdb.get_movies_of_composer_and_genre(composer, genre)

                        if len(movies) == 0:
                            message_answer.attachments\
                                .append(Attachment('text', '{first_name} {last_name} did not compose any {genre} movies.'
                                        .format(first_name=composer['first_name'], last_name=composer['last_name'], genre=genre)))
                        else:
                            message_answer.attachments\
                                .append(Attachment('text', '{genre} movies composed by {first_name} {last_name}:'
                                                   .format(first_name=composer['first_name'], last_name=composer['last_name'],
                                                           genre=genre.capitalize())))
                            message_answer.attachments\
                                .append(Attachment('list', [movie[1] for movie in movies[:10]]))

                    elif 'comp_ln' in entities_map and 'comp_fn' in entities_map:
                        composer = {'first_name': entities_map['comp_fn'][0][0], 'last_name': entities_map['comp_ln'][0][0]}
                        print('find movies with: {0}'.format(composer))
                        movies = self.imdb.get_movies_of_composer(composer)

                        if len(movies) == 0:
                            message_answer.attachments\
                                .append(Attachment('text', '{first_name} {last_name} did not compose any movies.'
                                        .format(first_name=composer['first_name'], last_name=composer['last_name'])))
                        else:
                            message_answer.attachments\
                                .append(Attachment('text', 'Movies composed by {first_name} {last_name}:'
                                                   .format(first_name=composer['first_name'], last_name=composer['last_name'])))
                            message_answer.attachments\
                                .append(Attachment('list', [movie[1] for movie in movies[:10]]))

                    elif 'movie_genre' in entities_map:
                        genre = entities_map['movie_genre'][0][0]
                        print('Find {genre} movies.'.format(genre=genre))
                        movies = self.imdb.get_movies_of_genre(genre)

                        if len(movies) == 0:
                            message_answer.attachments\
                                .append(Attachment('text', 'The genre {genre} is not known!'.format(genre=genre)))
                        else:
                            message_answer.attachments\
                                .append(Attachment('text', 'Some {genre} movies:'.format(genre=genre)))
                            message_answer.attachments\
                                .append(Attachment('list', [movie[1] for movie in movies[:10]]))

                    else:
                        message_answer.attachments.append(Attachment('text', 'Unknown intent-entity combination! {0} - {1}'
                                                                     .format(intent, entities)))

                elif intent == 'actor_name':
                    print('Get actor name.')
                    if 'movie_name' in entities_map:
                        movie_name = entities_map['movie_name'][0][0]
                        actors = self.imdb.get_actors_of_movie(movie_name)
                        if len(actors) == 0:
                            message_answer.attachments \
                                .append(Attachment('text',
                                                   'No actors found for {movie_name}!'.format(movie_name=movie_name)))
                        else:
                            message_answer.attachments \
                                .append(Attachment('text', 'Actors in {movie_name}:'.format(movie_name=movie_name)))
                            message_answer.attachments \
                                .append(Attachment('list', [actor[1] for actor in actors[:10]]))
                    else:
                        print('Missed movie name!')
                        message_answer.attachments.append(Attachment('text', 'Missed the name of the movie.'))

                elif intent == 'dir_name':
                    print('Get director name.')
                    if 'movie_name' in entities_map:
                        movie_name = entities_map['movie_name'][0][0]
                        directors = self.imdb.get_directors_of_movie(movie_name)
                        if len(directors) == 0:
                            message_answer.attachments \
                                .append(Attachment('text',
                                                   'No director found for {movie_name}!'.format(movie_name=movie_name)))
                        elif len(directors) == 1:
                            message_answer.attachments \
                                .append(Attachment('text', '{director} directed {movie_name}:'.format(director=directors[0][1], movie_name=movie_name)))
                        else:
                            message_answer.attachments \
                                .append(Attachment('text', 'Directors of {movie_name}:'.format(movie_name=movie_name)))
                            message_answer.attachments \
                                .append(Attachment('list', [director[1] for director in directors[:10]]))

                    else:
                        print('Missed movie name!')
                        message_answer.attachments.append(Attachment('text', 'Missed the name of the movie.'))

                elif intent == 'comp_name':
                    print('Get composers name.')
                    if 'movie_name' in entities_map:
                        movie_name = entities_map['movie_name'][0][0]
                        composers = self.imdb.get_composers_of_movie(movie_name)
                        if len(composers) == 0:
                            message_answer.attachments \
                                .append(Attachment('text',
                                                   'No composer found for {movie_name}!'.format(movie_name=movie_name)))
                        elif len(composers) == 1:
                            message_answer.attachments \
                                .append(Attachment('text', '{composer} composed {movie_name}:'.format(composer=composers[0][1], movie_name=movie_name)))
                        else:
                            message_answer.attachments \
                                .append(Attachment('text', 'Composers of {movie_name}:'.format(movie_name=movie_name)))
                            message_answer.attachments \
                                .append(Attachment('list', [composer[1] for composer in composers[:10]]))

                    else:
                        print('Missed movie name!')
                        message_answer.attachments.append(Attachment('text', 'Missed the name of the movie.'))

                else:
                    message_answer.attachments.append(Attachment('text', 'Unknown Intent!'))
            except Exception as err:
                print("Unexpected error:", sys.exc_info()[0])
                self.logger.exception("Unexpected error while parsing intent...")
                message_answer.attachments.append(Attachment('text', 'Sorry something went wrong internally!'))

            message_answer.session_id = session_id
            message_answer.actor = 'bot'

            message_answer.extra = Extra()
            message_answer.extra.intents = intents
            message_answer.extra.query = question
            message_answer.extra.entities = entities

        elapsed = int(time()*(10**6)) - start_time
        message_answer.extra.time_required = elapsed

        self.logger.info(log_message.format(query_plain=message_question.attachments[0].content,
                                            query=message_question.to_string(), intents=intents, entities=entities,
                                            answer_plain=message_answer.attachments[0].content,
                                            answer=message_answer.to_string()))

        if not message_question.attachments[0].content.startswith(':'):
            self.logger_questions.info(message_question.attachments[0].content)

        return message_answer
