CREATE TABLE _prop (
    key TEXT NOT NULL PRIMARY KEY
    ,value ANY
) STRICT;

INSERT INTO _prop (key, value) VALUES ('initialized.at', unixepoch());
INSERT INTO _prop (key, value) VALUES ('initialized.sqlite_version', (SELECT sqlite_version()));
