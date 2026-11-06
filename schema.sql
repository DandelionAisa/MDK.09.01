PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 login TEXT NOT NULL UNIQUE COLLATE NOCASE,
 full_name TEXT NOT NULL,
 password_hash TEXT NOT NULL,
 email TEXT NOT NULL,
 phone TEXT NOT NULL,
 role TEXT NOT NULL DEFAULT 'participant' CHECK(role IN ('participant','admin'))
);
CREATE TABLE IF NOT EXISTS events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 title TEXT NOT NULL,
 event_date TEXT NOT NULL,
 place TEXT NOT NULL,
 description TEXT NOT NULL,
 category TEXT NOT NULL DEFAULT 'Конференция'
);
CREATE TABLE IF NOT EXISTS statuses (
 id INTEGER PRIMARY KEY,
 name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS requests (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER NOT NULL REFERENCES users(id),
 event_id INTEGER NOT NULL REFERENCES events(id),
 status_id INTEGER NOT NULL DEFAULT 1 REFERENCES statuses(id),
 room TEXT NOT NULL CHECK(room IN ('Большой зал','Малый зал','Онлайн')),
 payment TEXT NOT NULL CHECK(payment IN ('Карта','Перевод по счёту','Бесплатно')),
 seats INTEGER NOT NULL CHECK(seats BETWEEN 1 AND 50),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS reviews (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 request_id INTEGER NOT NULL UNIQUE REFERENCES requests(id) ON DELETE CASCADE,
 body TEXT NOT NULL,
 rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_requests_user ON requests(user_id);
CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status_id);
