-- +goose Up
-- +goose StatementBegin
CREATE TABLE users(
  chat_id INTEGER NOT NULL,
  username TEXT,
  full_user_name TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  last_modified TIMESTAMP DEFAULT now(),
  PRIMARY KEY(chat_id)
);
CREATE TABLE subscribers(
  user_id INTEGER REFERENCES users(chat_id),
  channel_id INTEGER NOT NULL,
  thread_id INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  last_modified TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY(user_id)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE subscribers;
DROP TABLE users;
-- +goose StatementEnd
