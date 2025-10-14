from django.urls import path
from . import views

app_name = 'apis'
urlpatterns = [
    path('recursos/videos/', views.VideoAPIView.as_view(), name='video_list'),
    path('es/recursos/videos/<int:video_id>/', views.VideoAPIView.as_view(), name='video_detail'),

    # API Libros
    path('recursos/libros/', views.LibroAPIView.as_view(), name='libro_list'),
    path('recursos/libros/<int:libro_id>/', views.LibroAPIView.as_view(), name='libro_detail'),

    # API Enlaces
    path('recursos/enlaces/', views.EnlaceAPIView.as_view(), name='enlace_list'),
    path('recursos/enlaces/<int:enlace_id>/', views.EnlaceAPIView.as_view(), name='enlace_detail'),

    # API Artículos
    path('recursos/articulos/', views.ArticuloAPIView.as_view(), name='articulo_list'),
    path('recursos/articulos/<int:articulo_id>/', views.ArticuloAPIView.as_view(), name='articulo_detail'),
]