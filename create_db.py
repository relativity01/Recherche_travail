import sqlite3
import os
from datetime import datetime

def create_db():
    print("Database not found. Creating new database...")
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    db_path = os.path.join(script_dir, 'jobs.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS etape (
        id_etape INTEGER PRIMARY KEY AUTOINCREMENT,
        etape TEXT NOT NULL UNIQUE
    )
    ''')
    stages = [
        'Demande',
        'Entretien 1',
        'Entretien 2',
        'Entretien 3',
        'Entretien Final'
    ]
    for stage in stages:
        cursor.execute('INSERT OR IGNORE INTO etape (etape) VALUES (?)', (stage,))


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statut (
        id_statut INTEGER PRIMARY KEY AUTOINCREMENT,
        statut TEXT NOT NULL UNIQUE
    )
    ''')
    statuts = [
    'non_postulee', #Pas de postulation
    'a_postuler',
    'postulee',
    'refusee', #refusée directement après postulation
    'reponse_positive', #réponse positive pour un premier entretien mais pas de validation
    'reponse_négative', #après une réponse positive pour un premier entretien, une réponse négative pour la suite du processus
    ]
    for statut in statuts:
        cursor.execute('INSERT OR IGNORE INTO statut (statut) VALUES (?)', (statut,))


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS raison_non_candidature (
        id_raison INTEGER PRIMARY KEY AUTOINCREMENT,
        raison TEXT NOT NULL UNIQUE
    )
    ''')
    raisons = [
        'redondant',
        'salaire insuffisant',
        'trop loin',
        'pas intéressant',
        'pas les compétences'
    ]
    for raison in raisons:
        cursor.execute(
            'INSERT OR IGNORE INTO raison_non_candidature (raison) VALUES (?)',
            (raison,)
        )



    # Create the job table with foreign key reference
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT,
        entreprise TEXT,
        localisation TEXT, 
        url TEXT UNIQUE NOT NULL,
        url_id TEXT UNIQUE NOT NULL,
        id_etape INTEGER DEFAULT NULL,
        id_statut INTEGER NOT NULL DEFAULT 1,
        id_raison INTEGER DEFAULT NULL,
        premiere_candidature DATE,
        derniere_reponse DATE,
        prochaine_reponse DATE,
        description TEXT,
        commentaire TEXT,
        site_source TEXT,
        FOREIGN KEY (id_etape) REFERENCES etape (id_etape),
        FOREIGN KEY (id_statut) REFERENCES statut (id_statut),
        FOREIGN KEY (id_raison) REFERENCES raison (id_raison)
    )
    ''')


    conn.commit()
    conn.close()