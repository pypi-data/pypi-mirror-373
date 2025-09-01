'''
Useful filter factories for expressing font preferences for `FontFinder.family_prefs` and
`FontFinder.family_font_prefs`.
'''

def attr_in(attr_name, collection):
    '''A filter factory. Returns a filter function that takes a single argument `obj` and returns True
    if `obj.attr_name` is in `collection`, else False.
    '''
    def filter(obj):
        return getattr(obj, attr_name) in collection
    return filter

def attr_not_in(attr_name, collection):
    '''A filter factory. Returns a filter function that takes a single argument `obj` and returns True
    if `obj.attr_name` is not in `collection`, else False.
    '''
    def filter(obj):
        return getattr(obj, attr_name) not in collection
    return filter

def attr_contains(attr_name, collection):
    '''A filter factory. Returns a filter function that takes a single argument `obj` and returns True
    if any of the items in `collection` are in `obj.attr_name`. Otherwise returns False.
    '''
    def filter(obj):
        return any(map(lambda item: item in getattr(obj, attr_name), collection))
    return filter

def attr_not_contains(attr_name, collection):
    '''A filter factory. Returns a filter function that takes a single argument `obj` and returns True
    if none of the items in `collection` are in `obj.attr_name`. Otherwise returns False.
    '''
    def filter(obj):
        return not any(map(lambda item: item in getattr(obj, attr_name), collection))
    return filter

def attr_contains_str(attr_name, str_collection):
    '''A filter factory. Returns a filter function that takes a single argument `obj` and returns True
    if any of the strings in `str_collection` are in the string conversion of `obj.attr_name`, when all strings are
    casefolded. Otherwise returns False.
    '''
    def filter(obj):
        return any(map(lambda s: s.casefold() in str(getattr(obj, attr_name)).casefold(), str_collection))
    return filter

def attr_not_contains_str(attr_name, str_collection):
    '''A filter factory. Returns a filter function that takes a single argument `obj` and returns True
    if none of the strings in `str_collection` are in the string conversion of `obj.attr_name`, when all strings are
    casefolded. Otherwise returns False.
    '''
    def filter(obj):
        return not any(map(lambda s: s.casefold() in str(getattr(obj, attr_name).casefold()), str_collection))
    return filter
