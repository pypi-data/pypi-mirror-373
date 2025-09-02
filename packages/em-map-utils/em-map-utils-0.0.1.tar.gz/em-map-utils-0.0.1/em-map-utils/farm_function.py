"""
farm_function.py

Author: Ardan Patwardhan
Affiliation: EMBL-EBI, Wellcome Genome Campus, CB10 1SD, UK
Date: 25/08/2025
Description: 
    Run multiple processes of the same function, changing one parameter
    and collecting any results in a JSON file.
"""

import json
import logging
import multiprocessing as mp
import random
import sqlite3 as sql
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class FarmFunction:
    """
    Run multiple processes of a function f(v, args, kwargs), mapping
    v over a list of values and collecting the results in a JSON file.

    In contrast with the Pool function of multiprocessing, this class
    can attempt multiple tries of the function before giving up.
    """

    max_cpu = mp.cpu_count()

    def __init__(self, f, values, args=[], kwargs={},
                 num_workers=2,
                 max_tries=2,
                 monitoring_interval=5,
                 file_root = "dummy",
                 resume = False,
                 retry = False):
        """
        Initialise and run worker processes to run function with
        different values.

        This is the only method that needs to be called as it will
        also write the results to a JSON file.

        :param f: Function to run. The function must either return a
            boolean value or a tuple(status, result_dict) where status
            is a boolean and result_dict is the output of running the
            function.
        :param values: A list of values to pass to f.
        :param args:  Arguments to pass to f that do not change.
        :param kwargs: Keyword arguments to pass to f that do not
            change.
        :param num_workers: Number of worker processes to run. The
            number is checked and capped at the number of available
            CPUs.
        :param max_tries: Number of attempts to retry the function.
        :param monitoring_interval: How often (in seconds) to check the
            progress of the worker processes.
        :param file_root: The root of the database and output files.
        :param resume: If True, the database and processes are loaded
            from file and resumed.
        :param retry: If True, items will be moved from the failed
            table to the processing table with num_tries reset so that
            they can be run again. This option is only relevant if
            resume is True.
        """
        self.f = f
        self.values = values
        self.args = args
        self.kwargs = kwargs
        self.num_workers = max( 1, min(num_workers, FarmFunction.max_cpu))
        self.max_tries = max_tries
        self.monitoring_interval = monitoring_interval

        self.file_root = file_root
        self.db_name = f'{self.file_root}.db'
        self.output_file = f'{self.file_root}.json'

        self.resume = resume
        self.retry = retry

        self.process_queue = mp.Queue()
        self.success_queue = mp.Queue()
        self.fail_queue = mp.Queue()
        self.num_processed = mp.Value('i', 0)
        self.num_error = mp.Value('i', 0)
        self.num_success = mp.Value('i', 0)
        self.old_values = []
        self.lock = mp.Lock()

        self.__setup()

    def __setup(self):
        """
        Create/load database, add items to process queue, and start
        processing them.

        :return: No return value.
        """
        if self.resume:
            self.__load_from_db()
        else:
            self.__create_db()

        con = sql.connect(self.db_name, check_same_thread=False)
        for x in self.values:
            self.__add_to_processing(con, None, x)
        con.close()
        self.values.extend(self.old_values)
        self.num_values = len(self.values)

        mp.Process(target=self.__monitor).start()

        for i in range(self.num_workers):
            mp.Process(target=self.__worker).start()


    def __monitor(self):
        """
        Process to monitor worker processes.

        When all the items are processed, the workers are killed and
        the output written to file.

        :return: No return value.
        """
        while self.num_processed.value < self.num_values:
            time.sleep(self.monitoring_interval)

        logger.debug(f'All values processed. Sending termination signal to processes.')
        for _ in range(self.num_workers):
            self.process_queue.put(None)

        con = sql.connect(self.db_name, check_same_thread=False)
        self.write_to_files(con)
        # cur = con.cursor()
        # print(f'Failed entries\n')
        # for row in cur.execute("SELECT id, value FROM failed ORDER BY id"):
        #     print(f'ID= {row[0]}, value= {row[1]}')
        con.close()

    def __inc_num_processed(self):
        """
        Increment counter to track processed values.

        :return: No return value.
        """
        with self.num_processed.get_lock():
            self.num_processed.value += 1
            logger.debug(f'Number processed: {self.num_processed.value}')

    def __inc_num_error(self):
        """
        Increment counter to track failed values

        :return: No return value.
        """
        with self.num_error.get_lock():
            self.num_error.value += 1
            logger.debug(f'Number of errors: {self.num_error.value}')

    def __inc_num_success(self):
        """
        Increment counter to track successful values.

        :return: No return value.
        """
        with self.num_success.get_lock():
            self.num_success.value += 1
            logger.debug(f'Number of success: {self.num_success.value}')

    def __worker(self):
        """
        Worker process to run function with values plucked from the
        process queue.

        :return: No return value.
        """
        con = sql.connect(self.db_name, check_same_thread=False)
        cur_proc = mp.current_process().name
        for x in iter(self.process_queue.get, None):

            if x is None:
                break

            status = False
            result = None

            try:
                y = self.f(x[1], *self.args, **self.kwargs)
                if isinstance(y, tuple):
                    status = y[0]
                    if len(y) > 1:
                        result = y[1]
                else:
                    status = y
            except Exception as e:
                logger.error(f'Exception raised evaluating function f: {e}, type: {type(e)}')

            x[2] += 1

            if status:
                self.__move_processing_to_success(con, *x, result=result)
            elif x[2] < self.max_tries:
                self.__add_to_processing(con, *x)
            else:
                self.__move_processing_to_failed(con, *x)

            logger.debug(f'{cur_proc} received ID: {x[0]}, value={x[1]}, tries: {x[2]}')

        logger.debug(f'{cur_proc} all done!')
        con.close()

    def __create_db(self):
        """
        Creat database tables, dropping any existing tables.

        :return: No return value.
        """
        con = sql.connect(self.db_name, check_same_thread=False)
        con.execute("DROP TABLE IF EXISTS itemid")
        con.execute("DROP TABLE IF EXISTS processing")
        con.execute("DROP TABLE IF EXISTS success")
        con.execute("DROP TABLE IF EXISTS failed")
        con.execute("""
                    CREATE TABLE itemid
                    (
                        id        INTEGER PRIMARY KEY
                    )
                    """)
        con.execute("""
            CREATE TABLE processing(
                                    id INTEGER PRIMARY KEY,
                                    value TEXT NOT NULL,
                                    num_tries INT DEFAULT 0)
        """)
        con.execute("""
            CREATE TABLE failed(
                                id INTEGER PRIMARY KEY,
                                value TEXT NOT NULL,
                                num_tries INT)
        """)
        con.execute("""
            CREATE TABLE success(
                                id INTEGER PRIMARY KEY,
                                value TEXT NOT NULL,
                                num_tries INT,
                                result TEXT)
        """)
        con.commit()
        con.close()

    def __load_from_db(self):
        """
        Load queue from database.

        :return: No return value.
        """
        con = sql.connect(self.db_name, check_same_thread=False)
        for row in con.execute("SELECT * FROM processing ORDER BY num_tries"):
            self.process_queue.put(list(row))
            self.old_values.append(row[1])
        for row in con.execute("SELECT * FROM failed ORDER BY id"):
            if self.resume and self.retry:
                x = list(row)
                x[2] = 0
                self.process_queue.put(x)
                with self.lock:
                    con.execute("BEGIN TRANSACTION")
                    con.execute("REPLACE INTO processing VALUES (?, ?, ?)", (x[0], x[1], x[2]))
                    con.execute("DELETE FROM failed WHERE id = ?", (x[0],))
                    con.commit()
            else:
                self.fail_queue.put(list(row))
                self.__inc_num_processed()
                self.__inc_num_error()
            self.old_values.append(row[1])
        for row in con.execute("SELECT * FROM success ORDER BY id"):
            self.success_queue.put(list(row))
            self.__inc_num_processed()
            self.__inc_num_success()
            self.old_values.append(row[1])
        con.close()

    def __add_to_processing(self, con, id, value, num_tries=0):
        """
        Add item for processing.

        The process queue and the processing database table are updated.

        :param con: Database connection.
        :param id: Item ID, or None if it is to be autogenerated.
        :param value: Item value.
        :param num_tries: Number of previous attempts to run function.
        :return: No return value.
        """
        with self.lock:
            cur = con.cursor()
            if id is None:
                row = cur.execute("INSERT INTO itemid VALUES(NULL) RETURNING id").fetchone()
                if row is not None:
                    id = row[0]
                    cur.execute("INSERT INTO processing(id, value, num_tries) VALUES (?, ?, ?)",
                                      (id, value, num_tries))
                else:
                    logger.error(f'Unable to add item with value {value} to database.')
            else:
                cur.execute("REPLACE INTO processing VALUES (?, ?, ?)", (id, value, num_tries))
            con.commit()
            self.process_queue.put([id, value, num_tries])

    def __move_processing_to_failed(self, con, id, value, num_tries):
        """
        Move item from processing to failed.

        This function will move the item from processing to failed
        queues as well as tables.

        :param con: Database connection.
        :param id: Item ID.
        :param value: Item value.
        :param num_tries: Number of attempts to run function with this
            value.
        :return: No return value.
        """
        self.fail_queue.put([id, value,  num_tries])
        with self.lock:
            con.execute("BEGIN TRANSACTION")
            con.execute("REPLACE INTO failed VALUES (?, ?, ?)", (id, value, num_tries))
            con.execute("DELETE FROM processing WHERE id = ?", (id,))
            con.commit()
        self.__inc_num_processed()
        self.__inc_num_error()


    def __move_processing_to_success(self, con, id, value, num_tries, result=None):
        """
        Move item from processing to success.

        This function will move the item from processing to success
        queues as well as tables.

        :param con: Database connection.
        :param id: Item ID.
        :param value: Item value.
        :param num_tries: Number of attempts to run function with this
            value.
        :param result: Optional dict result to add to the queue. Can be
            None.
        :return: No return value.
        """
        self.success_queue.put([id, value, num_tries, result])
        with self.lock:
            con.execute("BEGIN TRANSACTION")
            con.execute("REPLACE INTO success VALUES (?, ?, ?, ?)", (id, value, num_tries, json.dumps(result)))
            con.execute("DELETE FROM processing WHERE id = ?", (id,))
            con.commit()
        self.__inc_num_processed()
        self.__inc_num_success()

    @staticmethod
    def dict_factory(cursor, row):
        """
        Format rows as a dictionary for SQLite output.

        If the column result is present, it is assumed to be a json
        dump and loaded back into a dictionary.

        :param cursor: Database cursor.
        :param row: Database row tuple.
        :return: Formatted row dictionary.
        """
        fields = [column[0] for column in cursor.description]
        row_dict = dict(zip(fields, row))
        for key, value in row_dict.items():
            if key == 'result':
                row_dict[key] = json.loads(value)
        return row_dict

    def write_to_files(self, con):
        """
        Write success, failed, and processing tables to a file.

        :param con: Database connection.
        :return: No return value.
        """
        con.row_factory = self.dict_factory

        # Write to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            failed_res = con.execute("SELECT * FROM failed").fetchall()
            success_res = con.execute("SELECT * FROM success").fetchall()
            processing_res = con.execute("SELECT * FROM processing").fetchall()
            res_dict = {'success': success_res, 'failed': failed_res, 'processing': processing_res}
            json.dump(res_dict, f, ensure_ascii=False, indent=4)

        # Reset row_factory to default
        con.row_factory = sql.Row
