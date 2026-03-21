import argparse
import random
from datetime import date, timedelta

from database import connect, init_db


TEST_NAMES = [
    ("Pushups", "reps"),
    ("Plank", "sec"),
    ("Squat", "reps"),
    ("Cooper", "m"),
]

PROGRAM_NAMES = ["Full Body Perus", "Voima 3-jakoinen", "Kestävyys + Core"]
DAY_NAMES = ["Monday", "Wednesday", "Friday"]
EXERCISES = [
    "Bench Press",
    "Back Squat",
    "Deadlift",
    "Overhead Press",
    "Pull Up",
    "Barbell Row",
    "Walking Lunge",
    "Plank",
]


def ensure_user(cursor):
    cursor.execute("SELECT id FROM users ORDER BY id ASC LIMIT 1")
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO users (name, height_cm, start_weight, goal)
        VALUES (?, ?, ?, ?)
        """,
        ("Testikäyttäjä", 178.0, 92.0, "Parantaa kuntoa"),
    )
    return cursor.lastrowid


def populate_weight_entries(cursor, user_id, count):
    base_date = date.today() - timedelta(days=count)
    weight = 92.0

    for i in range(count):
        entry_date = (base_date + timedelta(days=i)).isoformat()
        weight += random.uniform(-0.25, 0.15)

        cursor.execute(
            """
            INSERT INTO weight_entries (user_id, entry_date, weight, note)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, entry_date, round(weight, 1), f"autogen #{i + 1}"),
        )


def populate_fitness_tests(cursor, user_id, count):
    base_date = date.today() - timedelta(days=count)

    for i in range(count):
        entry_date = (base_date + timedelta(days=i)).isoformat()
        test_name, unit = random.choice(TEST_NAMES)

        if unit == "reps":
            result_value = random.randint(8, 45)
        elif unit == "sec":
            result_value = random.randint(20, 180)
        else:
            result_value = random.randint(1200, 3200)

        cursor.execute(
            """
            INSERT INTO fitness_tests (user_id, entry_date, test_name, result_value, unit, note)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, entry_date, test_name, result_value, unit, f"autogen #{i + 1}"),
        )


def populate_workout_programs(cursor, count):
    programs_to_create = max(1, min(3, count // 5 or 1))

    for i in range(programs_to_create):
        program_name = f"{PROGRAM_NAMES[i % len(PROGRAM_NAMES)]} {i + 1}"
        cursor.execute(
            "INSERT INTO workout_programs (name) VALUES (?)",
            (program_name,),
        )
        program_id = cursor.lastrowid

        for day_name in DAY_NAMES:
            for _ in range(2):
                exercise_name = random.choice(EXERCISES)
                sets = random.randint(3, 5)
                reps = random.choice([5, 6, 8, 10, 12])
                extra_weight = round(random.uniform(0, 80), 1)
                cursor.execute(
                    """
                    INSERT INTO workout_exercises (
                        program_id, day_name, exercise_name, sets, reps, extra_weight, note
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        program_id,
                        day_name,
                        exercise_name,
                        sets,
                        reps,
                        extra_weight,
                        "autogen",
                    ),
                )


def main():
    parser = argparse.ArgumentParser(
        description="Luo demodataa StrengthTrackin SQLite-tietokantaan."
    )
    parser.add_argument(
        "count",
        nargs="?",
        type=int,
        default=50,
        help="Kuinka monta paino- ja testituloriviä lisätään (oletus: 50).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Satunnaisgeneraattorin siemen (oletus: 42).",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Tyhjennä nykyinen data ennen populaatiota.",
    )
    parser.add_argument(
        "--clear-only",
        action="store_true",
        help="Tyhjennä data ja poistu ilman uuden testidatan generointia.",
    )

    args = parser.parse_args()

    if args.count <= 0:
        raise SystemExit("count pitää olla > 0")

    random.seed(args.seed)
    init_db()

    conn = connect()
    cursor = conn.cursor()

    if args.clear or args.clear_only:
        cursor.execute("DELETE FROM workout_exercises")
        cursor.execute("DELETE FROM workout_programs")
        cursor.execute("DELETE FROM fitness_tests")
        cursor.execute("DELETE FROM weight_entries")
        cursor.execute("DELETE FROM users")

    if args.clear_only:
        conn.commit()
        conn.close()
        print("Testidata tyhjennetty.")
        return

    user_id = ensure_user(cursor)
    populate_weight_entries(cursor, user_id, args.count)
    populate_fitness_tests(cursor, user_id, args.count)
    populate_workout_programs(cursor, args.count)

    conn.commit()
    conn.close()

    print(
        f"Lisättiin käyttäjälle id={user_id}: {args.count} painomerkintää, "
        f"{args.count} testimerkintää ja ohjelmadataa."
    )


if __name__ == "__main__":
    main()
