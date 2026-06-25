import json
from ..models.database import get_connection


class Optimization:
    @staticmethod
    def save(event_id, best_fitness, generations, processing_time, result_data):
        conn = get_connection()
        conn.execute('''
            INSERT INTO optimizations (event_id, best_fitness, generations, processing_time, result_json)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(event_id) DO UPDATE SET
                best_fitness = excluded.best_fitness,
                generations = excluded.generations,
                processing_time = excluded.processing_time,
                result_json = excluded.result_json,
                created_at = CURRENT_TIMESTAMP
        ''', (event_id, best_fitness, generations, processing_time, json.dumps(result_data)))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_event(event_id):
        conn = get_connection()
        row = conn.execute(
            'SELECT * FROM optimizations WHERE event_id = ?', (event_id,)
        ).fetchone()
        conn.close()
        if row:
            return {
                'best_fitness': row['best_fitness'],
                'generations': row['generations'],
                'processing_time': row['processing_time'],
                'result': json.loads(row['result_json']),
                'created_at': row['created_at']
            }
        return None
