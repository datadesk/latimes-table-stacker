"""
Utilities to format values into more meaningful strings.
Inspired by James Bennett's template_utils and Django's
template filters.
"""
import re

def _saferound(value, decimal_places):
    """
    Rounds a float value off to the desired precision
    """
    try:
        f = float(value)
    except ValueError:
        return ''
    format = '%%.%df' % decimal_places
    return format % f

AP_STATES_NORMALIZATION = {
    'ak': 'Alaska',
    'al': 'Ala.',
    'ala': 'Ala.',
    'alabama': 'Ala.',
    'alaska': 'Alaska',
    'american samao': 'A.S.',
    'american samoa': 'A.S.',
    'ar': 'Ark.',
    'ariz': 'Ariz.',
    'arizona': 'Ariz.',
    'ark': 'Ark.',
    'arkansas': 'Ark.',
    'as': 'A.S.',
    'az': 'Ariz.',
    'ca': 'Calif.',
    'calf': 'Calif.',
    'calif': 'Calif.',
    'california': 'Calif.',
    'co': 'Colo.',
    'colo': 'Colo.',
    'colorado': 'Colo.',
    'conn': 'Conn.',
    'connecticut': 'Conn.',
    'ct': 'Conn.',
    'dc': 'D.C.',
    'de': 'Del.',
    'del': 'Del.',
    'delaware': 'Del.',
    'deleware': 'Del.',
    'district of columbia': 'D.C.',
    'fl': 'Fla.',
    'fla': 'Fla.',
    'florida': 'Fla.',
    'ga': 'Ga.',
    'georgia': 'Ga.',
    'gu': 'Guam',
    'guam': 'Guam',
    'hawaii': 'Hawaii',
    'hi': 'Hawaii',
    'ia': 'Iowa',
    'id': 'Idaho',
    'idaho': 'Idaho',
    'il': 'Ill.',
    'ill': 'Ill.',
    'illinois': 'Ill.',
    'in': 'Ind.',
    'ind': 'Ind.',
    'indiana': 'Ind.',
    'iowa': 'Iowa',
    'kan': 'Kan.',
    'kans': 'Kan.',
    'kansas': 'Kan.',
    'kentucky': 'Ky.',
    'ks': 'Kan.',
    'ky': 'Ky.',
    'la': 'La.',
    'louisiana': 'La.',
    'ma': 'Mass.',
    'maine': 'Maine',
    'marianas islands': 'M.P.',
    'marianas islands of the pacific': 'M.P.',
    'marinas islands of the pacific': 'M.P.',
    'maryland': 'Md.',
    'mass': 'Mass.',
    'massachusetts': 'Mass.',
    'massachussetts': 'Mass.',
    'md': 'Md.',
    'me': 'Maine',
    'mi': 'Mich.',
    'mich': 'Mich.',
    'michigan': 'Mich.',
    'minn': 'Minn.',
    'minnesota': 'Minn.',
    'miss': 'Miss.',
    'mississippi': 'Miss.',
    'missouri': 'Mo.',
    'mn': 'Minn.',
    'mo': 'Mo.',
    'mont': 'Mont.',
    'montana': 'Mont.',
    'mp': 'M.P.',
    'ms': 'Miss.',
    'mt': 'Mont.',
    'n d': 'N.D.',
    'n dak': 'N.D.',
    'n h': 'N.H.',
    'n j': 'N.J.',
    'n m': 'N.M.',
    'n mex': 'N.M.',
    'nc': 'N.C.',
    'nd': 'N.D.',
    'ne': 'Neb.',
    'neb': 'Neb.',
    'nebr': 'Neb.',
    'nebraska': 'Neb.',
    'nev': 'Nev.',
    'nevada': 'Nev.',
    'new hampshire': 'N.H.',
    'new jersey': 'N.J.',
    'new mexico': 'N.M.',
    'new york': 'N.Y.',
    'nh': 'N.H.',
    'nj': 'N.J.',
    'nm': 'N.M.',
    'nmex': 'N.M.',
    'north carolina': 'N.C.',
    'north dakota': 'N.D.',
    'northern mariana islands': 'M.P.',
    'nv': 'Nev.',
    'ny': 'N.Y.',
    'oh': 'Ohio',
    'ohio': 'Ohio',
    'ok': 'Okla.',
    'okla': 'Okla.',
    'oklahoma': 'Okla.',
    'or': 'Ore.',
    'ore': 'Ore.',
    'oreg': 'Ore.',
    'oregon': 'Ore.',
    'pa': 'Pa.',
    'penn': 'Pa.',
    'pennsylvania': 'Pa.',
    'pr': 'P.R.',
    'puerto rico': 'P.R.',
    'rhode island': 'R.I.',
    'ri': 'R.I.',
    's dak': 'S.D.',
    'sc': 'S.C.',
    'sd': 'S.D.',
    'sdak': 'S.D.',
    'south carolina': 'S.C.',
    'south dakota': 'S.D.',
    'tenn': 'Tenn.',
    'tennessee': 'Tenn.',
    'territory of hawaii': 'Hawaii',
    'tex': 'Texas',
    'texas': 'Texas',
    'tn': 'Ten..',
    'tx': 'Texas',
    'us virgin islands': 'V.I.',
    'usvi': 'V.I.',
    'ut': 'Utah',
    'utah': 'Utah',
    'va': 'Va.',
    'vermont': 'Vt.',
    'vi': 'V.I.',
    'viginia': 'Va.',
    'virgin islands': 'V.I.',
    'virgina': 'Va.',
    'virginia': 'Va.',
    'vt': 'Vt.',
    'w va': 'W.Va.',
    'wa': 'Wash.',
    'wash': 'Wash.',
    'washington': 'Wash.',
    'west virginia': 'W.Va.',
    'wi': 'Wis.',
    'wis': 'Wis.',
    'wisc': 'Wis.',
    'wisconsin': 'Wis.',
    'wv': 'W.Va.',
    'wva': 'W.Va.',
    'wy': 'Wyo.',
    'wyo': 'Wyo.',
    'wyoming': 'Wyo.',
}


