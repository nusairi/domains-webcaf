import json
from pathlib import Path

from behave import given, step, then
from behave.runner import Context
from playwright.sync_api import expect

from features.util import exists_model, get_model, run_async_orm


@then('User model with email "{email}" should exist with "{user_role}" user role')
def check_user_with_profile_exists(context, email, user_role):
    from django.contrib.auth.models import User

    from webcaf.webcaf.models import UserProfile

    user_exists = exists_model(User, **{"email": email})

    # Assert that the user was found
    assert user_exists, f"User with email '{email}' was not found in the database."

    user = get_model(User, **{"email": email})
    user_profile = get_model(UserProfile, **{"user": user})
    assert user_profile.role == user_role


@then('User profile model with email "{email}" should not exist')
def check_user_does_not_exist(context, email):
    from django.contrib.auth.models import User

    from webcaf.webcaf.models import UserProfile

    user = get_model(User, **{"email": email})
    user_profile_exists = exists_model(UserProfile, **{"user": user})

    # Assert that the user was not found
    assert (
        not user_profile_exists
    ), f"User profile with email '{email}' was found in the database but should have been removed."


@then('check organisation "{org_name}" has type "{type}" and contact details "{name}" "{role}" and "{email}"')
def check_saved_org_has_expected_fields(context, org_name, type, name, role, email):
    from webcaf.webcaf.models import Organisation

    organisation = get_model(
        Organisation,
        **{
            "name": org_name,
        },
    )
    assert organisation.organisation_type == type, f"organisation  {org_name} type is not {type} as expected"
    assert organisation.contact_name == name, f"organisation {org_name} contact name is not {name} as expected"
    assert organisation.contact_role == role, f"organisation {org_name} contact role is not {role} as expected"
    assert organisation.contact_email == email, f"organisation {org_name} contact email is not {email} as expected"


@step('confirm the current assessment has expected data "{data_file_name}"')
def check_assessment_data(context: Context, data_file_name: str):
    """
    :type context: behave.runner.Context
    """
    from webcaf.webcaf.models import Assessment

    with open(Path(__file__).parent.parent / "data" / data_file_name, "r") as f:
        json_data = f.read()
        assert json.loads(json_data) == get_model(Assessment, id=context.current_assessment_id).assessments_data


@step('confirm current assessment is in "{expected_state}" state')
def confirm_assessment_status(context: Context, expected_state: str):
    """
    :type context: behave.runner.Context
    """
    from webcaf.webcaf.models import Assessment

    assessment = get_model(Assessment, id=context.current_assessment_id, last_updated_by__email=context.current_email)
    assessment.state = expected_state
    page = context.page
    # Confirm we have the correct reference displayed on the page.
    expect(page.locator("strong#reference_number").filter(has_text=assessment.reference)).to_be_visible()


@given("azure seed assessment exists")
def seed_azure_assessment(context: Context):
    """
    Create or update seed data without deleting anything.
    Override defaults with -D arguments, e.g.:
      -D seed_org_name="Bristol City Council"
      -D seed_org_type="Other"
      -D seed_system_name="System 1"
      -D seed_user_email="other@example.gov.uk"
      -D seed_user_role="Organisation lead"
      -D seed_assessment_period="25/26"
      -D seed_status="draft"
      -D seed_caf_profile="enhanced"
      -D seed_framework="caf32"
      -D seed_review_type="peer_review"
      -D seed_data_file="alice_completed_assessment.json"
    """
    from django.contrib.auth.models import User

    from webcaf.webcaf.models import Assessment, Organisation, System, UserProfile

    userdata = context.config.userdata
    org_name = userdata.get("seed_org_name", "Ministry of Agriculture")
    org_type_input = userdata.get("seed_org_type", "Ministerial department")
    system_name = userdata.get("seed_system_name", "System 1")
    user_email = userdata.get("seed_user_email", "other@example.gov.uk")
    user_role_input = userdata.get("seed_user_role", "Organisation lead")
    period = userdata.get("seed_assessment_period", "25/26")
    status = userdata.get("seed_status", "draft")
    caf_profile = userdata.get("seed_caf_profile", "enhanced")
    framework = userdata.get("seed_framework", "caf32")
    review_type = userdata.get("seed_review_type", "peer_review")
    data_file = userdata.get("seed_data_file", "alice_completed_assessment.json")

    def resolve_org_type(value: str) -> str:
        org_type_ids = {choice[0] for choice in Organisation.ORGANISATION_TYPE_CHOICES}
        if value in org_type_ids:
            return value
        return Organisation.get_type_id(value) or "other"

    def resolve_role(value: str) -> str:
        role_ids = {choice[0] for choice in UserProfile.ROLE_CHOICES}
        if value in role_ids:
            return value
        return UserProfile.get_role_id(value) or "organisation_lead"

    def load_assessment_data() -> dict:
        if not data_file:
            return {}
        file_path = Path(__file__).parent.parent / "data" / data_file
        if not file_path.exists():
            return {}
        with open(file_path, "r") as f:
            return json.loads(f.read())

    def seed():
        org_type = resolve_org_type(org_type_input)
        role = resolve_role(user_role_input)
        assessments_data = load_assessment_data()

        organisation, _ = Organisation.objects.get_or_create(name=org_name)
        if organisation.organisation_type != org_type:
            organisation.organisation_type = org_type
            organisation.save(update_fields=["organisation_type"])

        system, _ = System.objects.get_or_create(name=system_name, organisation=organisation)

        user, _ = User.objects.get_or_create(username=user_email, defaults={"email": user_email})
        if user.email != user_email:
            user.email = user_email
            user.save(update_fields=["email"])

        profile, _ = UserProfile.objects.get_or_create(user=user, organisation=organisation, defaults={"role": role})
        if profile.organisation_id != organisation.id or profile.role != role:
            profile.organisation = organisation
            profile.role = role
            profile.save(update_fields=["organisation", "role"])

        assessment, created = Assessment.objects.get_or_create(
            system=system,
            assessment_period=period,
            status=status,
            defaults={
                "caf_profile": caf_profile,
                "review_type": review_type,
                "framework": framework,
                "assessments_data": assessments_data,
                "created_by": user,
                "last_updated_by": user,
            },
        )
        if not created:
            assessment.caf_profile = caf_profile
            assessment.review_type = review_type
            assessment.framework = framework
            assessment.assessments_data = assessments_data
            assessment.created_by = user
            assessment.last_updated_by = user
            assessment.save()

    run_async_orm(seed)


@then(
    'confirm initial assessment has system "{system_name}" caf profile "{caf_profile}" and review type "{review_type}"'
)
def check_assessment_initial_setup(context: Context, system_name: str, caf_profile: str, review_type: str):
    """
    checks the initial persisted assessment has the expected values for system, caf profile
    and review type
    """
    from webcaf.webcaf.models import Assessment, System

    assessment = get_model(Assessment, id=context.current_assessment_id)
    system = get_model(System, id=assessment.system_id)
    assert system.name == system_name, f"System name persisted as '{system.name}' not expect '{system_name}'"
    assert (
        assessment.caf_profile == caf_profile
    ), f"Caf profile  persisted as '{assessment.caf_profile}' not expect '{caf_profile}'"
    assert (
        assessment.review_type == review_type
    ), f"Caf profile  persisted as '{assessment.review_type}' not expect '{review_type}'"
