# StrengthTrack Database Schema

This document describes the database structure used by the StrengthTrack application.
The database uses SQLite and is stored in:

```
data/strengthtrack.db
```

The purpose of the database is to store user information, body weight tracking, fitness test results, and workout exercises.

---

# Table: users

Stores basic user profile information.

| Column       | Type    | Required | Description                                     |
| ------------ | ------- | -------- | ----------------------------------------------- |
| id           | INTEGER | Yes      | Primary key. Unique user identifier.            |
| name         | TEXT    | Yes      | User name.                                      |
| height_cm    | REAL    | Yes      | User height in centimeters.                     |
| start_weight | REAL    | Yes      | Weight at the start of tracking.                |
| goal         | TEXT    | No       | User goal. Example: lose weight, gain strength. |

Example row:

| id | name  | height_cm | start_weight | goal       |
| -- | ----- | --------- | ------------ | ---------- |
| 1  | Juuso | 178       | 92.5         | Lose 10 kg |

---

# Table: weight_entries

@@ -77,43 +77,76 @@ Example row:

| id | user_id | entry_date | test_name | result_value | unit | note      |
| -- | ------- | ---------- | --------- | ------------ | ---- | --------- |
| 1  | 1       | 2026-03-17 | Pushups   | 32           | reps | good form |

Relationship:

```
fitness_tests.user_id → users.id
```

Each user can have many fitness tests.

---

# Relationships Overview

```
users
  │
  ├── weight_entries
  │       user_id → users.id
  │
  └── fitness_tests
          user_id → users.id

workout_programs
  │
  └── workout_exercises
          program_id → workout_programs.id
```

One user can have multiple weight entries and multiple fitness test records.
One workout program can have multiple workout exercises.

---

# Table: workout_exercises

Stores exercises assigned to workout programs.

| Column        | Type    | Required | Description                                       |
| ------------- | ------- | -------- | ------------------------------------------------- |
| id            | INTEGER | Yes      | Primary key.                                      |
| program_id    | INTEGER | Yes      | Reference to workout_programs.id.                 |
| day_name      | TEXT    | Yes      | Day label inside the program. Example: Monday.    |
| exercise_name | TEXT    | Yes      | Name of the exercise.                             |
| sets          | INTEGER | No       | Number of sets.                                   |
| reps          | INTEGER | No       | Number of repetitions.                            |
| extra_weight  | REAL    | No       | Additional load in kilograms or chosen unit.      |
| note          | TEXT    | No       | Optional note for execution or progression detail.|

Example row:

| id | program_id | day_name | exercise_name | sets | reps | extra_weight | note           |
| -- | ---------- | -------- | ------------- | ---- | ---- | ------------ | -------------- |
| 1  | 1          | Monday   | Bench Press   | 4    | 8    | 60.0         | controlled tempo |

Relationship:

```
workout_exercises.program_id → workout_programs.id
```

---

# Future Tables

These tables will be added later during development:

| Table            | Purpose                           |
| ---------------- | --------------------------------- |
| workout_sessions | Stores completed workout sessions |
| progress_metrics | Calculated metrics for graphs     |

---
