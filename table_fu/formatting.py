"""
Utilities to format values into more meaningful strings.
Inspired by James Bennett's template_utils and Django's
template filters.
"""
import re
from datetime import datetime
from toolbox import statestyle
from toolbox.dateutil.parser import parse as dateparse
from django.template.defaultfilters import date as dateformater
from django.template.defaultfilters import capfirst as djcapfirst


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


def ap_state(value):
    """
    Converts a state's name or postal abbreviation to .A.P. style.
    
    Example usage:
    
        >> ap_state("California")
        'Calif.'
    
    """
    try:
        return statestyle.get(value.lower()).ap
    except:
        return value


def bubble(value, yes_icon='/static/img/bubble_yes.png',
    no_icon="/static/img/bubble_no.png", empty="&mdash;"):
    """
    Returns one of two "Consumer Reports" style bubbles that indicate:
    
        - Yes (Filled bubble)
        - No (Empty bubble)
    
    The first letter of each type is what should be provided, i.e. Y, N.
    """
    img = "<img alt='%(name)s' title='%(name)s' class='bubble' src='%(icon)s'>"
    if value.lower() == 'y':
        return img % dict(name='Yes', icon=yes_icon)
    elif value.lower() == 'n':
        return img % dict(name='No', icon=no_icon)
    else:
        return empty


def capfirst(value):
    try:
        return djcapfirst(value.lower())
    except:
        return 'N/A'


def checkbox(value,
    yes_icon='/static/img/checkbox_yes.png',
    no_icon='/static/img/checkbox_no.png',
    ):
    """
    Returns one of two icons:
    
        - Yes (checked box)
        - No (empty box)
    
    Or, if a match can't be made, an empty string.
    
    The first letter of each type is what should be provided, i.e. Y, N, anything else.
    """
    img = "<img alt='%(name)s' title='%(name)s' class='vote' src='%(icon)s'>"
    if value.lower() == 'y':
        return img % dict(name='Yes', icon=yes_icon)
    elif value.lower() == 'n':
        return img % dict(name='No', icon=no_icon)
    else:
        return ''


