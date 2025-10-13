from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.views import PasswordResetView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .forms import ProfesionalLoginForm, ProfesionalRegistrationForm, ProfesionalUpdateForm,ProfesionalSetPasswordForm,ProfesionalPasswordResetForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime, date
from .models import Cita, Video, Libro, Enlace, Articulo


# ==================== VISTAS DE AUTENTICACIÓN ====================

class ProfesionalLoginView(LoginView):
    """Vista personalizada para el login de profesionales"""
    form_class = ProfesionalLoginForm
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def get(self, request, *args, **kwargs):
        """Manejar GET request y verificar cookies"""
        # Verificar si viene de un logout exitoso
        if request.COOKIES.get('logout_message'):
            messages.info(request, '✅ Has cerrado sesión exitosamente.')
        
        # Verificar si viene de una eliminación de cuenta
        if request.COOKIES.get('account_deleted'):
            messages.warning(request, '⚠️ Tu cuenta ha sido eliminada permanentemente. Esperamos verte de nuevo pronto.')
        
        response = super().get(request, *args, **kwargs)
        
        # Eliminar las cookies si existen
        if request.COOKIES.get('logout_message'):
            response.delete_cookie('logout_message')
        if request.COOKIES.get('account_deleted'):
            response.delete_cookie('account_deleted')
        
        return response
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            # Si no marca "recordarme", la sesión expira al cerrar el navegador
            self.request.session.set_expiry(0)
        else:
            # Mantener sesión por 2 semanas
            self.request.session.set_expiry(1209600)
        
        messages.success(self.request, f'¡Bienvenido de nuevo, {form.get_user().nombre_completo}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos. Por favor, intenta de nuevo.')
        return super().form_invalid(form)


class ProfesionalRegisterView(CreateView):
    """Vista para registro de nuevos profesionales"""
    form_class = ProfesionalRegistrationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        # Si ya está autenticado, redirigir al dashboard
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Autenticar automáticamente después del registro
        login(self.request, self.object)
        messages.success(
            self.request, 
            f'¡Registro exitoso! Bienvenido a DislexIA, {self.object.nombre_completo}.'
        )
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error en el registro. Por favor, verifica los datos ingresados.')
        return super().form_invalid(form)


class ProfesionalLogoutView(LogoutView):
    """Vista para cerrar sesión"""
    template_name = None  # No usar template, solo redirigir
    http_method_names = ['get', 'post', 'options']
    
    def get_next_page(self):
        """Obtener la página a la que redirigir después del logout"""
        return reverse_lazy('core:login')
    
    def dispatch(self, request, *args, **kwargs):
        """Procesar el logout y agregar mensaje"""
        response = super().dispatch(request, *args, **kwargs)
        # Agregar un mensaje como cookie temporal que se mostrará en el login
        if isinstance(response, redirect.__class__) or hasattr(response, 'url'):
            response.set_cookie('logout_message', '1', max_age=5)
        return response


# ==================== VISTAS PROTEGIDAS ====================

@method_decorator(login_required, name='dispatch')
class CalendarView(TemplateView):
    template_name = 'calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Calendario - DislexIA',
            'active_section': 'calendar',
        })
        return context

class CrearRecursoView(LoginRequiredMixin, CreateView):
    model = Video
    template_name = 'recurso.html'
    fields = ['titulo', 'descripcion', 'archivo', 'categoria']  # según tu modelo
    success_url = reverse_lazy('core:documents')

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        return super().form_valid(form)

