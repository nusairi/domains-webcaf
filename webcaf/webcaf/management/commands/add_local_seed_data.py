import sys

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from webcaf.webcaf.models import Assessment, Configuration, Organisation, System, UserProfile

SUPERUSER_NAME = "admin"
SUPERUSER_PASSWORD = "password"  # pragma: allowlist secret
SEED_USERS = [
    ("mhclg@A2zSoftwaresolutions.onmicrosoft.com", "organisation_lead"),
    ("mirali110@ymail.com", "organisation_user"),
]
ORG_NAME = "An Organisation"
SYSTEM_NAMES = ["Big System", "Little System"]
CONFIGS = [
    {
        "name": "25/26",
        "current_assessment_period": "2025/26",
        "assessment_period_end": "31 March 2026 11:59pm",
        "default_framework": "caf32",
    },
    {
        "name": "26/27",
        "current_assessment_period": "2026/27",
        "assessment_period_end": "31 March 2027 11:59pm",
        "default_framework": "caf32",
    },
]


class Command(BaseCommand):
    help = "Creates a superuser, standard user, organisation, and systems"

    def handle(self, *args, **options):
        if not Organisation.objects.exists():
            self.stdout.write(self.style.ERROR("Run python manage.py add_organisations before running this command"))
            sys.exit(1)

        if not User.objects.filter(username=SUPERUSER_NAME).exists():
            superuser = User.objects.create_superuser(
                username=SUPERUSER_NAME, email=f"{SUPERUSER_NAME}@admin.org", password=SUPERUSER_PASSWORD
            )

            UserProfile.objects.create(user=superuser)
            self.stdout.write(self.style.SUCCESS(f"Superuser '{SUPERUSER_NAME}' created"))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser '{SUPERUSER_NAME}' already exists"))

        organisation = Organisation.objects.first()

        for config in CONFIGS:
            Configuration.objects.get_or_create(
                name=config["name"],
                defaults={
                    "config_data": {
                        "current_assessment_period": config["current_assessment_period"],
                        "assessment_period_end": config["assessment_period_end"],
                        "default_framework": config["default_framework"],
                    }
                },
            )

        for system_name in SYSTEM_NAMES:
            _, sys_created = System.objects.get_or_create(name=system_name, organisation=organisation)
            if not sys_created:
                self.stdout.write(
                    self.style.WARNING(f"System '{system_name}' already exists for organisation '{ORG_NAME}'")
                )

        for email, role in SEED_USERS:
            user, created = User.objects.get_or_create(username=email, defaults={"email": email})
            if created:
                user.set_unusable_password()
                user.save()
                self.stdout.write(self.style.SUCCESS(f"User '{email}' created"))
            if not UserProfile.objects.filter(user=user).exists():
                UserProfile.objects.create(user=user, organisation=organisation, role=role)
                self.stdout.write(self.style.SUCCESS(f"UserProfile for '{email}' created"))
            else:
                self.stdout.write(self.style.WARNING(f"UserProfile for '{email}' already exists"))

        seed_owner = User.objects.filter(username=SEED_USERS[0][0]).first()
        if seed_owner:
            for system in System.objects.filter(organisation=organisation):
                Assessment.objects.get_or_create(
                    system=system,
                    assessment_period="2025/26",
                    status="draft",
                    defaults={
                        "framework": "caf32",
                        "caf_profile": "baseline",
                        "created_by": seed_owner,
                        "last_updated_by": seed_owner,
                        "review_type": "self_assessment",
                    },
                )
