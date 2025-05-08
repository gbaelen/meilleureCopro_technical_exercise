from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path('', views.index, name='index'),
    path('stats/form/', views.form_view, name='stats_form'),
    path('api/stats/', views.StatisticsView.as_view(), name='api_stats'),
    path('api/add/', views.AddBienIciListingView.as_view(), name='api_add_listing'),
]