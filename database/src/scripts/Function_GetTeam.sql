CREATE OR REPLACE FUNCTION get_team(oauthid_toget TEXT, teamkey_toget UUID)
RETURNS RECORD AS $$
DECLARE team_record RECORD;
BEGIN
  team_record := (SELECT (key, userid, name) FROM team
    WHERE userid = oauthid_toget AND key = teamkey_toget);

  RETURN team_record;
END;
$$ LANGUAGE plpgsql
RETURNS NULL ON NULL INPUT;
