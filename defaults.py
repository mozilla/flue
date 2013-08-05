import random
from cgi import escape
from datetime import date, timedelta


XSS = False

xss_text = '"\'><script>alert("poop");</script><\'"'
dummy_text = 'foo bar zip zap cvan fizz buzz something something'.split()


def text(default):
    return xss_text if XSS else default


def ptext(len=10):
    return text(' '.join(random.choice(dummy_text) for i in xrange(len)))


def rand_bool():
    return random.choice((True, False))


def category(slug, name):
    return {
        'name': text(name),
        'slug': slug,
    }

AUTHORS = [
    text('basta'),
    text('cvan'),
    text('Chris Van Halen')
]

MESSAGES = [
    ['be careful, cvan made it', 'loljk'],
    ["it's probably a game or something"],
    None
]

SCREENSHOT_MAP = [
    (70, 70367),
    (78, 78540),
    (72, 72384),
]


def _app_preview():
    url = ('https://marketplace-dev-cdn.allizom.org/'
           'img/uploads/previews/%%s/%d/%d.png' %
               random.choice(SCREENSHOT_MAP))
    return {
        'caption': ptext(5),
        'filetype': 'image/png',
        'thumbnail_url': url % 'thumbs',
        'image_url': url % 'full',
    }


def app(name, slug, **kwargs):
    # In the API everything here except `user` should be serialized and
    # keyed off app_id:region:locale.
    data = {
        'name': text(name),
        'slug': slug,
        'description': escape(kwargs.get('description', ptext(100))),
        'is_packaged': slug == 'packaged' or rand_bool(),
        'manifest_url':
            'http://%s%s.testmanifest.com/manifest.webapp' %
            (ptext(1), random.randint(1, 50000)),  # Minifest if packaged
        'current_version': text('%d.0' % int(random.random() * 20)),
        'icons': {
            16: '/media/img/icons/firefox-beta.png',
            48: '/media/img/icons/firefox-beta.png',
            64: '/media/img/icons/firefox-beta.png',
            128: '/media/img/icons/firefox-beta.png'
        },
        'previews': [_app_preview() for i in range(4)],
        'author': random.choice(AUTHORS),
        'ratings': {
            'average': random.random() * 4 + 1,
            'count': int(random.random() * 500),
        },
        'notices': random.choice(MESSAGES),
        'support_email': text('support@%s.com' % slug),
        'homepage': 'http://marketplace.mozilla.org/',
        'privacy_policy': kwargs.get('privacy_policy', ptext()),
        'public_stats': False,
        'upsell': False,
        'content_ratings': {
            'dejus': {'name': '12', 'description': text('Ask your parents')},
            'esrb': {'name': 'L', 'description': text('L for BASTA')},
        },
        'device_types': ['desktop', 'firefoxos', 'android-mobile',
                         'android-tablet'],
    }

    has_price = rand_bool()
    price = '%.2f' % (random.random() * 10)
    if slug == 'free':
        has_price = False
    elif slug == 'paid':
        has_price = True
        price = '0.99'

    if slug == 'upsell':
        data['upsell'] = {
            'id': random.randint(1, 10000),
            'name': ptext(),
            'icon_url': '/media/img/icons/firefox-beta.png',
            'app_slug': 'upsold',
            'resource_uri': '/api/v1/fireplace/app/%s/' % 'upsold',
        }

    if has_price:
        data.update(price=price, price_locale='$%s' % price)
    else:
        data.update(price=None, price_locale='$0.00')

    data['payment_required'] = has_price

    if slug == 'packaged':
        data['current_version'] = '1.0'

    data.update(app_user_data(slug))

    return data


def app_user_data(slug=None):
    data = {
        'user': {
            'developed': rand_bool(),
            'has_rated': rand_bool(),
            'can_rate': rand_bool(),
        }
    }
    if data['user']['can_rate']:
        data['rating'] = random.randint(1, 5)
        data['user']['has_rated'] = rand_bool()

    # Conditional slugs for great debugging.
    if slug == 'has_rated':
        data['user']['has_rated'] = True
        data['user']['can_rate'] = True
    elif slug == 'can_rate':
        data['user']['has_rated'] = False
        data['user']['can_rate'] = True
    elif slug == 'cant_rate':
        data['user']['can_rate'] = False
    elif slug == 'developer':
        data['user']['developed'] = True
    elif slug == 'user':
        data['user']['developed'] = False

    return data


def app_user_review(slug, **kwargs):
    data = {
        'body': kwargs.get('review', ptext()),
        'rating': 4
    }
    return data


user_names = ['Cvan', 'Basta', 'Davor', 'Queen Krupa']


def rand_posted():
    rand_date = date.today() - timedelta(days=random.randint(0, 600))
    return rand_date.strftime('%b %d %Y %H:%M:%S')


def rating():
    version = None
    if random.choice((True, False)):
        version = {
            'name': random.randint(1, 3),
            'latest': False,
        }
    report_spam = '/api/v1/apps/rating/%d/flag/' % random.randint(1000, 9999)

    return {
        'rating': 4,
        'body': ptext(20),
        'is_flagged': random.randint(1, 5) == 1,
        'is_author': random.randint(1, 5) == 1,
        'posted': rand_posted(),
        'report_spam': report_spam,
        'user': {
            'display_name': text(random.choice(user_names)),
            'id': random.randint(1000, 9999),
        },
        'version': version,
    }


def collection(name, slug, **kwargs):
    return {
        'name': text(name),
        'slug': slug,
        'collection_type': kwargs.get('collection_type') or 'standard',
        'author': text('Basta Splasha'),
        'description': ptext(),
        'apps': [app('Featured App', 'creat%d' % i)
                 for i in xrange(3)]
    }
