CREATE OR REPLACE FUNCTION save_account(oauthid_tosave TEXT, accounttype_tosave INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
  INSERT INTO account(oauthid, accounttype)
    VALUES (oauthid_tosave, accounttype_tosave)
  ON CONFLICT (oauthid) DO UPDATE
    SET accounttype = accounttype_tosave;

  RETURN TRUE;
END;
$$ LANGUAGE plpgsql
RETURNS NULL ON NULL INPUT;
