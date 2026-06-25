from ..models.database import get_connection


class Area:
    PRIORITIES = ['Baixa', 'Media', 'Alta', 'Critica']
    PRIORITY_WEIGHTS = {'Baixa': 1.0, 'Media': 1.5, 'Alta': 2.5, 'Critica': 4.0}

    @staticmethod
    def get_by_event(event_id):
        conn = get_connection()
        rows = conn.execute(
            'SELECT * FROM areas WHERE event_id = ? ORDER BY id',
            (event_id,)
        ).fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_by_id(area_id):
        conn = get_connection()
        row = conn.execute('SELECT * FROM areas WHERE id = ?', (area_id,)).fetchone()
        conn.close()
        return row

    @staticmethod
    def create(event_id, name, estimated_people, priority):
        conn = get_connection()
        cursor = conn.execute(
            'INSERT INTO areas (event_id, name, estimated_people, priority) VALUES (?, ?, ?, ?)',
            (event_id, name, estimated_people, priority)
        )
        conn.commit()
        area_id = cursor.lastrowid
        conn.close()
        return area_id

    @staticmethod
    def delete(area_id):
        conn = get_connection()
        conn.execute('DELETE FROM areas WHERE id = ?', (area_id,))
        conn.commit()
        conn.close()
