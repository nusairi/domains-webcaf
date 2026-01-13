# GOV.UK One Login integration (sandbox)

This document describes how the app integrates with GOV.UK One Login in the sandbox environment.
It is written for engineers and operators who need to configure or troubleshoot the integration.

## High-level flow

1. User clicks Sign in in the app.
2. The app sends an OAuth2 /authorize request to GOV.UK One Login.
3. GOV.UK One Login authenticates the user and redirects back to the app callback URL.
4. The app exchanges the authorization code for tokens using private_key_jwt.
5. The app uses the access token to call /userinfo and maps the user to a local profile.

## Required settings (Terraform vars)

These are set via `*.tfvars` or `TF_VAR_...` environment variables.
Do not commit real values to git.

Required:
- `oidc_client_id`
- `oidc_client_secret`
- `oidc_client_assertion_private_key`

Recommended:
- `oidc_client_assertion_kid` (only if your public key includes a matching kid)

Sandbox example values (use your own endpoints if they differ):

```
sso_mode = "external"

# GOV.UK One Login integration endpoints
oidc_op_authorization_endpoint = "https://oidc.integration.account.gov.uk/authorize"
oidc_op_token_endpoint         = "https://oidc.integration.account.gov.uk/token"
oidc_op_user_endpoint          = "https://oidc.integration.account.gov.uk/userinfo"
oidc_op_jwks_endpoint           = "https://oidc.integration.account.gov.uk/.well-known/jwks.json"
oidc_op_logout_endpoint         = "https://oidc.integration.account.gov.uk/logout"

# Scopes and token settings
oidc_rp_scopes         = "openid email phone"
oidc_rp_sign_algo      = "ES256"   # ID token signing algorithm from One Login
oidc_token_auth_method = "private_key_jwt"
oidc_client_assertion_alg = "RS256" # client assertion signing algorithm

# Required User-Agent for One Login
# (include a real URL you control)
oidc_user_agent = "webcaflocalpocsbx/1.0 (https://<your-sandbox-fqdn>)"
```

## Key pair requirements

GOV.UK One Login uses public key cryptography for the client assertion.
The app signs a JWT with your private key (RS256) and includes it in the /token request.

Key requirements that worked in this integration:
- RSA 2048 key pair
- Upload the public key to One Login
- Store the private key in Key Vault as a secret

### Generate RSA key pair

If you have OpenSSL installed:

```
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

One Login accepted the PEM public key directly.

If your JWT library expects PKCS1 format for signing, convert the private key:

```
openssl rsa -in private_key.pem -traditional -out private_key_pkcs1.pem
```

### Store the private key in Key Vault

Save the private key PEM as the secret `oidc-client-assertion-private-key`.
Terraform reads this secret and injects it into the app as `OIDC_CLIENT_ASSERTION_PRIVATE_KEY`.

## One Login admin tool configuration

In the One Login admin tool:
- Set Redirect URI to your app callback:
  `https://<app-fqdn>/oidc/callback/`
- Authentication method: `private_key_jwt`
- Upload the public key
- Scopes: `openid`, `email`, `phone` (or as required)

## Required HTTP header

GOV.UK One Login requires a non-empty User-Agent header.
The app sets `OIDC_USER_AGENT` and uses it for the /token and /userinfo requests.
If missing, One Login may return HTTP 403.

## Troubleshooting

Common errors and fixes:

- `invalid_client` / `Invalid signature in private_key_jwt`
  - The private key does not match the uploaded public key.
  - The app is signing with the wrong algorithm (RS256 required).
  - The key format is not parsable by the JWT library.

- 400 from /token with `invalid_request`
  - Mismatch between redirect URI and configured callback.
  - Missing required parameters in the token request.

- Login succeeds but user has no access
  - Ensure the user has a local UserProfile with the correct organisation and role.

## Secrets and repo safety

Do not commit any of these to git:
- `*.pem`, `*.key`, `*.jwk`, `*.jwks`
- `*.tfvars`
- Terraform state files

Use Key Vault for private keys and `TF_VAR_...` environment variables for sensitive values.
