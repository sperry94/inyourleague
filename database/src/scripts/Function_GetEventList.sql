DROP FUNCTION IF EXISTS  get_eventlist;

CREATE FUNCTION get_eventlist(userid_toget TEXT, teamkey_toget UUID)
RETURNS TABLE(
  key UUID,
  teamkey UUID,
  name TEXT,
  fullDay BOOLEAN,
  startTime TIMESTAMP,
  endTime TIMESTAMP
) AS $$
BEGIN

  IF teamkey_toget IS NULL THEN
    RETURN QUERY
      SELECT
        event.key,
        event.teamkey,
        event.name,
        event.fullDay,
        event.startTime,
        event.endTime
      FROM event
      JOIN team
      ON event.teamkey = team.key
      WHERE team.userid = userid_toget
      ORDER BY event.startTime ASC;

      RETURN QUERY
        SELECT
          event.key,
          event.teamkey,
          event.name,
          event.fullDay,
          event.startTime,
          event.endTime
        FROM event
        JOIN teammembers
        ON event.teamkey = teammembers.teamkey
        WHERE teammembers.userid = userid_toget
        ORDER BY event.startTime ASC;

      RETURN;
  END IF;

  IF NOT EXISTS(
    SELECT 1 FROM team
    WHERE team.userid = userid_toget
      AND team.key = teamkey_toget
  ) AND NOT EXISTS (
    SELECT 1 FROM teammembers
    WHERE teammembers.userid = userid_toget
      AND teammembers.teamkey = teamkey_toget
  )
  THEN
    RETURN;
  END IF;

  RETURN QUERY
    SELECT
      event.key,
      event.teamkey,
      event.name,
      event.fullDay,
      event.startTime,
      event.endTime
    FROM event
    WHERE event.teamkey = teamkey_toget
    ORDER BY event.startTime ASC;

END;
$$ LANGUAGE plpgsql;
