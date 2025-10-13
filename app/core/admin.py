from django.contrib import admin
from django.utils.html import format_html
from .models import Nino, Profesional, ReporteIA, ValidacionProfesional, Video, Libro, Enlace, Articulo


@admin.register(Nino)
class NinoAdmin(admin.ModelAdmin):
    """Administrador para el modelo Niño - completamente editable"""
    
    list_display = [
        'nombre_completo_display',
        'edad',
        'genero',
        'idioma_nativo',
        'fecha_nacimiento',
        'total_evaluaciones',
        'ultima_evaluacion',
        'activo',
        'fecha_registro'
    ]
    list_filter = [
        'genero',
        'edad',
        'idioma_nativo',
        'activo',
        'fecha_registro'
    ]
    search_fields = ['nombres', 'apellidos', 'idioma_nativo']
    ordering = ['-fecha_registro', 'apellidos', 'nombres']
    list_per_page = 25
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'fecha_nacimiento', 'edad')
        }),
        ('Características', {
            'fields': ('genero', 'idioma_nativo')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas del Sistema', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_registro']
    
    def nombre_completo_display(self, obj):
        """Muestra el nombre completo con formato"""
        return format_html(
            '<strong>{}</strong>',
            obj.nombre_completo
        )
    nombre_completo_display.short_description = 'Nombre Completo'
    
    def total_evaluaciones(self, obj):
        """Muestra el total de evaluaciones del niño"""
        count = obj.evaluaciones.count()
        if count > 0:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{}</span>',
                count
            )
        return format_html(
            '<span style="color: #6c757d;">0</span>'
        )
    total_evaluaciones.short_description = 'Total Evaluaciones'
    
    def ultima_evaluacion(self, obj):
        """Muestra la fecha de la última evaluación"""
        ultima = obj.evaluaciones.first()  # Ya está ordenado por -fecha_hora_inicio
        if ultima:
            return format_html(
                '<span style="color: #007bff;">{}</span>',
                ultima.fecha_hora_inicio.strftime('%d/%m/%Y')
            )
        return format_html(
            '<span style="color: #6c757d;">Sin evaluaciones</span>'
        )
    ultima_evaluacion.short_description = 'Última Evaluación'
    
    def get_queryset(self, request):
        """Optimizar consultas con prefetch_related"""
        return super().get_queryset(request).prefetch_related('evaluaciones')


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    """Administrador para el modelo Profesional"""
    
    list_display = [
        'nombre_completo_display',
        'username',
        'especialidad',
        'numero_licencia',
        'email',
        'rol',
        'total_validaciones',
        'ultimo_acceso',
        'is_active'
    ]
    list_filter = [
        'rol',
        'especialidad',
        'is_active',
        'is_staff',
        'fecha_registro'
    ]
    search_fields = ['username', 'nombres', 'apellidos', 'especialidad', 'numero_licencia', 'email']
    ordering = ['-fecha_registro', 'apellidos', 'nombres']
    
    fieldsets = (
        ('Credenciales de Acceso', {
            'fields': ('username', 'password', 'email')
        }),
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'first_name', 'last_name')
        }),
        ('Información Profesional', {
            'fields': ('especialidad', 'numero_licencia', 'rol', 'imagen')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('fecha_registro', 'ultimo_acceso', 'last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_registro', 'last_login', 'date_joined']
    
    def nombre_completo_display(self, obj):
        """Muestra el nombre completo con formato"""
        return format_html(
            '<strong>{}</strong>',
            obj.nombre_completo
        )
    nombre_completo_display.short_description = 'Nombre Completo'
    
    def total_validaciones(self, obj):
        """Muestra el total de validaciones realizadas"""
        count = obj.validaciones.count()
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">{}</span>',
            count
        )
    total_validaciones.short_description = 'Validaciones'


@admin.register(ReporteIA)
class ReporteIAAdmin(admin.ModelAdmin):
    """Administrador para el modelo ReporteIA - solo lectura"""
    
    list_display = [
        'id',
        'evaluacion',
        'clasificacion_riesgo',
        'indice_riesgo',
        'confianza_prediccion',
        'fecha_generacion'
    ]
    list_filter = [
        'clasificacion_riesgo',
        'fecha_generacion'
    ]
    search_fields = [
        'evaluacion__nino__nombres',
        'evaluacion__nino__apellidos',
        'clasificacion_riesgo'
    ]
    ordering = ['-fecha_generacion']
    
    # Solo lectura
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]


