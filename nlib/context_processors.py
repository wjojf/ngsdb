from django.conf import settings
from django.urls import resolve


# Context processors
def branding(request):
    '''
    Makes settings.BRANDING available in templates.
    '''
    try:
        branding = settings.BRANDING
    except AttributeError:
        branding = ''
    return { 'branding': '| %s' %  branding }


def crumbs(request):
    '''
    Very simplistic URL-based breadcrumbs.
    Adds breadcrumbs to the template in the following format:
    [ {'name': 'foo', 'path': '/foo'},
      {'name': 'bar', 'path': '/foo/bar'},
      {'name': 'bing', 'path': '/foo/bar/bing'} ]
    '''
    def get_crumb_path(pth_bits):
        url = '/%s/' % '/'.join(pth_bits)
        try:
            match = resolve(url)
        except:
            url = ''
        return url

    try:
        home_url = settings.CRUMBS_HOME
    except AttributeError:
        home_url = '/'

    crumb_names = request.path.strip('/').split('/')
    #crumbs = [ {'name': name.replace('_', ' '), 'path': '/' + '/'.join(crumb_names[:ind+1]) + '/'} for ind, name in enumerate(crumb_names) if name != settings.ROOT_URL.strip('/') ]
    crumbs = [ {'name': name.replace('_', ' '), 'path': get_crumb_path(crumb_names[:ind+1]) } for ind, name in enumerate(crumb_names) if name != settings.ROOT_URL.strip('/') ]
    #if not request.path.startswith(home_url):
    #       home = {'name': 'Home', 'path': home_url, }
    #       crumbs.insert(0, home)

    crumbs.insert(0, {'name': 'Home', 'path': home_url})
    return { 'crumbs': crumbs }

