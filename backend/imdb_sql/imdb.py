import mysql.connector
import re


class IMDB():
    def __init__(self):
        self.connection = mysql.connector.connect(host="localhost", user="user", passwd="password", db="imdb")

        self.template_get_movies_of_director = "SELECT title.id, title.title FROM title " \
            "INNER JOIN kind_type on kind_type.id = title.kind_id and (kind_type.kind = 'movie' or kind_type.kind = 'tv movie' or kind_type.kind = 'video movie') " \
            "INNER JOIN cast_info on title.id = cast_info.movie_id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and role_type.role = 'director' " \
            "INNER JOIN name on cast_info.person_id = name.id and name.name LIKE '{last_name}, {first_name}'" \
            "INNER JOIN movie_info_idx on title.id = movie_info_idx.movie_id " \
            "INNER JOIN info_type on movie_info_idx.info_type_id = info_type.id and info_type.info = 'rating' " \
            "GROUP BY title.id, title.title " \
            "ORDER BY movie_info_idx.info DESC " \
            "LIMIT 10 " \
            ";"
        self.template_get_movies_of_director_and_genre = "SELECT title.id, title.title FROM title " \
            "INNER JOIN kind_type on kind_type.id = title.kind_id and (kind_type.kind = 'movie' or kind_type.kind = 'tv movie' or kind_type.kind = 'video movie') " \
            "INNER JOIN cast_info on title.id = cast_info.movie_id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and role_type.role = 'director' " \
            "INNER JOIN name on cast_info.person_id = name.id and name.name LIKE '{last_name}, {first_name}'" \
            "INNER JOIN movie_info on title.id = movie_info.movie_id and movie_info.info = '{genre}' " \
            "INNER JOIN info_type on movie_info.info_type_id = info_type.id and info_type.info = 'genres' " \
            "INNER JOIN movie_info_idx on title.id = movie_info_idx.movie_id " \
            "INNER JOIN info_type it on movie_info_idx.info_type_id = it.id and it.info = 'rating' " \
            "GROUP BY title.id, title.title " \
            "ORDER BY movie_info_idx.info DESC " \
            "LIMIT 10 " \
            ";"

        self.template_get_movies_of_composer = "SELECT title.id, title.title FROM title " \
            "INNER JOIN kind_type on kind_type.id = title.kind_id and (kind_type.kind = 'movie' or kind_type.kind = 'tv movie' or kind_type.kind = 'video movie') " \
            "INNER JOIN cast_info on title.id = cast_info.movie_id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and role_type.role = 'composer' " \
            "INNER JOIN name on cast_info.person_id = name.id and name.name LIKE '{last_name}, {first_name}'" \
            "INNER JOIN movie_info_idx on title.id = movie_info_idx.movie_id " \
            "INNER JOIN info_type on movie_info_idx.info_type_id = info_type.id and info_type.info = 'rating' " \
            "GROUP BY title.id, title.title " \
            "ORDER BY movie_info_idx.info DESC " \
            "LIMIT 10 " \
            ";"
        self.template_get_movies_of_composer_and_genre = "SELECT title.id, title.title FROM title " \
            "INNER JOIN kind_type on kind_type.id = title.kind_id and (kind_type.kind = 'movie' or kind_type.kind = 'tv movie' or kind_type.kind = 'video movie') " \
            "INNER JOIN cast_info on title.id = cast_info.movie_id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and role_type.role = 'composer' " \
            "INNER JOIN name on cast_info.person_id = name.id and name.name LIKE '{last_name}, {first_name}'" \
            "INNER JOIN movie_info on title.id = movie_info.movie_id and movie_info.info = '{genre}' " \
            "INNER JOIN info_type on movie_info.info_type_id = info_type.id and info_type.info = 'genres' " \
            "INNER JOIN movie_info_idx on title.id = movie_info_idx.movie_id " \
            "INNER JOIN info_type it on movie_info_idx.info_type_id = it.id and it.info = 'rating' " \
            "GROUP BY title.id, title.title " \
            "ORDER BY movie_info_idx.info DESC " \
            "LIMIT 10 " \
            ";"

        self.template_get_movies_of_actor = "SELECT title.id, title.title FROM title " \
            "INNER JOIN kind_type on kind_type.id = title.kind_id and (kind_type.kind = 'movie' or kind_type.kind = 'tv movie' or kind_type.kind = 'video movie') " \
            "INNER JOIN cast_info on title.id = cast_info.movie_id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and (role_type.role = 'actor' or role_type.role = 'actress') " \
            "INNER JOIN name on cast_info.person_id = name.id and name.name LIKE '{last_name}, {first_name}'" \
            "INNER JOIN movie_info_idx on title.id = movie_info_idx.movie_id " \
            "INNER JOIN info_type on movie_info_idx.info_type_id = info_type.id and info_type.info = 'rating' " \
            "GROUP BY title.id, title.title " \
            "ORDER BY movie_info_idx.info DESC " \
            "LIMIT 10 " \
            ";"
        self.template_get_movies_of_actor_and_genre = "SELECT title.id, title.title FROM title " \
            "INNER JOIN kind_type on kind_type.id = title.kind_id and (kind_type.kind = 'movie' or kind_type.kind = 'tv movie' or kind_type.kind = 'video movie') " \
            "INNER JOIN cast_info on title.id = cast_info.movie_id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and (role_type.role = 'actor' or role_type.role = 'actress') " \
            "INNER JOIN name on cast_info.person_id = name.id and name.name LIKE '{last_name}, {first_name}'" \
            "INNER JOIN movie_info on title.id = movie_info.movie_id and movie_info.info = '{genre}' " \
            "INNER JOIN info_type on movie_info.info_type_id = info_type.id and info_type.info = 'genres' " \
            "INNER JOIN movie_info_idx on title.id = movie_info_idx.movie_id " \
            "INNER JOIN info_type it on movie_info_idx.info_type_id = it.id and it.info = 'rating' " \
            "WHERE movie_info.info = '{genre}' " \
            "GROUP BY title.id, title.title " \
            "ORDER BY movie_info_idx.info DESC " \
            "LIMIT 10 " \
            ";"

        self.template_get_movies_of_genre = "SELECT title.id, title.title FROM title " \
            "INNER JOIN kind_type on kind_type.id = title.kind_id and (kind_type.kind = 'movie' or kind_type.kind = 'tv movie' or kind_type.kind = 'video movie') " \
            "INNER JOIN movie_info on title.id = movie_info.movie_id and movie_info.info = '{genre}' " \
            "INNER JOIN movie_info_idx on title.id = movie_info_idx.movie_id " \
            "INNER JOIN info_type on movie_info.info_type_id = info_type.id or movie_info_idx.info_type_id = info_type.id and (info_type.info = 'genres' or info_type.info = 'rating')" \
            "GROUP BY title.id, title.title " \
            "ORDER BY movie_info_idx.info DESC " \
            "LIMIT 10 " \
            ";"

        self.template_get_actors_of_movie = "SELECT name.id, name.name, MAX(actor_ratings.rating) as rating FROM title " \
            "INNER JOIN kind_type on kind_type.id = title.kind_id and (kind_type.kind = 'movie' or kind_type.kind = 'tv movie' or kind_type.kind = 'video movie') " \
            "INNER JOIN cast_info on cast_info.movie_id = title.id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and (role_type.role = 'actor' or role_type.role = 'actress') " \
            "INNER JOIN name on cast_info.person_id = name.id " \
            "INNER JOIN actor_ratings on actor_ratings.actor_id = name.id " \
            "WHERE title.title = '{title}'" \
            "GROUP BY name.id, name.name " \
            "ORDER BY rating DESC " \
            "LIMIT 10 " \
            ";"
        self.template_get_directors_of_movie = "SELECT name.id, name.name FROM title " \
            "INNER JOIN kind_type on kind_type.id = title.kind_id and (kind_type.kind = 'movie' or kind_type.kind = 'tv movie' or kind_type.kind = 'video movie') " \
            "INNER JOIN cast_info on cast_info.movie_id = title.id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and role_type.role = 'director' " \
            "INNER JOIN name on cast_info.person_id = name.id " \
            "WHERE title.title = '{title}'" \
            "LIMIT 10 " \
            ";"
        self.template_get_composers_of_movie = "SELECT name.id, name.name FROM title " \
            "INNER JOIN kind_type on kind_type.id = title.kind_id and (kind_type.kind = 'movie' or kind_type.kind = 'tv movie' or kind_type.kind = 'video movie') " \
            "INNER JOIN cast_info on cast_info.movie_id = title.id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and role_type.role = 'composer' " \
            "INNER JOIN name on cast_info.person_id = name.id " \
            "WHERE title.title = '{title}'" \
            "LIMIT 10 " \
            ";"

        self.template_get_movie_titles = "SELECT title.id, title.title FROM title WHERE title.title LIKE '%{title}%'"
        self.template_get_director_by_name = "SELECT name.id, name.name, COUNT(cast_info.id) as num_movies FROM name " \
            "INNER JOIN cast_info on cast_info.person_id = name.id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and role_type.role = 'director' " \
            "WHERE name.name LIKE '{last_name}, {first_name}' " \
            "GROUP BY name.id, name.name " \
            "ORDER BY num_movies DESC " \
            ";"
        self.template_get_actor_by_name = "SELECT name.id, name.name, COUNT(cast_info.id) as num_movies FROM name " \
            "INNER JOIN cast_info on cast_info.person_id = name.id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and (role_type.role = 'actor' or role_type.role = 'actress') " \
            "WHERE name.name LIKE '{last_name}, {first_name}' " \
            "GROUP BY name.id, name.name " \
            "ORDER BY num_movies DESC " \
            ";"
        self.template_get_composer_by_name = "SELECT name.id, name.name, COUNT(cast_info.id) as num_movies FROM name " \
            "INNER JOIN cast_info on cast_info.person_id = name.id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and role_type.role = 'composer' " \
            "WHERE name.name LIKE '{last_name}, {first_name}' " \
            "GROUP BY name.id, name.name " \
            "ORDER BY num_movies DESC " \
            ";"

        self.template_get_movies_about_keyword = "SELECT title.id, title.title FROM title " \
            "INNER JOIN movie_keyword on title.id = movie_keyword.movie_id " \
            "INNER JOIN keyword on keyword.id = movie_keyword.keyword_id " \
            "WHERE keyword.keyword LIKE '{keyword}' " \
            "GROUP BY title.id, title.title " \
            "ORDER BY COUNT(keyword.id)"

        self.template_get_all_actor_names = "SELECT DISTINCT name.name FROM name " \
            "INNER JOIN cast_info on cast_info.person_id = name.id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and (role_type.role = 'actor' or role_type.role = 'actress') "
        self.template_get_all_director_names = "SELECT DISTINCT name.name FROM name " \
            "INNER JOIN cast_info on cast_info.person_id = name.id " \
            "INNER JOIN role_type on cast_info.role_id = role_type.id and role_type.role = 'director' "
        self.template_get_all_movie_names = "SELECT DISTINCT title.title FROM title " \
            "INNER JOIN kind_type on kind_type.id = title.kind_id and (kind_type.kind = 'movie' or kind_type.kind = 'tv movie' or kind_type.kind = 'video movie') " \
            "INNER JOIN movie_info_idx on title.id = movie_info_idx.movie_id " \
            "INNER JOIN info_type on movie_info_idx.info_type_id = info_type.id and info_type.info = 'rating' " \
            "ORDER BY movie_info_idx.info DESC "
        self.template_get_all_genres = "SELECT DISTINCT movie_info.info FROM movie_info " \
                                       "INNER JOIN info_type on movie_info.info_type_id = info_type.id and info_type.info = 'genres'"

    def get_similar_titles(self, movie_name):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_movie_titles.format(title=movie_name))
        rows = cursor.fetchall()

        print('Found {0} rows for movie title similar to: {1}.'.format(len(rows), movie_name))

        self.connection.commit()
        cursor.close()
        return rows

    def get_movies_of_composer(self, composer):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_movies_of_composer
                       .format(first_name=composer['first_name'], last_name=composer['last_name']))
        rows = cursor.fetchall()

        print('Found {0} rows for movies of composer {1}'.format(len(rows), composer))

        if len(rows) == 0:
            print('Should look for aka names etc...')

        self.connection.commit()
        cursor.close()
        return rows

    def get_movies_of_composer_and_genre(self, composer, genre):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_movies_of_composer_and_genre
                       .format(first_name=composer['first_name'], last_name=composer['last_name'], genre=genre))
        rows = cursor.fetchall()

        print('Found {0} rows for {genre} movies of composer {1}'.format(len(rows), composer, genre=genre))

        if len(rows) == 0:
            print('Should look for aka names etc...')

        self.connection.commit()
        cursor.close()
        return rows

    def get_movies_of_director(self, director):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_movies_of_director
                       .format(first_name=director['first_name'], last_name=director['last_name']))
        rows = cursor.fetchall()

        print('Found {0} rows for movies of director {1}'.format(len(rows), director))

        if len(rows) == 0:
            print('Should look for aka names etc...')

        self.connection.commit()
        cursor.close()
        return rows

    def get_movies_of_director_and_genre(self, director, genre):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_movies_of_director_and_genre
                       .format(first_name=director['first_name'], last_name=director['last_name'], genre=genre))
        rows = cursor.fetchall()

        print('Found {0} rows for {genre} movies of director {1}'.format(len(rows), director, genre=genre))

        if len(rows) == 0:
            print('Should look for aka names etc...')

        self.connection.commit()
        cursor.close()
        return rows

    def get_movies_of_actor(self, actor):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_movies_of_actor
                       .format(first_name=actor['first_name'], last_name=actor['last_name']))
        rows = cursor.fetchall()

        print('Found {0} rows for movies of actor {1}'.format(len(rows), actor))

        if len(rows) == 0:
            print('Should look for aka names etc...')

        self.connection.commit()
        cursor.close()
        return rows

    def get_movies_of_actor_and_genre(self, actor, genre):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_movies_of_actor_and_genre
                       .format(first_name=actor['first_name'], last_name=actor['last_name'], genre=genre))
        rows = cursor.fetchall()

        print('Found {0} rows for movies of actor {1}'.format(len(rows), actor))

        if len(rows) == 0:
            print('Should look for aka names etc...')

        self.connection.commit()
        cursor.close()
        return rows

    def get_movies_of_genre(self, genre):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_movies_of_genre.format(genre=genre))
        rows = cursor.fetchall()

        print('Found {0} rows for movies of genre {1}'.format(len(rows), genre))

        self.connection.commit()
        cursor.close()
        return rows

    def get_actors_of_movie(self, movie):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_actors_of_movie.format(title=movie))
        rows = cursor.fetchall()

        print('Found {0} rows for actors in {1}'.format(len(rows), movie))

        self.connection.commit()
        cursor.close()
        return rows

    def get_directors_of_movie(self, movie):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_directors_of_movie.format(title=movie))
        rows = cursor.fetchall()

        print('Found {0} rows for directors in {1}'.format(len(rows), movie))

        self.connection.commit()
        cursor.close()
        return rows

    def get_composers_of_movie(self, movie):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_composers_of_movie.format(title=movie))
        rows = cursor.fetchall()

        print('Found {0} rows for composers in {1}'.format(len(rows), movie))

        self.connection.commit()
        cursor.close()
        return rows

    def get_composer_names_by_name(self, composer):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_composer_by_name.format(first_name=composer['first_name'], last_name=composer['last_name']))
        rows = cursor.fetchall()

        print('Found {0} rows for composer names corresponding to {1}'.format(len(rows), composer))

        self.connection.commit()
        cursor.close()
        return rows

    def get_director_names_by_name(self, director):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_director_by_name.format(first_name=director['first_name'], last_name=director['last_name']))
        rows = cursor.fetchall()

        print('Found {0} rows for director names corresponding to {1}'.format(len(rows), director))

        self.connection.commit()
        cursor.close()
        return rows

    def get_actor_names_by_name(self, actor):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_actor_by_name.format(first_name=actor['first_name'], last_name=actor['last_name']))
        rows = cursor.fetchall()

        print('Found {0} rows for actor names corresponding to {1}'.format(len(rows), actor))

        self.connection.commit()
        cursor.close()
        return rows

    def get_movies_about_keyword(self, keyword):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_movies_about_keyword.format(keyword=keyword))
        rows = cursor.fetchall()

        print('Found {0} rows for movies about {1}'.format(len(rows), keyword))

        self.connection.commit()
        cursor.close()
        return rows

    def get_all_actor_names(self):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_all_actor_names)
        names = cursor.fetchall()
        names = [(name[0][:name[0].find(',')], name[0][name[0].find(',') + 2:]) for name in names]

        self.connection.commit()
        cursor.close()
        return names

    def get_all_director_names(self):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_all_director_names)
        names = cursor.fetchall()
        names = [(name[0][:name[0].find(',')], name[0][name[0].find(',') + 2:]) for name in names]

        self.connection.commit()
        cursor.close()
        return names

    def get_all_movie_names(self):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_all_movie_names)
        movies = cursor.fetchall()

        self.connection.commit()
        cursor.close()
        return [movie[0] for movie in movies]

    def get_all_genres(self):
        cursor = self.connection.cursor()
        cursor.execute(self.template_get_all_genres)
        genres = cursor.fetchall()

        self.connection.commit()
        cursor.close()
        return [genre[0] for genre in genres]

    def create_actor_ratings_table(self):
        cursor = self.connection.cursor()
        print('Drop table...')
        cursor.execute('DROP TABLE IF EXISTS actor_ratings')
        self.connection.commit()
        cursor.close()
        cursor = self.connection.cursor()
        print('Create table...')
        cursor.execute('CREATE TABLE actor_ratings (id INT NOT NULL AUTO_INCREMENT, actor_id INT, rating DOUBLE, PRIMARY KEY (id))')
        self.connection.commit()
        cursor.close()

        cursor = self.connection.cursor(buffered=True)
        insert_cursor = self.connection.cursor()

        print('Select all actors...')
        cursor.execute("SELECT DISTINCT name.id, name.name FROM name "
            "INNER JOIN cast_info on name.id = cast_info.person_id "
            "INNER JOIN role_type on cast_info.role_id = role_type.id and (role_type.role = 'actor' or role_type.role = 'actress') ")

        for num, actor in enumerate(cursor):
            person_info_cursor = self.connection.cursor()
            person_info_cursor.execute("SELECT person_info.info FROM person_info "
                "INNER JOIN info_type on info_type.id = person_info.info_type_id AND info_type.info = 'salary history' "
                "WHERE person_info.person_id = {actor_id}".format(actor_id=actor[0]))

            salaries = []
            for salary_history in person_info_cursor:
                str = salary_history[0]

                if '::' in str:
                    str = str[str.find('::') + 2:]
                    if len(str) > 0 and str[0] == '$':
                        str = str[1:]

                    str = re.sub("[^0-9]", " ", str.replace(',', ''))

                    if ' ' in str:
                        str = str[:str.find(' ')]

                    if str != '':
                        try:
                            salaries.append(int(str))
                        except Exception as ex:
                            print(ex)
                else:
                    try:
                        salaries.append(int(str))
                    except Exception as ex:
                        print(ex)

            person_info_cursor.close()
            total = sum(salaries)

            person_info_cursor = self.connection.cursor()
            person_info_cursor.execute("SELECT COUNT(cast_info.id) as num_movies FROM cast_info "
                "INNER JOIN name on name.id = cast_info.person_id "
                "WHERE name.id = {actor_id} "
                "GROUP BY name.id".format(actor_id=actor[0]))

            movie_count = person_info_cursor.fetchall()
            if len(movie_count) > 0:
                total += movie_count[0][0]

            if num % 100 == 0:
                print('{num}\t\t{name}:\t{rating}'.format(name=actor[1], rating=total, num=num))
                self.connection.commit()

            insert_cursor.execute("INSERT INTO actor_ratings (actor_id, rating) VALUES ('{id}','{rating}')".format(id=actor[0], rating=total))

        self.connection.commit()
        insert_cursor.close()
        cursor.close()