@admin.register(ValidacionProfesional)
class ValidacionProfesionalAdmin(admin.ModelAdmin):
    """Administrador para el modelo ValidacionProfesional"""
    
    list_display = [
        'id',
        'profesional',
        'evaluacion',
        'riesgo_confirmado',
        'indice_ajustado',
        'requiere_seguimiento',
        'fecha_validacion'
    ]
    list_filter = [
        'riesgo_confirmado',
        'requiere_seguimiento',
        'fecha_validacion',
        'profesional'
    ]
    search_fields = [
        'evaluacion__nino__nombres',
        'evaluacion__nino__apellidos',
        'profesional__nombres',
        'profesional__apellidos'
    ]
    ordering = ['-fecha_validacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('profesional', 'evaluacion')
        }),
        ('Diagnóstico', {
            'fields': ('riesgo_confirmado', 'indice_ajustado', 'diagnostico_final')
        }),
        ('Detalles Clínicos', {
            'fields': ('notas_clinicas', 'plan_tratamiento', 'requiere_seguimiento')
        }),
        ('Fecha', {
            'fields': ('fecha_validacion',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_validacion']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'duracion', 'preview_thumbnail', 'activo', 'fecha_creacion', 'creado_por']
    list_filter = ['activo', 'fecha_creacion', 'fecha_publicacion']
    search_fields = ['titulo', 'descripcion']
    list_editable = ['activo']
    readonly_fields = ['creado_por', 'fecha_creacion', 'preview_video']
    date_hierarchy = 'fecha_creacion'

    fieldsets = (
        ('Información Principal', {
            'fields': ('titulo', 'descripcion', 'activo')
        }),
        ('Código de YouTube', {
            'fields': ('codigo_embed', 'preview_video'),
            'description': 'Pega aquí el código iframe completo que te da YouTube al hacer clic en "Compartir > Insertar"'
        }),
        ('Información Adicional', {
            'fields': ('duracion', 'fecha_publicacion'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('creado_por', 'fecha_creacion'),
            'classes': ('collapse',)
        }),
    )

    def preview_thumbnail(self, obj):
        """Muestra miniatura del video en la lista"""
        thumbnail_url = obj.get_thumbnail()
        if thumbnail_url:
            return format_html(
                '<img src="{}" style="width: 100px; height: auto; border-radius: 4px;" />',
                thumbnail_url
            )
        return '-'

    preview_thumbnail.short_description = 'Vista Previa'

    def preview_video(self, obj):
        """Muestra preview del video en el formulario"""
        if obj.codigo_embed:
            return format_html(
                '<div style="max-width: 560px;">{}</div>',
                obj.get_embed_code()
            )
        return 'No hay video para previsualizar'

    preview_video.short_description = 'Preview del Video'

    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(creado_por=request.user)


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'año_publicacion', 'preview_portada', 'activo', 'tiene_descarga',
                    'fecha_creacion']
    list_filter = ['activo', 'año_publicacion', 'fecha_creacion']
    search_fields = ['titulo', 'autor', 'descripcion', 'isbn']
    list_editable = ['activo']
    readonly_fields = ['creado_por', 'fecha_creacion', 'preview_portada_grande']
    date_hierarchy = 'fecha_creacion'

    fieldsets = (
        ('Información del Libro', {
            'fields': ('titulo', 'autor', 'descripcion', 'activo')
        }),
        ('Portada', {
            'fields': ('portada', 'preview_portada_grande'),
        }),
        ('Detalles Adicionales', {
            'fields': ('isbn', 'año_publicacion', 'url_descarga'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('creado_por', 'fecha_creacion'),
            'classes': ('collapse',)
        }),
    )

    def preview_portada(self, obj):
        """Miniatura en la lista"""
        if obj.portada:
            return format_html(
                '<img src="{}" style="width: 50px; height: auto; border-radius: 4px;" />',
                obj.portada.url
            )
        return '📚'

    preview_portada.short_description = 'Portada'

    def preview_portada_grande(self, obj):
        """Preview grande en el formulario"""
        if obj.portada:
            return format_html(
                '<img src="{}" style="max-width: 300px; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.portada.url
            )
        return 'No hay portada'

    preview_portada_grande.short_description = 'Preview de Portada'

    def tiene_descarga(self, obj):
        """Indica si tiene URL de descarga"""
        if obj.url_descarga:
            return format_html(
                '<span style="color: green;">✓ Sí</span>'
            )
        return format_html('<span style="color: red;">✗ No</span>')

    tiene_descarga.short_description = 'Descarga'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Enlace)
class EnlaceAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'url_corta', 'activo', 'fecha_creacion', 'creado_por']
    list_filter = ['activo', 'categoria', 'fecha_creacion']
    search_fields = ['titulo', 'descripcion', 'url', 'categoria']
    list_editable = ['activo', 'categoria']
    readonly_fields = ['creado_por', 'fecha_creacion']
    date_hierarchy = 'fecha_creacion'

    fieldsets = (
        ('Información del Enlace', {
            'fields': ('titulo', 'descripcion', 'url', 'activo')
        }),
        ('Organización', {
            'fields': ('categoria',),
        }),
        ('Metadatos', {
            'fields': ('creado_por', 'fecha_creacion'),
            'classes': ('collapse',)
        }),
    )

    def url_corta(self, obj):
        """Muestra URL acortada con link"""
        url_text = obj.url[:50] + '...' if len(obj.url) > 50 else obj.url
        return format_html(
            '<a href="{}" target="_blank" style="color: #0066cc;">{}</a>',
            obj.url,
            url_text
        )

    url_corta.short_description = 'URL'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'fecha_publicacion', 'preview_imagen', 'activo', 'tiene_url', 'fecha_creacion']
    list_filter = ['activo', 'fecha_publicacion', 'fecha_creacion']
    search_fields = ['titulo', 'autor', 'resumen', 'contenido']
    list_editable = ['activo']
    readonly_fields = ['creado_por', 'fecha_creacion', 'preview_imagen_grande', 'contador_palabras']
    date_hierarchy = 'fecha_publicacion'

    fieldsets = (
        ('Información del Artículo', {
            'fields': ('titulo', 'autor', 'fecha_publicacion', 'activo')
        }),
        ('Contenido', {
            'fields': ('resumen', 'contenido', 'contador_palabras'),
        }),
        ('Imagen', {
            'fields': ('imagen', 'preview_imagen_grande'),
        }),
        ('URL Externa', {
            'fields': ('url_fuente',),
            'description': 'Si el artículo está en otro sitio web, ingresa la URL aquí'
        }),
        ('Metadatos', {
            'fields': ('creado_por', 'fecha_creacion'),
            'classes': ('collapse',)
        }),
    )

    def preview_imagen(self, obj):
        """Miniatura en la lista"""
        if obj.imagen:
            return format_html(
                '<img src="{}" style="width: 60px; height: auto; border-radius: 4px;" />',
                obj.imagen.url
            )
        return '📄'

    preview_imagen.short_description = 'Imagen'

    def preview_imagen_grande(self, obj):
        """Preview grande en el formulario"""
        if obj.imagen:
            return format_html(
                '<img src="{}" style="max-width: 400px; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.imagen.url
            )
        return 'No hay imagen'

    preview_imagen_grande.short_description = 'Preview de Imagen'

    def tiene_url(self, obj):
        """Indica si tiene URL externa"""
        if obj.url_fuente:
            return format_html(
                '<a href="{}" target="_blank" style="color: green;">✓ Ver</a>',
                obj.url_fuente
            )
        return format_html('<span style="color: gray;">✗ Local</span>')

    tiene_url.short_description = 'URL Externa'

    def contador_palabras(self, obj):
        """Cuenta palabras del contenido"""
        if obj.contenido:
            palabras = len(obj.contenido.split())
            return format_html(
                '<span style="font-weight: bold; color: #0066cc;">{} palabras</span>',
                palabras
            )
        return '0 palabras'

    contador_palabras.short_description = 'Longitud del Artículo'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