def ap_state(value):
    """
    Converts a state's name or postal abbreviation to .A.P. style.
    
    Example usage:
    
        >> ap_state("California")
        'Calif.'
    
    """
    try:
        return AP_STATES_NORMALIZATION[value.lower()]
    except KeyError:
        return value


def bubble(value, yes_icon='/media/img/bubble_yes.png',
    no_icon="/media/img/bubble_no.png", empty="&mdash;"):
    """
    Returns one of two "Consumer Reports" style bubbles that indicate:
    
        - Yes (Filled bubble)
        - No (Empty bubble)
    
    The first letter of each type is what should be provided, i.e. Y, N.
    """
    img = "<img alt='%(name)s' title='%(name)s' class='bubble' src='%(icon)s'>"
    if value == 'Y':
        return img % dict(name='Yes', icon=yes_icon)
    elif value == 'N':
        return img % dict(name='No', icon=no_icon)
    else:
        return empty


def checkbox(value,
    yes_icon='<img class="vote" src="/media/img/checkbox_yes.png">',
    no_icon='<img class="vote" src="/media/img/checkbox_no.png">',
    ):
    """
    Returns one of three icons:
    
        - Yes (checked box)
        - No (empty box)
    
    The first letter of each type is what should be provided, i.e. Y, N, anything else.
    """
    if value.lower() == 'y':
        return yes_icon
    elif value.lower() == 'n':
        return no_icon
    else:
        return ''


def dollar_signs(value):
    """
    Converts an integer into the corresponding number of dollar sign symbols.
    
    Meant to emulate the illustration of price range on Yelp.
    """
    try:
        count = int(value)
    except ValueError:
        return 'N/A'
    string = ''
    for i in range(0, count):
        string += '$'
    return string


def dollars(value, decimal_places=2):
    """
    Converts a number in a dollar figure, with commas after ever three digits.
    """
    if not value:
        value = 0
    value = _saferound(value, decimal_places)
    if not value:
        return 'N/A'
    return u'$%s'% intcomma(value)


