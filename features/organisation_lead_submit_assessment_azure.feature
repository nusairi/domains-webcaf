Feature: Organisation lead can submit assessment (Azure)

  # Prereqs:
  # - Azure Entra test account exists and has no MFA.
  # - User has a UserProfile with Organisation lead role in the target organisation.
  # - A draft assessment exists for the system name below and is complete enough to submit.

  Background:
    Given the application is running
    And cookies have been "accepted"
    And azure seed assessment exists
    And the user logs in with azure oidc

  Scenario: Organisation lead can submit a completed assessment (Azure)
    Then page title contains "My account"
    And click link containing text "draft self-assessment"
    And click link in table row containing value "System 1" with text "View"
    And click link with text "Complete the full self-assessment"
    And click button with text "Save and send for review"
    Then navigate to page "/my-account"
    And link with text "View self-assessments sent for review"
