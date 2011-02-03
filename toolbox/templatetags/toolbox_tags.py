"""
A collection of miscellaneous string filters that we use to dress up our data.
"""
# Templatetag helpers
import re
from django import template
from django.utils.safestring import mark_safe, SafeData
from django.template.defaultfilters import stringfilter

# Open up the templatetag registry
register = template.Library()

#
# Replacement filters
#

def truthjs(bool):
    """
    Replaces True with true and False with false, so I can print JavaScript.
    """
    if bool == True:
        return 'true'
    elif bool == False:
        return 'false'
    elif bool == None:
        return 'null'
    else:
        return ''
truthjs.is_safe = True
register.filter(truthjs)


def trim_p(html, count=2):
    """
    Trims a html block to the requested number of paragraphs
    """
    grafs = [i.end() for i in re.finditer("</p>", html)]
    if len(grafs) < count:
        return html
    else:
        end = grafs[count-1]
        return html[:end]
trim_p = stringfilter(trim_p)
register.filter(trim_p)
