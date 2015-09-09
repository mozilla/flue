import random
import string
from cgi import escape

from factory.constants import (AUTHORS, CARRIERS, MESSAGES, PROMO_IMAGES,
                               SPECIAL_APP_SLUGS, REGIONS, SAMPLE_BG,
                               SCREENSHOT_MAP, SPECIAL_SLUGS_TO_IDS,
                               URLS, USER_NAMES)
from factory.utils import rand_bool, rand_text, rand_datetime, text


counter = 0


def _app_preview():
    """Generate app preview object."""
    url = ('https://marketplace.cdn.mozilla.net/'
           'img/uploads/previews/%%s/%d/%d.png' %
           random.choice(SCREENSHOT_MAP))
    return {
        'caption': rand_text(n=5),
        'filetype': 'image/png',
        'thumbnail_url': url % 'thumbs',
        'image_url': url % 'full',
    }


def carrier(**kw):
    slug = kw.get('slug')
    if not slug:
        # No slug ? Pick a random carrier from the dict.
        slug, name = random.choice(CARRIERS.items())
    else:
        # A slug was given ? Pick the corresponding carrier name or just make
        # one up.
        name = CARRIERS.get(slug, 'Seavan Sellular')
    return {
        'id': kw.get('id', 1),
        'name': name,
        'slug': slug,
    }


def _category(slug, name):
    """Creates a category object."""
    return {
        'name': text(name),
        'slug': slug,
    }


def region(**kw):
    slug = kw.get('slug')
    if not slug:
        # No slug ? Pick a random region from the dict.
        slug, name = random.choice(REGIONS.items())
    else:
        # A slug was given ? Pick the corresponding region name or just make
        # one up.
        name = REGIONS.get(slug, 'Cvanistan')
    return {
        'id': kw.get('id', 1),
        'name': name,
        'slug': slug,
    }


def _user_apps():
    """Returns user's apps object."""
    return {
        'installed': [SPECIAL_SLUGS_TO_IDS['installed']],
        'developed': [SPECIAL_SLUGS_TO_IDS['developed']],
        'purchased': [SPECIAL_SLUGS_TO_IDS['purchased']]
    }


def app(**kw):
    """
    In the API everything here except `user` should be serialized and keyed off
    counter:region:locale.
    """
    global counter
    counter += 1

    num_previews = kw.get('num_previews', 4)
    slug = kw.get('slug', 'app-%d' % counter)

    data = {
        'id': SPECIAL_SLUGS_TO_IDS.get(slug, counter),
        'author': random.choice(AUTHORS),
        'categories': ['social', 'games'],
        'content_ratings': {
            'body': 'generic',
            'rating': '12',
            'descriptors': ['scary', 'lang', 'drugs'],
            'interactives': ['users-interact', 'shares-info']
        },
        'current_version': text('%d.0' % int(random.random() * 20)),
        'description': {'en-US': escape(kw.get('description',
                                               rand_text(100)))},
        'device_types': ['desktop', 'firefoxos', 'android-mobile',
                         'android-tablet'],
        'file_size': 12345,
        'homepage': 'http://marketplace.mozilla.org/',
        'icons': {
            64: '/media/img/logos/64.png'
        },
        'is_packaged': slug == 'packaged' or rand_bool(),
        'last_updated': rand_datetime(),
        'manifest_url':
            # Minifest if packaged
            'http://%s.testmanifest.com/manifest.webapp' % slug,
        'name': text('App %d' % counter),
        'notices': random.choice(MESSAGES),
        'premium_type': 'free',
        'previews': [_app_preview() for i in range(num_previews)],
        'price': None,
        'price_locale': '$0.00',
        'promo_images': {
            'small': random.choice(PROMO_IMAGES),
            'large': random.choice(PROMO_IMAGES),
        },
        'privacy_policy': kw.get('privacy_policy', rand_text()),
        'public_stats': False,
        'slug': slug,
        'ratings': {
            'average': random.random() * 4 + 1,
            'count': int(random.random() * 500),
        },
        'release_notes': kw.get('release_notes', rand_text(100)),
        'support_email': text('support@%s.com' % slug),
        'support_url': text('support.%s.com' % slug),
        'upsell': False,
    }

    data.update(app_user_data(slug))
    data = dict(data, **kw)

    # Special apps.
    if slug == 'paid':
        data.update(
            price=3.50,
            price_locale='$3.50',
            payment_required=True
        )
    elif slug == 'upsell':
        data['upsell'] = {
            'id': random.randint(1, 10000),
            'name': rand_text(),
            'icon_url': '/media/img/logos/firefox-256.png',
            'app_slug': 'upsold',
            'resource_uri': '/api/v1/fireplace/app/%s/' % 'upsold',
        }
    elif slug == 'packaged':
        data['current_version'] = '1.0'
    elif slug == 'unrated':
        data['ratings'] = {
            'average': 0,
            'count': 0,
        }
    elif slug == 'tracking':
        data['id'] = 1234
        data['author'] = 'Tracking'
        data['name'] = 'Tracking'
    elif slug.startswith('num-previews-'):
        data['previews'] = [_app_preview() for x in
                            range(int(slug.split('num-previews-')[1]))]

    if slug in SPECIAL_APP_SLUGS or slug.startswith('num-previews-'):
        data['name'] = string.capwords(
            slug.replace('_', ' ').replace('-', ' '))

    return data


