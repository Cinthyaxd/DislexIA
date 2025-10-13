from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import re

# Importar constantes
from .constants import (
    GENERO_CHOICES,
    ROL_CHOICES,
    CLASIFICACION_RIESGO_CHOICES,
    EDAD_MIN,
    EDAD_MAX,
    INDICE_RIESGO_MIN,
    INDICE_RIESGO_MAX,
    CONFIANZA_MIN,
    CONFIANZA_MAX,
    DEFAULTS
)

class Nino(models.Model):
    """Modelo para almacenar información de los niños evaluados"""
    
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    edad = models.PositiveIntegerField(
        validators=[MinValueValidator(EDAD_MIN), MaxValueValidator(EDAD_MAX)],
        verbose_name="Edad"
    )
    imagen = models.ImageField(
        upload_to='ninos/', 
        verbose_name="Imagen",
        help_text="Imagen del niño (opcional)",
        # default='ninos/default_child_image.png',
        null=True,
        blank=True
        )
    genero = models.CharField(
        max_length=20, 
        choices=GENERO_CHOICES,
        verbose_name="Género"
    )
    idioma_nativo = models.CharField(max_length=50, verbose_name="Idioma Nativo")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    activo = models.BooleanField(default=DEFAULTS['nino_activo'], verbose_name="Activo")
    
    class Meta:
        verbose_name = "Niño"
        verbose_name_plural = "Niños"
        ordering = ['-fecha_registro']
        
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

# Modelo de usuario personalizado usando AbstractUser de Django
class Profesional(AbstractUser):
    """Modelo para profesionales que validan las evaluaciones"""
    
    # Campos adicionales (username, email, password, first_name, last_name ya vienen de AbstractUser)
    nombres = models.CharField(max_length=100, verbose_name="Nombres", blank=True)
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos", blank=True)
    imagen = models.ImageField(
        upload_to='profesionales/',
        verbose_name="Imagen",
        help_text="Imagen del profesional (opcional)",
        null=True,
        blank=True
    )
    especialidad = models.CharField(max_length=100, verbose_name="Especialidad", blank=True)
    numero_licencia = models.CharField(max_length=100, unique=True, verbose_name="Número de Licencia", null=True, blank=True)
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default=DEFAULTS['profesional_rol'],
        verbose_name="Rol"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    ultimo_acceso = models.DateTimeField(null=True, blank=True, verbose_name="Último Acceso")
    # El campo 'activo' ya viene como 'is_active' en AbstractUser
    
    # Usar email como campo de autenticación
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = "Profesional"
        verbose_name_plural = "Profesionales"
        ordering = ['-fecha_registro']
        
    def __str__(self):
        if self.nombres and self.apellidos:
            return f"{self.nombres} {self.apellidos}"
        return self.username
    
    @property
    def nombre_completo(self):
        if self.nombres and self.apellidos:
            return f"{self.nombres} {self.apellidos}"
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

class ReporteIA(models.Model):
    """Modelo para almacenar reportes generados por IA"""
    
    # Relación con evaluación (se importará desde games)
    evaluacion = models.OneToOneField(
        'games.Evaluacion',
        on_delete=models.CASCADE,
        related_name='reporte_ia',
        verbose_name="Evaluación"
    )
    
    indice_riesgo = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(INDICE_RIESGO_MIN), MaxValueValidator(INDICE_RIESGO_MAX)],
        verbose_name="Índice de Riesgo"
    )
    clasificacion_riesgo = models.CharField(
        max_length=20,
        choices=CLASIFICACION_RIESGO_CHOICES,
        verbose_name="Clasificación de Riesgo"
    )
    confianza_prediccion = models.PositiveIntegerField(
        validators=[MinValueValidator(CONFIANZA_MIN), MaxValueValidator(CONFIANZA_MAX)],
        verbose_name="Confianza de Predicción (%)"
    )
    caracteristicas_json = models.JSONField(
        verbose_name="Características (JSON)",
        help_text="Datos estructurados de las características analizadas"
    )
    recomendaciones = models.TextField(verbose_name="Recomendaciones")
    metricas_relevantes = models.JSONField(
        verbose_name="Métricas Relevantes",
        help_text="Métricas clave del análisis"
    )
    fecha_generacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Generación")
    
    class Meta:
        verbose_name = "Reporte IA"
        verbose_name_plural = "Reportes IA"
        ordering = ['-fecha_generacion']
        
    def __str__(self):
        return f"Reporte IA - {self.evaluacion} ({self.clasificacion_riesgo})"

