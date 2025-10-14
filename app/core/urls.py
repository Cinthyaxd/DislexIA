from django.urls import include, path
from . import views
from .views import get_citas_dia, crear_cita, eliminar_cita, marcar_cita_completada
app_name = 'core'
urlpatterns = [
    # Autenticación
    path('login/', views.ProfesionalLoginView.as_view(), name='login'),
    path('register/', views.ProfesionalRegisterView.as_view(), name='register'),
    path('logout/', views.ProfesionalLogoutView.as_view(), name='logout'),
    
    # Recuperación de contraseña
    path('password-reset/', views.ProfesionalPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.ProfesionalPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.ProfesionalPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.ProfesionalPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Vistas protegidas
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('documents/', views.DocumentsView.as_view(), name='documents'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('support/', views.SupportView.as_view(), name='support'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('account/delete/', views.DeleteAccountView.as_view(), name='delete_account'),

    # Citas
    path('citas/dia/', get_citas_dia, name='get_citas_dia'),
    path('citas/crear/', crear_cita, name='crear_cita'),
    path('citas/<int:cita_id>/eliminar/', eliminar_cita, name='eliminar_cita'),
    path('citas/<int:cita_id>/completar/', marcar_cita_completada, name='marcar_cita_completada'),

    
    # ==================== API RECURSOS - VIDEOS ====================
    path('api/recursos/videos/', views.VideoAPIView.as_view(), name='api_video_list'),
    path('api/recursos/videos/<int:video_id>/', views.VideoAPIView.as_view(), name='api_video_detail'),

# ==================== API RECURSOS - LIBROS ====================
    path('api/recursos/libros/', views.LibroAPIView.as_view(), name='api_libro_list'),
    path('api/recursos/libros/<int:libro_id>/', views.LibroAPIView.as_view(), name='api_libro_detail'),

# ==================== API RECURSOS - ENLACES ====================
    path('api/recursos/enlaces/', views.EnlaceAPIView.as_view(), name='api_enlace_list'),
    path('api/recursos/enlaces/<int:enlace_id>/', views.EnlaceAPIView.as_view(), name='api_enlace_detail'),

# ==================== API RECURSOS - ARTÍCULOS ====================
    path('api/recursos/articulos/', views.ArticuloAPIView.as_view(), name='api_articulo_list'),
    path('api/recursos/articulos/<int:articulo_id>/', views.ArticuloAPIView.as_view(), name='api_articulo_detail'),
]
