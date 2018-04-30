DROP FUNCTION IF EXISTS  save_account;

CREATE FUNCTION save_account(oauthid_tosave TEXT, accounttype_tosave INTEGER, firstname_tosave TEXT, lastname_tosave TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  INSERT INTO account(oauthid, accounttype, firstname, lastname)
    VALUES (oauthid_tosave, accounttype_tosave, firstname_tosave, lastname_tosave)
  ON CONFLICT (oauthid) DO UPDATE
    SET accounttype = accounttype_tosave,
      firstname = firstname_tosave,
      lastname = lastname_tosave;

  RETURN TRUE;
END;
$$ LANGUAGE plpgsql
RETURNS NULL ON NULL INPUT;
