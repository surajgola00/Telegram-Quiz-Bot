import mysql.connector
import random
from details import config

class db():
    @staticmethod
    def user_command(command:str):
        try:
            conn = get_db_connection()
            if conn is None:
                return None
            cursor = conn.cursor(dictionary=True)
            cursor.execute(command)
            data = cursor.fetchall()
            return data
        except Exception:
            return None
        finally:
            conn.close()
            cursor.close()


    @staticmethod
    def get_logs():
        try:
            conn = get_db_connection()
            if conn is None:
                return None
            cursor = conn.cursor(dictionary=True)
            query = 'SELECT * from error_logs;'
            cursor.execute(query)
            log = cursor.fetchall()
            return log
        except Exception:
            return 
        finally:
            cursor.close()
            conn.close()
    

    @staticmethod
    def delete_log():
        conn = get_db_connection()
        if conn is None:
            return False

        cur = conn.cursor()
        try:
            query = 'DELETE FROM error_logs;'
            cur.execute(query)
            conn.commit()  # Commit the transaction
            return True
        except Exception as e:
            conn.rollback()  # Rollback the transaction in case of error
            return False
        finally:
            cur.close()  # Close the cursor
            conn.close()  # Close the connection


    @staticmethod
    def log_error(error_message, location):
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        query = 'INSERT INTO error_logs (error_message, location) VALUES (%s, %s);'
        values = (error_message, location)
        try:
            cursor.execute(query, values)
            conn.commit()
        except Exception as e:
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def check_ques_presence(category, question):
        query = 'SELECT COUNT(*) as is_present FROM questions WHERE q=%s AND category=%s;'
        values = (question, category)  # Correct the order of parameters
        result = db.execute_query(query, values)
        if result['is_present'] > 0:
            return True
        return False

    @staticmethod
    def update_score(tg_id, category, score):
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        try:
            query = 'UPDATE user_score SET {}=%s WHERE tg_id=%s;'.format(category)
            values = (score, tg_id)
            cursor.execute(query, values)
            conn.commit()
        except Exception as e:
            db.log_error(str(e), 'update_score')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def execute_query(query, params):
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            result = cursor.fetchone()
        except mysql.connector.Error as e:
            db.log_error(str(e), 'execute_query')
            result = None
            conn.rollback()
        finally:
            cursor.close()
        return result


    @staticmethod
    def execute_query_multiple(query, params=None):
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
        except mysql.connector.Error as e:
            db.log_error(str(e), 'execute_query_multiple')
            results = []
        finally:
            cursor.close()
            conn.close()
        return results

    @staticmethod
    def get_user_data():
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        query = 'SELECT * FROM users;'
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results

    @staticmethod
    def get_user_score(tg_id, category):
        query = 'SELECT {} FROM user_score WHERE tg_id=%s;'.format(category)
        params = (tg_id,)
        results = db.execute_query(query, params)
        if results is None:
            return None
        return results[category]

    @staticmethod
    def initialise_user(msg):
        conn = get_db_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        user_id = msg.from_user.id
        query = 'INSERT IGNORE INTO users (tg_id, user_name, name) VALUES (%s, %s, %s);'
        values = (msg.from_user.id, msg.from_user.username, msg.from_user.first_name)
        cursor.execute(query, values)

        query = 'INSERT IGNORE INTO user_score (tg_id) VALUES (%s);'
        values = (msg.from_user.id,)
        cursor.execute(query, values)

        # Commit the transaction
        conn.commit()
        conn.close()
        cursor.close()

    @staticmethod
    def get_question(category, q_no):
        query = 'SELECT * FROM questions WHERE category=%s AND q_no=%s;'
        params = (category, q_no)
        results = db.execute_query(query, params)
        if results is None:
            return None
        return results

    @staticmethod
    def get_categories():
        conn = get_db_connection()
        if conn is None:
            return None
        try:
            query = """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'user_score'
            AND COLUMN_NAME != 'tg_id';
            """
            cursor = conn.cursor()
            cursor.execute(query)
            columns = cursor.fetchall()
        finally:
            conn.close()
            cursor.close()

        # Extract the column names from the result
        categories = [column[0] for column in columns]
        return categories

    @staticmethod
    def get_total_no_q(category):
        query = 'select count(*) as count from questions where category=%s;'
        value = (category,)
        result = db.execute_query(query, value)
        return result['count']


    @staticmethod
    def insert_data(dic):
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        total_q = db.get_total_no_q(dic['category'])

        # Ensure 'options' is a list before shuffling
        options_list = dic['options']
        if isinstance(options_list, str):
            options_list = options_list.split(",")  # Convert string to list if necessary

        random.shuffle(options_list)
        options = ','.join(options_list)  # Join options back into a string

        query = '''
            INSERT INTO questions
            (category, q_no, q, ans, options, hint, info)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        '''
        values = (
            dic['category'],
            total_q + 1,
            dic['q'],
            dic['ans'],
            options,
            dic['hint'],
            dic['info']
        )

        try:
            cursor.execute(query, values)
            conn.commit()
        except Exception as e:
            conn.rollback()
        finally:
            cursor.close()
            conn.close()



try:
    x = mysql.connector.connect(**config)
except mysql.connector.Error as e:
    db.log_error(str(e), 'Database Connection')

def get_db_connection():
    try:
        if not x.is_connected():
            x.reconnect(attempts=3, delay=5)
        return x
    except mysql.connector.Error as e:
        db.log_error(str(e), 'Database Connection')
        return None