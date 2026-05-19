import os
import sqlite3
from datetime import datetime
from create_db import create_db
from asyncio.windows_events import NULL


class DatabaseManager:
    def __init__(self):
        self.setup_database()

    def setup_database(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, 'jobs.db')  # always absolute
        
        if os.path.exists(db_path):
            print("Database found. Connecting...")
        else:
            print("Database not found. Creating new database...")
            create_db()
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def save_job(self, title, url, url_id, company, location, description, id_statut, site_source):
        try:
            self.cursor.execute("""
                INSERT OR IGNORE INTO job (titre, url, url_id, entreprise, localisation, description, id_statut, premiere_candidature, site_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, url, url_id, company, location, description, id_statut, datetime.now().strftime("%d-%m-%Y") if id_statut in [1, 3] else NULL, site_source))
            self.conn.commit()
            print(f"✓ Saved to DB: {url}")
        except sqlite3.Error as e:
            print(f"✗ DB error: {e}")

    def close(self):
        self.conn.close()