class ValidacionProfesional(models.Model):
    """Modelo para validaciones realizadas por profesionales"""
    
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name='validaciones',
        verbose_name="Profesional"
    )
    evaluacion = models.OneToOneField(
        'games.Evaluacion',
        on_delete=models.CASCADE,
        related_name='validacion_profesional',
        verbose_name="Evaluación"
    )
    
    riesgo_confirmado = models.BooleanField(verbose_name="Riesgo Confirmado")
    indice_ajustado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(INDICE_RIESGO_MIN), MaxValueValidator(INDICE_RIESGO_MAX)],
        verbose_name="Índice Ajustado"
    )
    diagnostico_final = models.TextField(verbose_name="Diagnóstico Final")
    notas_clinicas = models.TextField(blank=True, verbose_name="Notas Clínicas")
    plan_tratamiento = models.TextField(blank=True, verbose_name="Plan de Tratamiento")
    requiere_seguimiento = models.BooleanField(default=DEFAULTS['requiere_seguimiento'], verbose_name="Requiere Seguimiento")
    fecha_validacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Validación")
    
    class Meta:
        verbose_name = "Validación Profesional"
        verbose_name_plural = "Validaciones Profesionales"
        ordering = ['-fecha_validacion']
        
    def __str__(self):
        return f"Validación - {self.evaluacion} por {self.profesional}"

class Cita(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='citas')
    nombre_paciente = models.CharField(max_length=200, verbose_name="Nombre del Paciente")
    foto_paciente = models.ImageField(upload_to='pacientes/', null=True, blank=True, verbose_name="Foto del Paciente")
    fecha = models.DateField(verbose_name="Fecha de la Cita")
    hora = models.TimeField(verbose_name="Hora de la Cita")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas adicionales")
    completada = models.BooleanField(default=False, verbose_name="Completada")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f"{self.nombre_paciente} - {self.fecha} {self.hora}"

class Video(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    codigo_embed = models.TextField(
        help_text="Pega el código completo de iframe que te da Youtube."
    )
    duracion = models.CharField(max_length=20, blank=True, null=True, help_text="Ej: 10:30")
    fecha_publicacion= models.DateField(blank=True, null=True)
    creado_por= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self):
        return self.titulo

    def get_embed_code(self):
        """
        Limpia y valida el código embed.
        Acepta tanto el iframe completo como solo la URL
        """
        codigo = self.codigo_embed.strip()

        # Si ya es un iframe, lo devuelve limpio
        if '<iframe' in codigo.lower():
            # Asegurarse de que tenga las clases responsive de Bootstrap
            if 'class=' not in codigo:
                codigo = codigo.replace('<iframe', '<iframe class="w-100 h-100"')
            return codigo

        # Si es solo una URL, crear el iframe
        if 'youtube.com' in codigo or 'youtu.be' in codigo:
            video_id = self.extract_video_id(codigo)
            if video_id:
                return f'''<iframe class="w-100 h-100" 
                    src="https://www.youtube.com/embed/{video_id}" 
                    title="{self.titulo}"
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                    referrerpolicy="strict-origin-when-cross-origin" 
                    allowfullscreen>
                </iframe>'''

        return codigo

    def extract_video_id(self, url):
        """Extrae el ID del video de cualquier formato de URL de YouTube"""
        patterns = [
            r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'youtu\.be/([a-zA-Z0-9_-]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_thumbnail(self):
        """Obtiene la URL de la miniatura del video"""
        video_id = self.extract_video_id(self.codigo_embed)
        if video_id:
            return f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
        return None
class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    descripcion = models.TextField()
    url_descarga = models.URLField(blank=True, null=True, help_text="Link de descarga o vista previa")
    isbn = models.CharField(max_length=20, blank=True, null=True)
    año_publicacion = models.IntegerField(blank=True, null=True)
    portada = models.ImageField(upload_to='libros/', blank=True, null=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'

    def __str__(self):
        return f"{self.titulo} - {self.autor}"


class Enlace(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    url = models.URLField()
    categoria = models.CharField(max_length=100, blank=True, null=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Enlace'
        verbose_name_plural = 'Enlaces'

    def __str__(self):
        return self.titulo


class Articulo(models.Model):
    titulo = models.CharField(max_length=200)
    resumen = models.TextField()
    contenido = models.TextField(blank=True, null=True)
    autor = models.CharField(max_length=200)
    url_fuente = models.URLField(blank=True, null=True, help_text="URL del artículo original")
    fecha_publicacion = models.DateField()
    imagen = models.ImageField(upload_to='articulos/', blank=True, null=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_publicacion']
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'

    def __str__(self):
        return self.titulo