class DocumentsView(TemplateView):
    template_name = 'documents.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener todos los recursos activos
        videos = Video.objects.filter(activo=True)
        libros = Libro.objects.filter(activo=True)
        enlaces = Enlace.objects.filter(activo=True)
        articulos = Articulo.objects.filter(activo=True)

        # Crear lista unificada con etiqueta de categoría
        recursos_list = []

        # Agregar videos
        for video in videos:
            recursos_list.append({
                'id': video.id,
                'categoria': 'videos',
                'get_categoria_display': 'Video',
                'titulo': video.titulo,
                'descripcion': video.descripcion,
                'imagen': None,  # Videos no tienen imagen de portada
                'duracion': video.duracion,
                'autor': None,
                'visitas': 0,  # Agregar si tienes este campo
                'url_externa': None,
                'video_embed': video.get_embed_code(),  # Para usar en el template
            })

        # Agregar libros
        for libro in libros:
            recursos_list.append({
                'id': libro.id,
                'categoria': 'libros',
                'get_categoria_display': 'Libro',
                'titulo': libro.titulo,
                'descripcion': libro.descripcion,
                'imagen': libro.portada if hasattr(libro, 'portada') else None,
                'duracion': None,
                'autor': libro.autor,
                'visitas': 0,
                'url_externa': libro.url_descarga if hasattr(libro, 'url_descarga') else None,
                'video_embed': None,
            })

        # Agregar enlaces
        for enlace in enlaces:
            recursos_list.append({
                'id': enlace.id,
                'categoria': 'enlaces',
                'get_categoria_display': 'Enlace',
                'titulo': enlace.titulo,
                'descripcion': enlace.descripcion,
                'imagen': None,
                'duracion': None,
                'autor': None,
                'visitas': 0,
                'url_externa': enlace.url,
                'video_embed': None,
            })

        # Agregar artículos
        for articulo in articulos:
            recursos_list.append({
                'id': articulo.id,
                'categoria': 'articulos',
                'get_categoria_display': 'Artículo',
                'titulo': articulo.titulo,
                'descripcion': articulo.resumen if hasattr(articulo, 'resumen') else articulo.descripcion,
                'imagen': articulo.imagen if hasattr(articulo, 'imagen') else None,
                'duracion': None,
                'autor': articulo.autor,
                'visitas': 0,
                'url_externa': articulo.url_fuente if hasattr(articulo, 'url_fuente') else None,
                'video_embed': None,
            })

        context.update({
            'page_title': 'Recursos Digitales - DislexIA',
            'active_section': 'documents',
            'recursos': recursos_list,
            # También pasamos separados por si acaso
            'videos': videos,
            'libros': libros,
            'enlaces': enlaces,
            'articulos': articulos,
        })
        return context


class RecursoAPIView(TemplateView):
    """Vista base para API de recursos"""

    @method_decorator(login_required)
    @method_decorator(require_http_methods(["GET", "POST", "PUT", "DELETE"]))
    def dispatch(self, *args, **kwargs):
        # Solo staff puede crear/editar/eliminar
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            if not self.request.user.is_staff:
                return JsonResponse({'error': 'No autorizado'}, status=403)
        return super().dispatch(*args, **kwargs)


