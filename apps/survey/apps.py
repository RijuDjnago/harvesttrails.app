from django.apps import AppConfig


class SurveyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.survey'

    def ready(self):
        import apps.survey.signals
