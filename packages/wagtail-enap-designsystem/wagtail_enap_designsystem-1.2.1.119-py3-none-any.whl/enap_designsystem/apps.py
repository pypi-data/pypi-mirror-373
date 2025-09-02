from django.apps import AppConfig

class EnapDesignSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'enap_designsystem'

    def ready(self):
        import enap_designsystem.signals