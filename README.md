sqltext is a miminalist SQL library, for those times when a large library such as sqlalchemy is not neccesary.

    >>> from sqltext import SqlText
    >>> delete_q = "DELETE FROM people WHERE updated_at > datetime('now')"
    >>> verify_count = SqlText(delete_query).delete_clause('DELETE').set_clause('SELECT', 'count(*)')
    >>> verify_count
     u"SELECT count(*) FROM people WHERE updated_at > datetime('now')"
    >>> total_rows_q = verify_count.delete_clause('WHERE')
    >>> total_rows_q
     u'SELECT count(*) FROM people'

sqltext assumes the clause names are in UPPER CASE. It makes ~~no~~ very few assumptions about what dialect fo sql you are using.

    >>> name_counts_q = total_rows_q.append_to_clause('SELECT', 'first_name').set_clause('GROUP BY', 'first_name')
    >>> name_counts_q
     u'SELECT count(*), first_name FROM people GROUP BY first_name'

sqltext subclasses unicode, so all common string methods work.

    >>> top_ten_sirnames = name_counts_q.replace('first_name', 'last_name').set_clause('ORDER BY', 'count(*)').set_clause('LIMIT', 10)
    >>> top_ten_sirnames
     u'SELECT count(*), last_name FROM people GROUP BY last_name ORDER BY count(*) LIMIT 10'
    >>> commoners_q = total_rows_q.set_clause('WHERE',
    ...     'last_name IN (' + top_ten_sirnames.remove_from_clause('SELECT', 'count(*)') + ')')
    >>> commoners_q
     u'SELECT count(*) FROM people WHERE last_name IN (SELECT last_name FROM people GROUP BY last_name ORDER BY count(*) LIMIT 10)'
