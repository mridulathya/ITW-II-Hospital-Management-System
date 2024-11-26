from django.apps import AppConfig


class MridulConfig(AppConfig):
    name = 'mridul'
    def ready(self):
        import mridul.signals
