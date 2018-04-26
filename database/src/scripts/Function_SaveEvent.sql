DROP FUNCTION IF EXISTS save_event;

CREATE FUNCTION save_event(
    eventkey_tosave UUID,
    userid_tosave TEXT,
    teamkey_tosave UUID,
    name_tosave TEXT,
    fullDay_tosave BOOLEAN,
    startTime_tosave DATETIME,
    endTime_tosave DATETIME)
RETURNS UUID AS $$
DECLARE saved_eventkey UUID;
BEGIN

  IF NOT EXISTS(
    SELECT 1 FROM team
    WHERE team.userid = userid_tosave
      AND team.key = teamkey_tosave
  )
  THEN
    RETURN NULL
  ENDIF

  IF eventkey_tosave IS NULL THEN
    eventkey_tosave := uuid_generate_v4();
  END IF;

  INSERT INTO event(
      key,
      teamkey,
      name,
      fullDay,
      startTime,
      endTime)
    VALUES (
      eventkey_tosave,
      teamkey_tosave,
      name_tosave,
      fullDay_tosave
      startTime_tosave,
      endTime_tosave)
  ON CONFLICT (key) DO UPDATE
    SET
      name = name_tosave,
      fullDay = fullDay_tosave,
      startTime = startTime_tosave,
      endTime = endTime_tosave
    WHERE event.teamkey = teamkey_tosave
  RETURNING key INTO saved_eventkey;

  RETURN saved_eventkey;
END;
$$ LANGUAGE plpgsql;
