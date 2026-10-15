import sqlite3

from neuroscale.database.core import connect, initialize


def test_schema_and_foreign_keys(tmp_path):
    p=tmp_path/'x.sqlite'; initialize(p); con=connect(p)
    assert con.execute('PRAGMA foreign_keys').fetchone()[0] == 1
    try: con.execute("INSERT INTO participant(dataset_id,subject_code,analysis_included) VALUES (999,'x',1)")
    except sqlite3.IntegrityError: pass
    else: raise AssertionError('foreign key violation accepted')
