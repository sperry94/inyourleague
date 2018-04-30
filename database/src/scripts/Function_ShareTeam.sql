DROP FUNCTION IF EXISTS  share_team;

CREATE FUNCTION share_team(oauthid_tosave TEXT, sharecode_tosave UUID, teamkey_tosave UUID)
RETURNS BOOLEAN AS $$
DECLARE userid_tosave TEXT;
BEGIN

  IF NOT EXISTS(
    SELECT 1 FROM team
    WHERE team.userid = oauthid_tosave
      AND team.key = teamkey_tosave
  )
  THEN
    RETURN FALSE;
  END IF;

  userid_tosave := (SELECT oauthid FROM account WHERE sharecode = sharecode_tosave);

  INSERT INTO teammembers(userid, teamkey)
    VALUES (userid_tosave, teamkey_tosave)
  ON CONFLICT DO NOTHING;

  RETURN TRUE;
END;
$$ LANGUAGE plpgsql
RETURNS NULL ON NULL INPUT;
