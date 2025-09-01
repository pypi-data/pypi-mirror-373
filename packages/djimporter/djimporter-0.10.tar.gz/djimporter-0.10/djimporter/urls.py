from django.urls import path

from . import views

app_name = 'djimporter'

urlpatterns = [
    path('logs/', views.ListImportsView.as_view(), name='importlog-list'),
    path('logs/<int:pk>/', views.ImportDetailView.as_view(), name='importlog-detail'),
    path('logs/<int:pk>/extended', views.ImportDetailExtendedView.as_view(), name='importlog-detail-extended'),
    path('logs/<int:pk>/delete/', views.ImportDeleteView.as_view(), name='importlog-delete'),
    path('logs/<int:pk>/get/', views.ImportLogGetView.as_view(), name='importlog-get')
]
