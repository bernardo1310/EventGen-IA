import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'eventgen.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            total_participants INTEGER NOT NULL,
            security_count INTEGER NOT NULL,
            firefighter_count INTEGER NOT NULL,
            medical_count INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            estimated_people INTEGER NOT NULL,
            priority TEXT NOT NULL CHECK(priority IN ('Baixa', 'Media', 'Alta', 'Critica')),
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS optimizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL UNIQUE,
            best_fitness REAL NOT NULL,
            generations INTEGER NOT NULL,
            processing_time REAL NOT NULL,
            result_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
        );
    ''')

    conn.commit()
    conn.close()
