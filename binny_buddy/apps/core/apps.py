from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "binny_buddy.apps.core"

    def ready(self):
        from django.conf import settings

        try:
            from binny_buddy.apps.core.models import BinnyUser, BinnyCollection

            default_user, _ = BinnyUser.objects.update_or_create(
                username=settings.BINNY_USER_USERNAME
            )
            BinnyCollection.objects.update_or_create(user=default_user)

        except:
            pass
