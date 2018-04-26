DROP FUNCTION IF EXISTS  get_eventlist;

CREATE FUNCTION get_eventlist(userid_toget TEXT, teamkey_toget UUID)
RETURNS TABLE() AS $$
BEGIN

  IF NOT EXISTS(
    SELECT 1 FROM team
    WHERE team.userid = userid_toget
      AND team.key = teamkey_toget
  )
  THEN
    RETURN NULL
  ENDIF

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
$$ LANGUAGE plpgsql
RETURNS NULL ON NULL INPUT;
