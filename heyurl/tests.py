from django.test import TestCase
from django.urls import reverse
from .models import Url, Click
from .views import INVALID_URL_MSG, SUCCESS_MSG


class IndexTests(TestCase):
    def setUp(self):
        self.url_1 = Url.objects.create(
            short_url='07ERZ',
            original_url='https://www.caktusgroup.com/',
            clicks=0,
            created_at="2018-10-26T01:48:35Z",
            updated_at="2018-10-26T01:48:35Z"
        )

    def test_no_urls(self):
        """
        If no URLs exist, an appropriate message is displayed
        """
        self.url_1.delete()
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'heyurl/index.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no URLs in the system yet!')

    def test_one_urls(self):
        """
        If one URLs exist, an "no URL's exist" message not displayed
        """
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, template_name='heyurl/index.html')
        self.assertNotContains(response, '<div>There are no URLs in the system yet!</div>', status_code=200)
        self.assertContains(response, 'https://www.caktusgroup.com/')

    def test_submitting_new_url_failure(self):
        """
        When submitting an invalid URL, an error is returned to the user
        """
        response = self.client.post(reverse('store'), {
            'original_url': 'htps://developer.mozilla.org/en-US/'
        }, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), INVALID_URL_MSG)
        self.assertRedirects(response, '/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Url.objects.filter(original_url='htps://developer.mozilla.org/en-US/').count(), 0)

    def test_submitting_new_url_success(self):
        """
        When submitting a valid URL, a success message is displayed
        """
        response = self.client.post(reverse('store'), {
            'original_url': 'https://developer.mozilla.org/en-US/'
        }, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), SUCCESS_MSG)
        self.assertRedirects(response, '/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Url.objects.filter(original_url='https://developer.mozilla.org/en-US/').count(), 1)

    def test_visiting_short_url_missing(self):
        """
        If short URL does not exist, custom 404 page is displayed
        """
        response = self.client.get(reverse('short_url', kwargs={'short_url': 'ABC'}))
        self.assertTemplateUsed(response, 'heyurl/error404.html')
        self.assertEqual(response.status_code, 404)

    def test_visiting_short_url(self):
        """
        If short URL exists, stats logged and redirected to original URL
        """
        response = self.client.get(reverse('short_url', kwargs={'short_url': '07ERZ'}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Url.objects.get(pk=1).clicks, 1)
        self.assertEqual(Click.objects.all().count(), 1)
        self.assertRedirects(response, self.url_1.original_url, fetch_redirect_response=False)

    def tearDown(self):
        pass
        
