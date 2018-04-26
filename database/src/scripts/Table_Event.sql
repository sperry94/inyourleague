CREATE TABLE IF NOT EXISTS event(
  key UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	teamkey UUID NOT NULL REFERENCES team(key) ON DELETE CASCADE,
  name TEXT NOT NULL,
  fullDay BOOLEAN NOT NULL DEFAULT FALSE,
	startTime TIMESTAMP NULL,
	endTime TIMESTAMP NULL
);