class VideoAPIView(RecursoAPIView):
    """API para Videos"""

    def get(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id)
            return JsonResponse({
                'id': video.id,
                'titulo': video.titulo,
                'descripcion': video.descripcion,
                'codigo_embed': video.codigo_embed,
                'duracion': video.duracion,
                'fecha_publicacion': str(video.fecha_publicacion) if video.fecha_publicacion else None,
            })
        except Video.DoesNotExist:
            return JsonResponse({'error': 'Video no encontrado'}, status=404)

    def post(self, request):
        try:
            data = json.loads(request.body)
            video = Video.objects.create(
                titulo=data.get('titulo'),
                descripcion=data.get('descripcion'),
                codigo_embed=data.get('codigo_embed'),
                duracion=data.get('duracion', ''),
                creado_por=request.user,
                activo=True
            )
            return JsonResponse({
                'message': 'Video creado exitosamente',
                'id': video.id
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def put(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id)
            data = json.loads(request.body)

            video.titulo = data.get('titulo', video.titulo)
            video.descripcion = data.get('descripcion', video.descripcion)
            video.codigo_embed = data.get('codigo_embed', video.codigo_embed)
            video.duracion = data.get('duracion', video.duracion)
            video.save()

            return JsonResponse({'message': 'Video actualizado exitosamente'})
        except Video.DoesNotExist:
            return JsonResponse({'error': 'Video no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def delete(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id)
            video.delete()
            return JsonResponse({'message': 'Video eliminado exitosamente'})
        except Video.DoesNotExist:
            return JsonResponse({'error': 'Video no encontrado'}, status=404)


class LibroAPIView(RecursoAPIView):
    """API para Libros"""

    def get(self, request, libro_id):
        try:
            libro = Libro.objects.get(id=libro_id)
            return JsonResponse({
                'id': libro.id,
                'titulo': libro.titulo,
                'descripcion': libro.descripcion,
                'autor': libro.autor,
                'url_descarga': libro.url_descarga,
                'año_publicacion': libro.año_publicacion,
            })
        except Libro.DoesNotExist:
            return JsonResponse({'error': 'Libro no encontrado'}, status=404)

    def post(self, request):
        try:
            data = json.loads(request.body)
            libro = Libro.objects.create(
                titulo=data.get('titulo'),
                descripcion=data.get('descripcion'),
                autor=data.get('autor'),
                url_descarga=data.get('url_descarga', ''),
                año_publicacion=data.get('año_publicacion'),
                creado_por=request.user,
                activo=True
            )
            return JsonResponse({
                'message': 'Libro creado exitosamente',
                'id': libro.id
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def put(self, request, libro_id):
        try:
            libro = Libro.objects.get(id=libro_id)
            data = json.loads(request.body)

            libro.titulo = data.get('titulo', libro.titulo)
            libro.descripcion = data.get('descripcion', libro.descripcion)
            libro.autor = data.get('autor', libro.autor)
            libro.url_descarga = data.get('url_descarga', libro.url_descarga)
            libro.año_publicacion = data.get('año_publicacion', libro.año_publicacion)
            libro.save()

            return JsonResponse({'message': 'Libro actualizado exitosamente'})
        except Libro.DoesNotExist:
            return JsonResponse({'error': 'Libro no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def delete(self, request, libro_id):
        try:
            libro = Libro.objects.get(id=libro_id)
            libro.delete()
            return JsonResponse({'message': 'Libro eliminado exitosamente'})
        except Libro.DoesNotExist:
            return JsonResponse({'error': 'Libro no encontrado'}, status=404)


class EnlaceAPIView(RecursoAPIView):
    """API para Enlaces"""

    def get(self, request, enlace_id):
        try:
            enlace = Enlace.objects.get(id=enlace_id)
            return JsonResponse({
                'id': enlace.id,
                'titulo': enlace.titulo,
                'descripcion': enlace.descripcion,
                'url': enlace.url,
                'categoria': enlace.categoria,
            })
        except Enlace.DoesNotExist:
            return JsonResponse({'error': 'Enlace no encontrado'}, status=404)

    def post(self, request):
        try:
            data = json.loads(request.body)
            enlace = Enlace.objects.create(
                titulo=data.get('titulo'),
                descripcion=data.get('descripcion'),
                url=data.get('url'),
                categoria=data.get('categoria', ''),
                creado_por=request.user,
                activo=True
            )
            return JsonResponse({
                'message': 'Enlace creado exitosamente',
                'id': enlace.id
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def put(self, request, enlace_id):
        try:
            enlace = Enlace.objects.get(id=enlace_id)
            data = json.loads(request.body)

            enlace.titulo = data.get('titulo', enlace.titulo)
            enlace.descripcion = data.get('descripcion', enlace.descripcion)
            enlace.url = data.get('url', enlace.url)
            enlace.categoria = data.get('categoria', enlace.categoria)
            enlace.save()

            return JsonResponse({'message': 'Enlace actualizado exitosamente'})
        except Enlace.DoesNotExist:
            return JsonResponse({'error': 'Enlace no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def delete(self, request, enlace_id):
        try:
            enlace = Enlace.objects.get(id=enlace_id)
            enlace.delete()
            return JsonResponse({'message': 'Enlace eliminado exitosamente'})
        except Enlace.DoesNotExist:
            return JsonResponse({'error': 'Enlace no encontrado'}, status=404)


class ArticuloAPIView(RecursoAPIView):
    """API para Artículos"""

    def get(self, request, articulo_id):
        try:
            articulo = Articulo.objects.get(id=articulo_id)
            return JsonResponse({
                'id': articulo.id,
                'titulo': articulo.titulo,
                'descripcion': articulo.resumen if hasattr(articulo, 'resumen') else articulo.descripcion,
                'autor': articulo.autor,
                'url_fuente': articulo.url_fuente,
                'fecha_publicacion': str(articulo.fecha_publicacion) if articulo.fecha_publicacion else None,
            })
        except Articulo.DoesNotExist:
            return JsonResponse({'error': 'Artículo no encontrado'}, status=404)

    def post(self, request):
        try:
            data = json.loads(request.body)

            # Crear diccionario base
            articulo_data = {
                'titulo': data.get('titulo'),
                'autor': data.get('autor'),
                'url_fuente': data.get('url_fuente', ''),
                'creado_por': request.user,
                'activo': True
            }

            # Agregar campo según el modelo
            if hasattr(Articulo, 'resumen'):
                articulo_data['resumen'] = data.get('descripcion')
            else:
                articulo_data['descripcion'] = data.get('descripcion')

            # Fecha de publicación
            fecha_pub = data.get('fecha_publicacion')
            if fecha_pub:
                from datetime import datetime
                articulo_data['fecha_publicacion'] = datetime.strptime(fecha_pub, '%Y-%m-%d').date()

            articulo = Articulo.objects.create(**articulo_data)

            return JsonResponse({
                'message': 'Artículo creado exitosamente',
                'id': articulo.id
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def put(self, request, articulo_id):
        try:
            articulo = Articulo.objects.get(id=articulo_id)
            data = json.loads(request.body)

            articulo.titulo = data.get('titulo', articulo.titulo)
            articulo.autor = data.get('autor', articulo.autor)
            articulo.url_fuente = data.get('url_fuente', articulo.url_fuente)

            # Actualizar descripción/resumen según el modelo
            if hasattr(articulo, 'resumen'):
                articulo.resumen = data.get('descripcion', articulo.resumen)
            else:
                articulo.descripcion = data.get('descripcion', articulo.descripcion)

            # Actualizar fecha si se proporciona
            fecha_pub = data.get('fecha_publicacion')
            if fecha_pub:
                from datetime import datetime
                articulo.fecha_publicacion = datetime.strptime(fecha_pub, '%Y-%m-%d').date()

            articulo.save()

            return JsonResponse({'message': 'Artículo actualizado exitosamente'})
        except Articulo.DoesNotExist:
            return JsonResponse({'error': 'Artículo no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def delete(self, request, articulo_id):
        try:
            articulo = Articulo.objects.get(id=articulo_id)
            articulo.delete()
            return JsonResponse({'message': 'Artículo eliminado exitosamente'})
        except Articulo.DoesNotExist:
            return JsonResponse({'error': 'Artículo no encontrado'}, status=404)




# Panel de Administración de Recursos
class AdminRecursosView(LoginRequiredMixin, TemplateView):
    template_name = 'recursos/admin_recursos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Administrar Recursos',
            'videos': Video.objects.all(),
            'libros': Libro.objects.all(),
            'enlaces': Enlace.objects.all(),
            'articulos': Articulo.objects.all(),
        })
        return context

@method_decorator(login_required, name='dispatch')
class SettingsView(TemplateView):
    template_name = 'settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Configuraciones - DislexIA',
            'active_section': 'settings',
        })
        return context

@method_decorator(login_required, name='dispatch')
class SupportView(TemplateView):
    template_name = 'support.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Soporte - DislexIA',
            'active_section': 'support',
        })
        return context

@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Perfil - DislexIA',
            'active_section': 'profile',
            'form': ProfesionalUpdateForm(instance=self.request.user)
        })
        return context


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    """Vista para actualizar el perfil del profesional"""
    model = None  # Se establece dinámicamente
    form_class = ProfesionalUpdateForm
    success_url = reverse_lazy('core:profile')
    
    def get_object(self, queryset=None):
        # Retornar el usuario actual
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, '¡Perfil actualizado exitosamente!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el perfil. Por favor, verifica los datos.')
        return redirect('core:profile')


@method_decorator(login_required, name='dispatch')
class DeleteAccountView(TemplateView):
    """Vista para eliminar la cuenta del usuario permanentemente"""
    
    def post(self, request, *args, **kwargs):
        """Procesar la eliminación de la cuenta"""
        user = request.user
        username = user.username
        
        try:
            # Cerrar sesión del usuario
            from django.contrib.auth import logout
            logout(request)
            
            # Eliminar la cuenta permanentemente
            user.delete()
            
            # Mensaje de confirmación (se guarda en cookie para mostrarlo después del redirect)
            messages.success(request, f'La cuenta de {username} ha sido eliminada permanentemente.')
            
            # Redirigir al login
            response = redirect('core:login')
            response.set_cookie('account_deleted', 'true', max_age=10)
            return response
            
        except Exception as e:
            messages.error(request, f'Error al eliminar la cuenta: {str(e)}')
            return redirect('core:settings')


# ==================== VISTAS DE RECUPERACIÓN DE CONTRASEÑA ====================

class ProfesionalPasswordResetView(PasswordResetView):
    """Vista para solicitar recuperación de contraseña"""
    form_class = ProfesionalPasswordResetForm
    template_name = 'auth/password_reset_form.html'
    email_template_name = 'auth/password_reset_email.html'
    html_email_template_name = 'auth/password_reset_email.html'
    subject_template_name = 'auth/password_reset_subject.txt'
    success_url = reverse_lazy('core:password_reset_done')
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            'Si el correo electrónico existe en nuestro sistema, recibirás un enlace de recuperación.'
        )
        return super().form_valid(form)


class ProfesionalPasswordResetDoneView(PasswordResetDoneView):
    """Vista de confirmación después de solicitar recuperación"""
    template_name = 'auth/password_reset_done.html'


class ProfesionalPasswordResetConfirmView(PasswordResetConfirmView):
    """Vista para establecer nueva contraseña usando el token"""
    form_class = ProfesionalSetPasswordForm
    template_name = 'auth/password_reset_confirm.html'
    success_url = reverse_lazy('core:password_reset_complete')
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            '¡Contraseña cambiada exitosamente! Ya puedes iniciar sesión con tu nueva contraseña.'
        )
        return super().form_valid(form)


class ProfesionalPasswordResetCompleteView(PasswordResetCompleteView):
    """Vista final después de cambiar la contraseña"""
    template_name = 'auth/password_reset_complete.html'


@login_required
def get_citas_dia(request):
    """Obtener citas del día para el sidebar"""
    fecha_str = request.GET.get('fecha', date.today().isoformat())
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        fecha = date.today()
    
    citas = Cita.objects.filter(
        usuario=request.user,
        fecha=fecha
    ).order_by('hora')
    
    citas_data = [{
        'id': cita.id,
        'nombre_paciente': cita.nombre_paciente,
        'foto_paciente': cita.foto_paciente.url if cita.foto_paciente else None,
        'hora': cita.hora.strftime('%H:%M'),
        'fecha': cita.fecha.isoformat(),
        'completada': cita.completada,
        'notas': cita.notas
    } for cita in citas]
    
    return JsonResponse({'citas': citas_data})

@login_required
@require_http_methods(["POST"])
def crear_cita(request):
    """Crear una nueva cita"""
    try:
        print("=== DEBUG: Iniciando crear_cita ===")
        print(f"POST data: {request.POST}")
        print(f"FILES: {request.FILES}")
        
        # Manejar FormData en lugar de JSON
        nombre_paciente = request.POST.get('nombre_paciente')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        notas = request.POST.get('notas', '')
        
        print(f"Datos recibidos - Paciente: {nombre_paciente}, Fecha: {fecha_str}, Hora: {hora_str}")
        
        if not nombre_paciente or not fecha_str or not hora_str:
            return JsonResponse({
                'success': False, 
                'error': 'Faltan campos requeridos'
            }, status=400)
        
        # Convertir strings a objetos date y time
        from datetime import datetime
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        hora = datetime.strptime(hora_str, '%H:%M').time()
        
        cita = Cita.objects.create(
            usuario=request.user,
            nombre_paciente=nombre_paciente,
            fecha=fecha,
            hora=hora,
            notas=notas
        )
        
        print(f"Cita creada con ID: {cita.id}")
        
        # Manejar archivo de foto si existe
        if 'foto_paciente' in request.FILES:
            cita.foto_paciente = request.FILES['foto_paciente']
            cita.save()
            print("Foto agregada exitosamente")
        
        return JsonResponse({
            'success': True,
            'cita': {
                'id': cita.id,
                'nombre_paciente': cita.nombre_paciente,
                'fecha': cita.fecha.isoformat(),  # Ahora sí es un objeto date
                'hora': cita.hora.strftime('%H:%M'),  # Ahora sí es un objeto time
                'foto_paciente': cita.foto_paciente.url if cita.foto_paciente else None
            }
        })
    except ValueError as e:
        print(f"=== ERROR de formato en crear_cita: {str(e)} ===")
        return JsonResponse({
            'success': False, 
            'error': f'Formato de fecha u hora inválido: {str(e)}'
        }, status=400)
    except Exception as e:
        print(f"=== ERROR en crear_cita: {str(e)} ===")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=400)

@login_required
@require_http_methods(["DELETE"])
def eliminar_cita(request, cita_id):
    """Eliminar una cita"""
    try:
        cita = Cita.objects.get(id=cita_id, usuario=request.user)
        cita.delete()
        return JsonResponse({'success': True})
    except Cita.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cita no encontrada'}, status=404)

@login_required
@require_http_methods(["POST"])
def marcar_cita_completada(request, cita_id):
    """Marcar cita como completada"""
    try:
        cita = Cita.objects.get(id=cita_id, usuario=request.user)
        cita.completada = not cita.completada
        cita.save()
        return JsonResponse({'success': True, 'completada': cita.completada})
    except Cita.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cita no encontrada'}, status=404)

