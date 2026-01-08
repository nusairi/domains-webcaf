from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from webcaf.webcaf.models import Organisation, UserProfile


class Command(BaseCommand):
    help = "Create or update a user and attach an organisation profile."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="User email/username.")
        parser.add_argument("--organisation", required=True, help="Organisation name.")
        parser.add_argument(
            "--role",
            default="organisation_lead",
            help="UserProfile role (default: organisation_lead).",
        )
        parser.add_argument(
            "--create-organisation",
            action="store_true",
            help="Create the organisation if it does not exist.",
        )
        parser.add_argument(
            "--superuser",
            action="store_true",
            help="Grant Django superuser and staff.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        email = options["email"].strip()
        org_name = options["organisation"].strip()
        role = options["role"].strip()

        valid_roles = {choice[0] for choice in UserProfile.ROLE_CHOICES}
        if role not in valid_roles:
            raise CommandError(f"Invalid role '{role}'. Valid roles: {', '.join(sorted(valid_roles))}")

        try:
            org = Organisation.objects.get(name=org_name)
        except Organisation.DoesNotExist:
            if not options["create_organisation"]:
                raise CommandError(f"Organisation '{org_name}' does not exist. Use --create-organisation.")
            org = Organisation.objects.create(name=org_name)

        user, _ = User.objects.get_or_create(username=email, defaults={"email": email})
        if options["superuser"]:
            user.is_staff = True
            user.is_superuser = True
            user.save()

        profile, created = UserProfile.objects.get_or_create(
            user=user,
            organisation=org,
            defaults={"role": role},
        )
        if not created and profile.role != role:
            profile.role = role
            profile.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"UserProfile ready: user={user.username} organisation={org.name} role={profile.role}"
            )
        )
