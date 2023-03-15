from django.apps import AppConfig


class ToolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tool'
    
    def ready(self) -> None:
        import tool.signals    
    