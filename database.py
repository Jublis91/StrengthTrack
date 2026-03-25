import sqlite3
from pathlib import Path

# Tietokanta tiedostoineen tallennetaan projektin data-kansioon.
# Path-oliota käytetään, jotta polkukäsittely toimii luotettavasti eri käyttöjärjestelmissä.


DB_PATH = Path("data/strengthtrack.db")


def connect():
    """Avaa SQLite-yhteyden ja varmistaa, että data-kansio on olemassa."""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    """
    Luo sovelluksen kaikki taulut, jos niitä ei vielä ole.

    Tätä kutsutaan sovelluksen käynnistyksessä, jotta UI voi olettaa
    taulujen olevan aina valmiina CRUD-toimintoja varten.
    """

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        height_cm REAL NOT NULL,
        start_weight REAL NOT NULL,
        goal TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weight_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        entry_date TEXT NOT NULL,
        weight REAL NOT NULL,
        note TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fitness_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        entry_date TEXT NOT NULL,
        test_name TEXT NOT NULL,
        result_value REAL NOT NULL,
        unit TEXT,
        note TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workout_programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workout_exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER NOT NULL,
        day_name TEXT NOT NULL,
        exercise_name TEXT NOT NULL,
        sets INTEGER,
        reps INTEGER,
        extra_weight REAL,
        note TEXT,
        FOREIGN KEY(program_id) REFERENCES workout_programs(id)
    )
    """)

    conn.commit()
    conn.close()


def save_user(name, height_cm, start_weight, goal):
    """
    Tallentaa profiilin.

    Sovellus tukee yhtä aktiivista käyttäjää: jos profiili löytyy, päivitetään se;
    muuten luodaan uusi rivi.
    """

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users ORDER BY id ASC LIMIT 1")
    existing = cursor.fetchone()

    if existing is None:
        cursor.execute("""
        INSERT INTO users (name, height_cm, start_weight, goal)
        VALUES (?, ?, ?, ?)
        """, (name, height_cm, start_weight, goal))
    else:
        cursor.execute("""
        UPDATE users
        SET name = ?, height_cm = ?, start_weight = ?, goal = ?
        WHERE id = ?
        """, (name, height_cm, start_weight, goal, existing[0]))

    conn.commit()
    conn.close()



def get_user_profile():
    """Palauttaa ensimmäisen käyttäjäprofiilin tai None, jos profiilia ei ole."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, height_cm, start_weight, goal
    FROM users
    ORDER BY id ASC
    LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    return row


def save_weight_entry(user_id, entry_date, weight, note):
    """Lisää yhden painomerkinnän annetulle käyttäjälle."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO weight_entries (user_id, entry_date, weight, note)
    VALUES (?, ?, ?, ?)
    """, (user_id, entry_date, weight, note))

    conn.commit()
    conn.close()


def get_weight_entries(user_id):
    """
    Hakee käyttäjän painomerkinnät uusimmasta vanhimpaan.

    Tätä järjestystä käytetään listausnäkymissä sekä viimeisimmän muutoksen laskennassa.
    """

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, entry_date, weight, note
    FROM weight_entries
    WHERE user_id = ?
    ORDER BY entry_date DESC, id DESC
    """,
        (user_id,),
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_weight_entries_asc(user_id):
    """Hakee painomerkinnät aikajärjestyksessä (vanhin -> uusin) graafeja varten."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT entry_date, weight
    FROM weight_entries
    WHERE user_id = ?
    ORDER BY entry_date ASC, id ASC
    """,
        (user_id,),
    )


    rows = cursor.fetchall()
    conn.close()

    return rows


def delete_weight_entry(entry_id):
    """Poistaa yhden painomerkinnän id:n perusteella."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM weight_entries
    WHERE id = ?
    """, (entry_id,))

    conn.commit()
    conn.close()

def update_weight_entry(entry_id, entry_date, weight, note):
    """Päivittää olemassa olevan painomerkinnän tiedot."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE weight_entries
    SET entry_date = ?, weight = ?, note = ?
    WHERE id = ?
    """, (entry_date, weight, note, entry_id))

    conn.commit()
    conn.close()

def save_test_entry(user_id, entry_date, test_name, result_value, unit, note):
    """Lisää uuden testituloksen (esim. punnerrukset, leuanvedot)."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO fitness_tests (user_id, entry_date, test_name, result_value, unit, note)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, entry_date, test_name, result_value, unit, note))

    conn.commit()
    conn.close()

def get_test_entries(user_id):
    """Hakee testitulokset uusimmasta vanhimpaan testilistaa varten."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, entry_date, test_name, result_value, unit, note
    FROM fitness_tests
    WHERE user_id = ?
    ORDER BY entry_date DESC, id DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_test_entries_for_name(user_id, test_name):
    """Hakee vain yhden testityypin tulokset aikajärjestyksessä kehitysgraafia varten."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT entry_date, result_value, unit
    FROM fitness_tests
    WHERE user_id = ? AND test_name = ?
    ORDER BY entry_date ASC, id ASC
    """,
        (user_id, test_name),
    )


    rows = cursor.fetchall()
    conn.close()

    return rows

def delete_test_entry(entry_id):
    """Poistaa yhden testituloksen id:n perusteella."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM fitness_tests
    WHERE id = ?
    """, (entry_id,))

    conn.commit()
    conn.close()

def update_test_entry(entry_id, entry_date, test_name, result_value, unit, note):
    """Päivittää olemassa olevan testituloksen tiedot."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE fitness_tests
    SET entry_date = ?, test_name = ?, result_value = ?, unit = ?, note = ?
    WHERE id = ?
    """, (entry_date, test_name, result_value, unit, note, entry_id))

    conn.commit()
    conn.close()

def save_workout_exercise(program_id, day_name, exercise_name, sets, reps, extra_weight, note):
    """Lisää liikkeen tiettyyn treeniohjelmaan ja päivään."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO workout_exercises (program_id, day_name, exercise_name, sets, reps, extra_weight, note)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (program_id, day_name, exercise_name, sets, reps, extra_weight, note))

    conn.commit()
    conn.close()


def get_workout_exercises(program_id):
    """Hakee ohjelman liikkeet päiväjärjestyksessä UI-listaa varten."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, day_name, exercise_name, sets, reps, extra_weight, note
    FROM workout_exercises
    WHERE program_id = ?
    ORDER BY day_name ASC, id ASC
    """, (program_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows

def save_workout_program(name):
    """Luo uuden treeniohjelman ja palauttaa syntyneen ohjelman id:n."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO workout_programs (name)
    VALUES (?)
    """, (name,))

    conn.commit()
    program_id = cursor.lastrowid
    conn.close()
    return program_id


def get_workout_programs():
    """Hakee kaikki treeniohjelmat uusimmasta vanhimpaan."""
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, created_at
    FROM workout_programs
    ORDER BY created_at DESC, id DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows