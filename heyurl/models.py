from django.db import models
from datetime import datetime


class Url(models.Model):
    short_url = models.CharField(max_length=255, unique=True, blank=False)
    original_url = models.CharField(max_length=255, unique=True, blank=False)
    clicks = models.IntegerField(default=0)
    created_at = models.DateTimeField('date created', default=datetime.now)
    updated_at = models.DateTimeField('date updated', default=datetime.now)

    def clicked(self, browser, platform):
        self.clicks +=1
        self.click.create(browser=browser, platform=platform)
        self.save()

    def __str__(self):
        return self.short_url


class Click(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE, related_name='click')
    browser = models.CharField(max_length=255)
    platform = models.CharField(max_length=255)
    created_at = models.DateTimeField('date created', default=datetime.now)
    updated_at = models.DateTimeField('date updated', default=datetime.now)

    def __str__(self):
        return f'{self.url.__str__()}, browser-{self.browser}, platform-{self.platform}'
