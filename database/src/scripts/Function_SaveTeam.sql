DROP FUNCTION IF EXISTS save_team;

CREATE FUNCTION save_team(teamkey_tosave UUID, userid_tosave TEXT, name_tosave TEXT)
RETURNS UUID AS $$
DECLARE saved_teamkey UUID;
BEGIN

  IF teamkey_tosave IS NULL THEN
    teamkey_tosave := uuid_generate_v4();
  END IF;

  INSERT INTO team(key, userid, name)
    VALUES (teamkey_tosave, userid_tosave, name_tosave)
  ON CONFLICT (key) DO UPDATE
    SET name = name_tosave
    WHERE team.userid = userid_tosave
  RETURNING key INTO saved_teamkey;

  RETURN saved_teamkey;
END;
$$ LANGUAGE plpgsql;
