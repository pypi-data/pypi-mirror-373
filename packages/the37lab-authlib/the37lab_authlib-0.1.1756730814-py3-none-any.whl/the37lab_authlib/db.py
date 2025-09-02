import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from contextlib import contextmanager
from .models import UUIDGenerator, IntegerGenerator

class Database:
    def __init__(self, dsn, id_type='uuid', min_conn=1, max_conn=10):
        self.dsn = dsn
        self.id_generator = UUIDGenerator() if id_type == 'uuid' else IntegerGenerator()
        self.id_type = id_type
        self.min_conn = min_conn
        self.max_conn = max_conn
        self._pool = None
        self._init_pool()
        self._init_db()

    def _init_pool(self):
        self._pool = pool.ThreadedConnectionPool(
            self.min_conn,
            self.max_conn,
            self.dsn,
            cursor_factory=RealDictCursor
        )

    def _init_db(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Create users table with configurable ID type
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS users (
                        id {self._get_id_type()} PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        real_name VARCHAR(255) NOT NULL,
                        password_hash VARCHAR(255),
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS roles (
                        id {self._get_id_type()} PRIMARY KEY,
                        name VARCHAR(255) UNIQUE NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS user_roles (
                        user_id {self._get_id_type()} REFERENCES users(id),
                        role_id {self._get_id_type()} REFERENCES roles(id),
                        PRIMARY KEY (user_id, role_id)
                    );

                    CREATE TABLE IF NOT EXISTS api_tokens (
                        id VARCHAR(8) PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        name VARCHAR(255) NOT NULL,
                        token VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        expires_at TIMESTAMP,
                        last_used_at TIMESTAMP
                    );
                """)

    def _get_id_type(self):
        return 'UUID' if self.id_type == 'uuid' else 'SERIAL'

    @contextmanager
    def get_connection(self):
        conn = self._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    @contextmanager
    def get_cursor(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                yield cur

    def get_id_generator(self):
        return self.id_generator

    def close(self):
        if self._pool:
            self._pool.closeall() 