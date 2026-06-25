from ..models.database import get_connection


class Event:
    def __init__(self, id, name, total_participants, security_count,
                 firefighter_count, medical_count, created_at=None):
        self.id = id
        self.name = name
        self.total_participants = total_participants
        self.security_count = security_count
        self.firefighter_count = firefighter_count
        self.medical_count = medical_count
        self.created_at = created_at

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute('''
            SELECT e.*, COUNT(a.id) as area_count
            FROM events e
            LEFT JOIN areas a ON a.event_id = e.id
            GROUP BY e.id
            ORDER BY e.created_at DESC
        ''').fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_by_id(event_id):
        conn = get_connection()
        row = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
        conn.close()
        return row

    @staticmethod
    def create(name, total_participants, security_count, firefighter_count, medical_count):
        conn = get_connection()
        cursor = conn.execute(
            '''INSERT INTO events (name, total_participants, security_count,
               firefighter_count, medical_count)
               VALUES (?, ?, ?, ?, ?)''',
            (name, total_participants, security_count, firefighter_count, medical_count)
        )
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        return event_id

    @staticmethod
    def delete(event_id):
        conn = get_connection()
        conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
        conn.commit()
        conn.close()
