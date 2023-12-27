from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "news"
    
    # news 앱의 signals.py 임포트
    def ready(self):
        import news.signals