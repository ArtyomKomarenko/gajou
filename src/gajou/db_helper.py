import hashlib
import logging
from contextlib import contextmanager
from functools import lru_cache

import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresHelper:
    def __init__(self, host, port, user, password, dbname):
        self._cached_results = {}
        self._log = logging.getLogger(__name__)
        self._log.info(f'POSTGRES: Connect to postgresql://{host}:{port}/{dbname}\n')
        self._connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._log.info('POSTGRES: Close connection\n')
            self._connection.close()
        except Exception as e:  # noqa
            self._log.info(f'POSTGRES: No connection to close: {e}\n')
            return True

    @contextmanager
    def _commit(self, query):
        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        try:
            self._log.info(f'SQL EXECUTE {query}')
            cursor.execute(str(query))
            yield cursor
        except Exception as e:  # noqa
            raise DatabaseError(f'Exception of executing query: {e}')
        finally:
            cursor.close()

    def _select(self, sql_select_query, fetch_one=False, use_cache=False):
        if use_cache and get_hash(f'{sql_select_query} {fetch_one}') in self._cached_results.keys():
            self._log.info(f'SQL FROM CACHE {sql_select_query}')
            return self._cached_results.get(get_hash(f'{sql_select_query} {fetch_one}'))

        with self._commit(sql_select_query) as cursor:
            result = cursor.fetchone() if fetch_one else cursor.fetchall()
            self._cached_results[get_hash(f'{sql_select_query} {fetch_one}')] = result
            return result

    def _insert(self, sql_insert_query):
        with self._commit(f'{sql_insert_query} RETURNING id') as cursor:
            last_insert_id = cursor.fetchone()['id']
            self._connection.commit()
            return last_insert_id

    def _execute(self, sql_query):
        with self._commit(sql_query) as cursor:
            self._connection.commit()
            return cursor.rowcount

    @classmethod
    def _verify(cls, query, method):
        if not str(query).lower().startswith(f'{method.lower()} '):
            raise DatabaseError(f'Method should be used only for "{method.upper()}"')

    def select_one(self, sql_select_query, use_cache=False):
        self._verify(sql_select_query, 'SELECT')
        result = self._select(sql_select_query, fetch_one=True, use_cache=use_cache)
        self._log.info(f'SQL result: {dict(result)}')
        return result

    def select_all(self, sql_select_query, use_cache=False):
        self._verify(sql_select_query, 'SELECT')
        result = self._select(sql_select_query, fetch_one=False, use_cache=use_cache)
        self._log.info(f'SQL selected: {len(result)}')
        if result:
            self._log.info(f'SQL first item: {dict(result[0])}')
        return result

    def update(self, sql_update_query):
        self._verify(sql_update_query, 'UPDATE')
        result = self._execute(sql_update_query)
        self._log.info(f'SQL updated: {result}')
        return result

    def insert(self, sql_insert_query):
        self._verify(sql_insert_query, 'INSERT')
        result = self._insert(sql_insert_query)
        self._log.info(f'SQL last id: {result}')
        return result

    def delete(self, sql_delete_query):
        self._verify(sql_delete_query, 'DELETE')
        result = self._execute(sql_delete_query)
        self._log.info(f'SQL deleted: {result}')
        return result


class DatabaseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


@lru_cache
def get_hash(value):
    hash_object = hashlib.md5(str(value).encode())
    return hash_object.hexdigest()
