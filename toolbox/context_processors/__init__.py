from django.conf import settings

def metadata(request):
    """
    A context processor to add basic metadata about the site.
    """
    return {
        'site_name': getattr(settings, 'SITE_NAME', None),
        'facebook_admins': ", ".join(getattr(settings, 'FACEBOOK_ADMINS', [])),
    }
