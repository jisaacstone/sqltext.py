from sqltext import SqlText


example_select = SqlText('''
SELECT name, MAX(height)
FROM people
GROUP BY height
''')
example_update = SqlText('''
UPDATE government_work
SET success='close enough'
WHERE success IN (
    SELECT text_value
    FROM conditon
    WHERE better_than_nothing=1
)
''')
example_delete = SqlText('''
DELETE FROM the_queries
WHERE sql_statement LIKE '%ALTER%'
OR updated > datetime('now')
''')


def eq(a, b):
    assert a.split() == b.split(), '{0} != {1}'.format(a, b)
    print '.',


def test_everything():
    test_set()
    test_delete()
    test_insert()
    test_remove()
    print 'OK'


def test_set():
    eq(example_select.set_clause('HAVING', 'MAX(height) > 0'), '''
        SELECT name, MAX(height)
        FROM people
        GROUP BY height
        HAVING MAX(height) > 0
        ''')
    eq(example_update.set_clause('WHERE', 'percent_complete > 90'), '''
        UPDATE government_work
        SET success='close enough'
        WHERE percent_complete > 90
        ''')


def test_delete():
    eq(example_delete.delete_clause('WHERE'), '''
        DELETE FROM the_queries
        ''')


def test_insert():
    eq(example_select.append_to_clause('FROM',
        'INNER JOIN living_people USING first, last'), '''
        SELECT name, MAX(height)
        FROM people
        INNER JOIN living_people USING first, last
        GROUP BY height
        ''')


def test_remove():
    eq(example_delete.remove_from_clause('WHERE',
        "sql_statement LIKE '%ALTER%' OR"), '''
        DELETE FROM the_queries
        WHERE updated > datetime('now')
        ''')


if __name__ == '__main__':
    test_everything()
