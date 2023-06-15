from django.urls import path, include
from . import views
urlpatterns = [
    path("", views.home1, name='home'),
    path("audio/", views.audio, name="audio"),
    path('video/', views.video, name="video"),
    path('playlist/', views.playlist, name='playlist'),
    path('explore/', views.Explore, name='explore'),
    path('help/', views.help, name="help"),
    path('instagram/', views.instagram, name="instagram"),
    path('review/', views.review_page, name='review'),
    path('tiktok/', views.tiktok, name='tiktok'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
]