DROP FUNCTION IF EXISTS get_account;

CREATE FUNCTION get_account(oauthid_toget TEXT)
RETURNS RECORD AS $$
DECLARE account_record RECORD;
BEGIN
  account_record := (SELECT (oauthid, accounttype) FROM account
    WHERE oauthid = oauthid_toget);

  RETURN account_record;
END;
$$ LANGUAGE plpgsql
RETURNS NULL ON NULL INPUT;
