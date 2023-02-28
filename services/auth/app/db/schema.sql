ATTACH DATABASE 'auth.data' AS auth;

DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  role TEXT DEFAULT 'user'
);

INSERT INTO user (email, password, role) VALUES ('admin', 'admin', 'superuser')
