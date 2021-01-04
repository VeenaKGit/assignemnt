from django.urls import path

from heyurl import views

urlpatterns = [
    path('', views.index, name='index'),
    path('store', views.store, name='store'),
    path('metrics/<int:pk>', views.click_metrics, name='click-metrics')
]
