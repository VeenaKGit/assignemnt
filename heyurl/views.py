from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Url
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.contrib import messages
from django_user_agents.utils import get_user_agent
from django.db.models import Count
import random

INVALID_URL_MSG = f'URL provided is not valid, Please provide a valid URL'
SUCCESS_MSG = f'Short URL created successfully!'
SHORT_VALID_CHAR_SET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
SHORT_URL_LIMIT = 5
MAX = len(SHORT_VALID_CHAR_SET)**SHORT_URL_LIMIT - 1
SHORT_URL_MISSING = f'The requested short URL is missing in the sever'


def gen_short_url():
    hash_str = ''
    num = random.randint(1, MAX)
    while num > 0:
        r = num % len(SHORT_VALID_CHAR_SET)
        hash_str = hash_str + SHORT_VALID_CHAR_SET[r]
        num //= len(SHORT_VALID_CHAR_SET)
    return hash_str


def index(request):
    urls = Url.objects.order_by('-created_at')
    context = {'urls': urls}
    return render(request, 'heyurl/index.html', context)


def store(request):
    # FIXME: Insert a new URL object into storage
    original_url = request.POST.get('original_url')
    validate = URLValidator()
    try:
        validate(original_url)
    except ValidationError:
        messages.error(request, INVALID_URL_MSG)
    else:
        short_url_generated = gen_short_url()
        add_url = Url(short_url=short_url_generated,
                      original_url=original_url,
                      clicks=0)
        add_url.save()
        messages.success(request, SUCCESS_MSG)
    finally:
        return redirect('/')


def short_url(request, short_url):
    # FIXME: Do the logging to the db of the click with the user agent and browser
    try:
        url = Url.objects.get(short_url=short_url)
    except Url.DoesNotExist:
        return render(request, 'heyurl/error404.html', {'message': SHORT_URL_MISSING}, status=404)
    else:
        user_info = get_user_agent(request)
        url.clicked(user_info.browser.family, user_info.os.family)
        return redirect(url.original_url)


def click_metrics(request, pk):
    url = Url.objects.get(id=pk)
    data = url.click.values('created_at__month',
                            'created_at__day',
                            'browser',
                            'platform').annotate(count=Count('platform'))
    context = {
        'data': data,
        'total': url.click.all().count(),
        'url': url.short_url
    }
    return render(request, 'heyurl/metrics.html', context)
