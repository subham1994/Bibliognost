import psycopg2
from flask import g


class PostgresConnection:
    def __init__(self, config):
        self.__connection = None
        self.__db_config = config['db']

    def init_app(self, app):
        @app.before_request
        def get_db():
            """Opens a new database connection if there is none yet"""
            if not hasattr(g, 'db'):
                try:
                    self.__connection = psycopg2.connect(**self.__db_config)
                except psycopg2.DatabaseError as e:
                    print('DatabaseError: could not connect to the databse, ({})'.format(e))
                else:
                    g.db = self.__connection

        @app.teardown_appcontext
        def close_db(exception):
            """Closes the database at the end of the request."""
            if hasattr(g, 'db') and self.__connection.close:
                self.__connection.commit()
                self.__connection.close()
            return exception
