from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('our-story/', views.our_story, name='our_story'),
    path('sustainable-living/', views.sustainable_living, name='sustainable_living'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('returns-policy/', views.returns_policy, name='returns_policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_conditions, name='terms_conditions'),
    path('api/newsletter/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
]
