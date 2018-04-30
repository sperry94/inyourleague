DROP FUNCTION IF EXISTS  search_teams;

CREATE FUNCTION search_teams(keyword TEXT)
RETURNS TABLE(key UUID, name TEXT) AS $$
BEGIN
  RETURN QUERY SELECT team.key, team.name FROM team
    WHERE team.name LIKE '%' + keyword + '%';

  RETURN QUERY SELECT team.key, team.name
  FROM team
  JOIN account
  ON team.userid = account.oauthid
  WHERE account.firstname LIKE '%' + keyword + '%'
    OR account.lastname LIKE '%' + keyword + '%';
END;
$$ LANGUAGE plpgsql
RETURNS NULL ON NULL INPUT;
