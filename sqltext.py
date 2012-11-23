import re


class SqlTextException(Exception):
    pass


def remove_balanced(txt, check_balance=True):
    '''Removes all quoted and parenthetical text.
    So that there are no false positive matches when searching for clauses
    '''
    r_txt = ''
    ignore = False
    balanced = {'(': ')', '"': '"', "'": "'"}
    waiting = False
    for char in txt:
        if waiting:
            if not ignore and char == balanced[waiting]:
                waiting = False
        else:
            if not ignore and char in balanced:
                waiting = char
            else:
                r_txt += char

        if char == '\\' and not ignore:
            ignore = True
        else:
            ignore = False

    if check_balance and (waiting or ')' in r_txt):
        return False
    return r_txt


def re_word(string):
    return re.compile(r'\b' + string + r'\b')


def clause_rsplit(clause, text):
    '''Similar to str.rsplit(clause, 1) except with regex
    '''
    data = re.split(re_word(clause), text)
    txt = data.pop()
    while not remove_balanced(txt):
        if not data:
            raise SqlTextException('could not parse SQL string')
        txt = ' '.join((data.pop(), clause, txt))
    return ''.join(data), txt


def flat_key(order):
    '''Any item not in the order list will be added to the end
    '''
    def keyer(tup):
        return order.index(tup[0]) if tup[0] in order else len(order)
    return keyer


def flatten(query_dict, order):
    '''Flatten the query_dict so it can easily be converted to a string again.
    '''
    return filter(None,
                  map(lambda s: s.strip(),
                      reduce(list.__add__,
                             map(list,
                                 sorted(query_dict.iteritems(),
                                        key=flat_key(order))),
                             [])))


class SqlText(unicode):
    query_orders = dict(
            ALTER=['ALTER', 'TABLE', 'RENAME', 'ADD', 'DROP'],
            CREATE=['CREATE', 'TABLE', 'INDEX', 'TRIGGER', 'VIEW',
                    'BEFORE', 'AFTER', 'INSTEAD', 'DELETE', 'INSERT', 'UPDATE',
                    'BEGIN', 'USING'],
            DELETE=['DELETE', 'FROM', 'WHERE', 'ORDER', 'LIMIT'],
            DROP=['DROP', 'TABLE', 'INDEX', 'TRIGGER', 'VIEW'],
            INSERT=['INSERT', 'INTO', 'VALUES'],
            REPLACE=['REPLACE', 'INTO', 'VALUES'],
            SELECT=['SELECT', 'FROM', 'WHERE', 'GROUP', 'HAVING', 'ORDER',
                    'LIMIT', 'OFFSET'],
            UPDATE=['UPDATE', 'SET', 'WHERE', 'ORDER', 'LIMIT'],
            )

    joinable = [
            'SELECT', 'SET', 'ORDER',
            ]

    parenthetical = [
            'VALUES', 'INSERT'
            ]

    @property
    def known_clauses(self):
        '''A tuple of all query clauses this class knows about
        '''
        return tuple(set(reduce(list.__add__,
                                self.query_orders.values(),
                                [])))

    @property
    def clauses(self):
        '''A tuple of all clauses in the string, orderd by occurence
        '''
        test = remove_balanced(unicode(self), check_balance=False)
        in_self = [c for c in self.known_clauses
                   if re.search(re_word(c), test)]
        return tuple(sorted(in_self, key=lambda c: test.index(c)))

    def to_dict(self):
        '''Convert self into a dictionary of clause: text mappings
        '''
        c_d = {}
        txt = unicode(self)
        clauses = list(self.clauses)
        while clauses:
            cls = clauses.pop()
            txt, cls_txt = clause_rsplit(cls, txt)
            while not remove_balanced(cls_txt):
                txt, cls_append = clause_rsplit(cls, txt)
                if not txt:
                    raise SqlTextException('could not convert to dict')
                cls_txt += cls_append
            c_d[cls] = self.__class__(cls_txt.strip())
        return c_d

    def from_dict(self, clause_dict, order=None):
        '''Convert the dictionary back into a string.
        if order is None order will be looked up in query_orders
        '''
        if not order:
            # sorted works for now but beware
            for query_kind, order_ in sorted(self.query_orders.items()):
                if query_kind in clause_dict:
                    order = order_
                    break
        return self.__class__(' '.join(flatten(clause_dict, order)))

    def set_clause(self, clause, text):
        '''Add or update clause to text
        '''
        text = self.__class__(text)
        c_d = self.to_dict()
        order = self.clauses if clause in c_d else None
        c_d.update({clause: text})
        return self.from_dict(c_d, order=order)

    def delete_clause(self, clause):
        c_d = self.to_dict()
        del c_d[clause]
        return self.from_dict(c_d, order=self.clauses)

    def append_to_clause(self, clause, text, implicit_join=True):
        '''Append text to clause.
        If implicit_join is true it will place the text within 
        parenthesise or add a comma if deemed appropriate.
        '''
        text = self.__class__(text)
        c_d = self.to_dict()
        if clause not in c_d:
            raise KeyError(clause)
        if implicit_join:
            if (clause in self.parenthetical
            and c_d[clause].endswith(')')
            and not text.endswith(')')):
                c_d[clause] = c_d[clause][:-1]
                text = text + ')'
            if clause in self.parenthetical + self.joinable:
                if c_d[clause].rstrip()[-1] != ',' and text[0] != ',':
                    text = ', ' + text
            elif not c_d[clause].endswith(' '):
                text = ' ' + text.lstrip()
        c_d[clause] += text
        return self.from_dict(c_d, order=self.clauses)
    
    def remove_from_clause(self, clause, text):
        text = self.__class__(' '.join(text.split()))
        c_d = self.to_dict()
        c_d[clause] = ' '.join(c_d[clause].split())
        if text not in c_d[clause]:
            raise ValueError('substring not found')
        c_d[clause] = re.sub('(,\s?\s?,)', ',',
                             re.sub('\s\s+', ' ',
                                    re.sub(',(?=[^,]*$)', '',
                                           c_d[clause].replace(text, ''))))
        return self.from_dict(c_d, order=self.clauses)

    def replace(self, *args, **kwargs):
        return self.__class__(super(SqlText, self).replace(*args, **kwargs))

    # stolen from path.py
    def __add__(self, more):
        try:
            return self.__class__(super(SqlText, self).__add__(more))
        except TypeError: # Python bug
            return NotImplemented

    def __radd__(self, other):
        if not isinstance(other, basestring):
            return NotImplemented
        return self.__class__(other.__add__(self))
