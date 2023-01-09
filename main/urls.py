# from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .pdf import generate_pdf

urlpatterns = [
    path('', views.upload, name='index'), 
    path('batch_view/<str:institute>/<str:department>/<str:session>/', views.batch_view, name='batch_view'),
    path('gradesheet_view/<str:institute>/<str:department>/<str:session>/<str:reg_no>/', generate_pdf, name="generate_pdf"), 
    path('test/<str:institute>/<str:department>/<str:session>/<str:reg_no>/', views.test, name='test'), 
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
