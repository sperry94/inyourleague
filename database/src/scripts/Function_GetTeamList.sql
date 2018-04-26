CREATE OR REPLACE FUNCTION get_teamlist(oauthid_toget TEXT)
RETURNS TABLE(key UUID, name TEXT) AS $$
BEGIN
  RETURN QUERY SELECT team.key, team.name FROM team
    WHERE userid = oauthid_toget ORDER BY team.name ASC;
END;
$$ LANGUAGE plpgsql
RETURNS NULL ON NULL INPUT;
