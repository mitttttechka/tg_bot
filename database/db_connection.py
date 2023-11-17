import psycopg2
import logging
import redis


class Connection:
    conn = None
    rdb = None


def connect():
    """ Connect to the PostgreSQL database server """
    # conn = None
    try:

        # connect to the PostgreSQL server
        logging.info('Connecting to the PostgreSQL database...')
        Connection.conn = psycopg2.connect(
            host="localhost",
            database="tg_bot_develop",
            user="mitttttechka",
            password="",
            port="5432")
        logging.info('PostgreSQL database successfully connected.')

        logging.info('Connecting to the Redis database...')
        Connection.rdb = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True)
        logging.info('Redis database successfully connected.')

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)


def disconnect():
    Connection.conn.commit()
    if Connection.conn is not None:
        Connection.conn.close()
        logging.info('Database connection closed.')


def send_query(query):
    if Connection.conn is None:
        logging.error('No connection to the database')
        return 0
    cur = Connection.conn.cursor()
    cur.execute(query)
    if query[0:6].strip().lower() == 'select':
        answer = cur.fetchall()
    else:
        answer = 1
    Connection.conn.commit()
    cur.close()
    return answer
