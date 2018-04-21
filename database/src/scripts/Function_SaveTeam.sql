CREATE OR REPLACE FUNCTION save_team(teamkey_tosave UUID, userid_tosave TEXT, name_tosave TEXT)
RETURNS UUID AS $$
BEGIN

  IF teamkey_tosave IS NULL THEN
    teamkey_tosave := uuid_generate_v4();
  END IF;

  INSERT INTO team(key, userid, name)
    VALUES (teamkey_tosave, userid_tosave, name_tosave)
  ON CONFLICT (key) DO UPDATE
    SET name = name_tosave;

  RETURN teamkey_tosave;
END;
$$ LANGUAGE plpgsql;
