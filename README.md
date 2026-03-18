# StrengthTrack Database Schema

This document describes the database structure used by the StrengthTrack application.
The database uses SQLite and is stored in:

```
data/strengthtrack.db
```

The purpose of the database is to store user information, body weight tracking, and fitness test results.

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

Stores body weight history entries.

| Column     | Type    | Required | Description                                           |
| ---------- | ------- | -------- | ----------------------------------------------------- |
| id         | INTEGER | Yes      | Primary key.                                          |
| user_id    | INTEGER | Yes      | Reference to users.id.                                |
| entry_date | TEXT    | Yes      | Date of weight entry. Format recommended: YYYY-MM-DD. |
| weight     | REAL    | Yes      | Recorded body weight.                                 |
| note       | TEXT    | No       | Optional comment about the entry.                     |

Example row:

| id | user_id | entry_date | weight | note           |
| -- | ------- | ---------- | ------ | -------------- |
| 1  | 1       | 2026-03-17 | 91.8   | Morning weight |

Relationship:

```
weight_entries.user_id → users.id
```

Each user can have many weight entries.

---

# Table: fitness_tests

Stores fitness test results such as push ups, pull ups, or plank.

| Column       | Type    | Required | Description                                         |
| ------------ | ------- | -------- | --------------------------------------------------- |
| id           | INTEGER | Yes      | Primary key.                                        |
| user_id      | INTEGER | Yes      | Reference to users.id.                              |
| entry_date   | TEXT    | Yes      | Date of the test. Format recommended: YYYY-MM-DD.   |
| test_name    | TEXT    | Yes      | Name of the test. Example: Pushups, Pullups, Plank. |
| result_value | REAL    | Yes      | Result of the test.                                 |
| unit         | TEXT    | No       | Unit of the result. Example: reps, seconds.         |
| note         | TEXT    | No       | Optional comment.                                   |

Example row:

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
```

One user can have multiple weight entries and multiple fitness test records.

---

# Future Tables

These tables will be added later during development:

| Table             | Purpose                                  |
| ----------------- | ---------------------------------------- |
| workout_programs  | Stores workout program definitions       |
| workout_exercises | Stores exercises inside workout programs |
| workout_sessions  | Stores completed workout sessions        |
| progress_metrics  | Calculated metrics for graphs            |

---