def date_and_time(value, formatting="N j, Y, h:i a"):
    """
    Reformats a date string in a humanized format, AP style by default.
    """
    try:
        dt = dateparse(value)
    except ValueError:
        return value
    return dateformater(dt, formatting)


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
    
    The number of decimal places can be configured via the keyword argument. 
    The default is 2.
    """
    if not value:
        value = 0
    safevalue = _saferound(value, decimal_places)
    if not safevalue:
        return 'N/A'
    if float(value) < 0:
        safevalue = safevalue.replace("-", "")
        format = u'($%s)'
    else:
        format = u'$%s'
    return format % intcomma(safevalue)


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


def image(value, width='', height=''):
    """
    Accepts a URL and returns an HTML image tag ready to be displayed.
    
    Optionally, you can set the height and width with keyword arguments.
    """
    style = ""
    if width:
        style += "width:%s" % width
    if height:
        style += "height:%s" % height
    data_dict = dict(src=value, style=style)
    return '<img src="%(src)s" style="%(style)s">' % data_dict


def link(title, url):
    """
    Wrap the text in a hyperlink, if the link exists.
    """
    if not url:
        return title
    return '<a target="_blank" href="%(url)s" title="%(title)s">%(title)s</a>' % {'url': url, 'title': title}


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
    
    Number of decimal places set by the `decimal_places` kwarg. Default is one.
    
    By default the number is multiplied by 100. You can prevent it from doing
    that by setting the `multiply` keyword argument to False.
    
    Non-floats are assumed to be zero division errors and are presented as
    'N/A' in the output.
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


def short_ap_date(value, date_format=None):
    """
    Reformats a date string as in an abbreviated AP format.
    
        Example:
        
             >> short_ap_date('2010-04-03')
            'Apr. 2, 2011'
    
    If the date format cannot be automatically detected, you can specify it
    with the keyword argument.
    """
    # Split any date ranges and create a list
    value = value.replace("&ndash;", "-")
    date_parts = value.split(" - ")
    date_list = []
    for date_string in date_parts:
        try:
            if date_format:
                dt = datetime.strptime(date_string, date_format)
            else:
                dt = dateparse(date_string)
        except ValueError:
            return value
        # Check if this date is a "month-only" date
        # that needs to be specially formatted.
        if re.match('^\w{3,}\.?\s\d{4}$', date_string):
            dt = dateformater(dt, "M Y")
        # Otherwise just use the standard format
        else:
            dt = dateformater(dt, "M j, Y")
        # All months except May are abbreviated
        # and need a period added.
        if not dt.startswith("May"):
            dt = dt[:3] + "." + dt[3:]
        date_list.append(dt)
    return " &ndash; ".join(date_list)


def simple_bullet_graph(actual, target, width='95%', max=None):
    """
    Renders a simple bullet graph that compares a target line against
    an actual value.
    
    Unlike a conventional bullet graph, it does not shade the background
    into groups. Instead, it's all one solid color.
    """
    html = """
        <div class="bullet-graph-wrap" style="width:%(width)s; margin: 6px auto;">
            <div class="bullet-graph-box2" style="left:0; width:%(width)s;"></div>
            <div data="%(sort)s" class="bullet-graph-sort" style="display:none;"></div>
            <div class="bullet-graph-target" style="left: %(target)s%%;"></div>
            <div class="bullet-graph-actual" style="width: %(actual)s%%"></div>
        </div>
    """
    if not max:
        raise ValueError("Max keyword argument must be provided.")
    try:
        target_percent = (float(target) / max) * 100
        actual_percent = (float(actual) / max) * 100
    except ValueError:
        return ""
    try:
        sort = actual_percent / target_percent
    except:
        sort = 0.0
    config = dict(
        width=width,
        target=target_percent,
        actual=actual_percent,
        sort=sort,
    )
    return html % config


def title(value):
    """
    Converts a string into titlecase. Lifted from Django.
    """
    value = value.lower()
    t = re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), value.title())
    return re.sub("\d([A-Z])", lambda m: m.group(0).lower(), t)


def tribubble(value, yes_icon='/static/img/tribubble_yes.png',
    partly_icon='/static/img/tribubble_partly.png',
    no_icon="/static/img/tribubble_no.png", empty="&mdash;"):
    """
    Returns one of three "Consumer Reports" style bubbles that indicate:
    
        - Yes (Filled bubble)
        - Partly (Half-filled bubble)
        - No (Empty bubble)
    
    The first letter of each type is what should be provided, i.e. Y, P, N.
    """
    img = "<img alt='%(name)s' title='%(name)s' class='bubble' src='%(icon)s'>"
    if value.lower() == 'y':
        return img % dict(name='Yes', icon=yes_icon)
    elif value.lower() == 'p':
        return img % dict(name='Partly', icon=partly_icon)
    elif value.lower() == 'n':
        return img % dict(name='No', icon=no_icon)
    else:
        return empty


def vote(value,
    yes_vote='/static/img/thumb_up.png',
    no_vote='/static/img/thumb_down.png',
    did_not_vote="<b style='font-size:130%;'>&mdash;</b>"
    ):
    """
    Returns one of three icons:
    
        - Yes (Thumbs up)
        - Partly (Thumbs down)
        - No (Bolded em dash)
    
    The first letter of each type is what should be provided, i.e. Y, N, anything else.
    """
    img = "<img alt='%(name)s' title='%(name)s' class='vote' src='%(icon)s'>"
    if value.lower() == 'y':
        return img % dict(name='Yes', icon=yes_icon)
    elif value.lower() == 'n':
        return img % dict(name='No', icon=no_icon)
    else:
        return did_not_vote


DEFAULT_FORMATTERS = {
    'ap_state': ap_state,
    'bubble': bubble,
    'capfirst': capfirst,
    'checkbox': checkbox,
    'date_and_time': date_and_time,
    'dollar_signs': dollar_signs,
    'dollars': dollars,
    'link': link,
    'image': image,
    'intcomma': intcomma,
    'percentage': percentage,
    'percent_change': percent_change,
    'short_ap_date': short_ap_date,
    'simple_bullet_graph': simple_bullet_graph,
    'title': title,
    'tribubble': tribubble,
    'vote': vote,
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