def intcomma(value):
    """
    Borrowed from django.contrib.humanize
    
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    orig = str(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', orig)
    if orig == new:
        return new
    else:
        return intcomma(new)


def link(title, url):
    return u'<a target="_blank" href="%(url)s" title="%(title)s">%(title)s</a>' % {'url': url, 'title': title}


def percentage(value, decimal_places=1, multiply=True):
    """
    Converts a floating point value into a percentage value.
    
    Number of decimal places set by the `decimal_places` kwarg. Default is one.
    
    By default the number is multiplied by 100. You can prevent it from doing
    that by setting the `multiply` keyword argument to False.
    """
    value = float(value)
    if multiply:
        value = value * 100
    return _saferound(value, decimal_places) + '%'


def percent_change(value, decimal_places=1, multiply=True):
    """
    Converts a floating point value into a percentage change value.
    
    Number of decimal places set by the `precision` kwarg. Default is one.
    
    Non-floats are assumed to be zero division errors and are presented as
    'N/A' in the output.
    
    By default the number is multiplied by 100. You can prevent it from doing
    that by setting the `multiply` keyword argument to False.
    """
    try:
        f = float(value)
        if multiply:
            f = f * 100
    except ValueError:
       return  'N/A'
    s = _saferound(f, decimal_places)
    if f > 0:
        return '+' + s + '%'
    else:
        return s + '%'


def ratio(value, precision=0):
    """
    Converts a floating point value a X:1 ratio.
    
    Number of decimal places set by the `precision` kwarg. Default is one.
    """
    try:
        f = float(value)
    except ValueError:
        return 'N/A'
    return _saferound(f, decimal_places) + ':1'


def title(value):
    """
    Converts a string into titlecase.
    
    Lifted from Django.
    """
    value = value.lower()
    t = re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), value.title())
    return re.sub("\d([A-Z])", lambda m: m.group(0).lower(), t)


def tribubble(value, yes_icon='/media/img/tribubble_yes.png',
    partly_icon='/media/img/tribubble_partly.png',
    no_icon="/media/img/tribubble_no.png", empty="&mdash;"):
    """
    Returns one of three "Consumer Reports" style bubbles that indicate:
    
        - Yes (Filled bubble)
        - Partly (Half-filled bubble)
        - No (Empty bubble)
    
    The first letter of each type is what should be provided, i.e. Y, P, N.
    """
    img = "<img class='bubble' src='%(icon)s'>"
    if value.lower() == 'y':
        return img % dict(name='Yes', icon=yes_icon)
    elif value.lower() == 'p':
        return img % dict(name='Partly', icon=partly_icon)
    elif value.lower() == 'n':
        return img % dict(name='No', icon=no_icon)
    else:
        return empty


DEFAULT_FORMATTERS = {
    'ap_state': ap_state,
    'bubble': bubble,
    'checkbox': checkbox,
    'dollar_signs': dollar_signs,
    'dollars': dollars,
    'link': link,
    'intcomma': intcomma,
    'percentage': percentage,
    'percent_change': percent_change,
    'ratio': ratio,
    'title': title,
    'tribubble': tribubble,
}

class Formatter(object):
    """
    A formatter is a function (or any callable, really)
    that takes a value and returns a nicer-looking value,
    most likely a sting.
    
    Formatter stores and calls those functions, keeping
    the namespace uncluttered.
    
    Formatting functions should take a value as the first
    argument--usually the value of the Datum on which the
    function is called--followed by any number of positional
    arguments.
    
    In the context of TableFu, those arguments may refer to
    other columns in the same row.
    
    >>> formatter = Formatter()
    >>> formatter(1200, 'intcomma')
    '1,200'
    >>> formatter(1200, 'dollars')
    '$1,200'
    """
    
    def __init__(self):
        self._filters = {}
        for name, func in DEFAULT_FORMATTERS.items():
            self.register(name, func)
    
    def __call__(self, value, func, *args, **kwargs):
        if not callable(func):
            func = self._filters[func]
        return func(value, *args, **kwargs)
    
    def register(self, name=None, func=None):
        if not func and not name:
            return

        if callable(name) and not func:
            func = name
            name = func.__name__
        elif func and not name:
            name = func.__name__
        
        self._filters[name] = func
    
    def unregister(self, name=None, func=None):
        if not func and not name:
            return
        if not name:
            name = func.__name__
        
        if name not in self._filters:
            return
        
        del self._filters[name]
        

# Unless you need to subclass or keep formatting functions
# isolated, you can just import this instance.
format = Formatter()