def review_user_data(slug=None):
    data = {
        'user': {
            'has_rated': False,
            'can_rate': True,
        }
    }
    if data['user']['can_rate']:
        data['rating'] = random.randint(1, 5)
        data['user']['has_rated'] = False

    # Conditional slugs for great debugging.
    if slug == 'has_rated':
        data['user']['has_rated'] = True
        data['user']['can_rate'] = True
    elif slug == 'can_rate':
        data['user']['has_rated'] = False
        data['user']['can_rate'] = True
    elif slug == 'cant_rate':
        data['user']['can_rate'] = False

    return data


def app_user_data(slug=None):
    data = {
        'user': {
            'developed': rand_bool(),
        }
    }
    # Conditional slugs for great debugging.
    if slug == 'developed':
        data['user']['developed'] = True
    elif slug == 'user':
        data['user']['developed'] = False

    return data


def app_user_review(slug, **kw):
    data = {
        'body': kw.get('review', rand_text()),
        'rating': 4
    }
    return data


def review(slug=None, **kw):
    global counter
    counter += 1

    version = None
    if rand_bool():
        version = {
            'name': random.randint(1, 3),
            'latest': False,
        }

    data = dict({
        'rating': random.randint(1, 5),
        'body': rand_text(n=20),
        'created': rand_datetime(),
        'has_flagged': False,
        'is_author': False,
        'modified': rand_datetime(),
        'report_spam': '/api/v1/apps/rating/%d/flag/' % counter,
        'resource_uri': '/api/v1/apps/rating/%d/' % counter,
        'user': {
            'display_name': text(random.choice(USER_NAMES)),
            'id': counter,
        },
        'version': version,
    }, **kw)

    if slug == 'has_flagged':
        data['has_flagged'] = True

    return data


def preview():
    global counter
    counter += 1

    return {
        'id': counter,
        'position': 1,
        'thumbnail_url': 'http://f.cl.ly/items/103C0e0I1d1Q1f2o3K2B/'
                         'mkt-collection-logo.png',
        'image_url': SAMPLE_BG,
        'filetype': 'image/png',
        'resource_uri': 'pi/v1/apps/preview/%d' % counter
    }


def extension(**kw):
    global counter
    counter += 1
    slug = kw.get('slug', 'extension-%d' % counter)
    status = 'public'

    if slug == 'incomplete' or slug == 'pending':
        status = slug

    version = {
        'id': random.randint(1, 3),
        'download_url': URLS['extension_download'],
        'unsigned_download_url': URLS['extension_unsigned_download'],
        'status': status,
        'version': '0.%d' % random.randint(1, 3)
    }

    return {
        'id': counter,
        'description': {'en-US': escape(kw.get('description',
                                               rand_text(100)))},
        'latest_version': version,
        'latest_public_version': version,
        'mini_manifest_url': URLS['extension_mini_manifest'],
        'name': text('Add-on %d' % counter),
        'slug': slug,
        'status': status
    }
