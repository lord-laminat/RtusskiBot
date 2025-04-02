-- +goose Up
-- +goose StatementBegin
CREATE TABLE users(
  chat_id BIGINT NOT NULL,
  username TEXT,
  full_user_name TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  last_modified TIMESTAMP DEFAULT now(),
  PRIMARY KEY(chat_id)
);
CREATE TABLE subscribers(
  user_id BIGINT REFERENCES users(chat_id),
  channel_id BIGINT NOT NULL,
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
