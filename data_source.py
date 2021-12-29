import psycopg2
import logging

from message_data import ReminderData

logger = logging.getLogger()

SELECT_ALL_REMINDERS_STATEMENT = """SELECT * FROM reminders;"""

INSERT_REMINDER_STATEMENT = """
    INSERT INTO reminders(chat_id, message, time)
    VALUES(%s, %s, %s)
    RETURNING reminder_id, chat_id, message, time, fired;
"""

FIRE_REMINDER_STATEMENT = """
    UPDATE reminders
    SET fired = true
    WHERE reminder_id = %s;
"""


class DataSource:
    def __init__(self, database_url):
        self.database_url = database_url

    def get_connection(self):
        return psycopg2.connect(self.database_url, sslmode='allow')

    @staticmethod
    def close_connection(conn):
        if conn:
            conn.close()

    def create_tables(self):
        commands = (
            """
                CREATE TABLE if not exists reminders(
                    reminder_id serial PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    message VARCHAR(300) NOT NULL,
                    time TIMESTAMP NOT NULL,
                    fired BOOLEAN NOT NULL DEFAULT FALSE
                );
            """,
        )
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                for command in commands:
                    cur.execute(command)
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)

    def get_all_reminders(self):
        conn = None
        reminders = list()
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(SELECT_ALL_REMINDERS_STATEMENT)
                for row in cur.fetchall():
                    reminders.append(ReminderData(row))
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)
            return reminders

    def create_reminder(self, chat_id, message, time):
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(INSERT_REMINDER_STATEMENT, (chat_id, message, time,))
                row = cur.fetchone()
                conn.commit()
            return ReminderData(row)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)

    def fire_reminder(self, reminder_id):
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(FIRE_REMINDER_STATEMENT, (reminder_id,))
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)
