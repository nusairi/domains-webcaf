"""
Authentication module for webcaf application.

This module provides OpenID Connect (OIDC) authentication backend and middleware
for enforcing authentication requirements across the application.
"""

import logging
import time
import uuid

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
import jwt
import requests

from webcaf.webcaf.utils import mask_email


class OIDCBackend(OIDCAuthenticationBackend):
    """
    Custom OIDC authentication backend for creating and updating local user representations.

    This backend extends mozilla_django_oidc's OIDCAuthenticationBackend to handle
    user creation and updates based on claims received from the OIDC provider during
    SSO authentication.

    Attributes:
        logger: Logger instance for tracking authentication events.
    """

    logger = logging.getLogger("OIDCBackend")

    def _get_identifier(self, claims):
        """
        Resolve a stable user identifier from OIDC claims.
        Prefer email, then preferred_username/upn, then sub.
        """
        return (
            claims.get("email")
            or claims.get("preferred_username")
            or claims.get("upn")
            or claims.get("sub")
        )

    def verify_claims(self, claims):
        """
        Allow Azure AD users that don't return an email claim.
        """
        if getattr(settings, "OIDC_DEBUG_CLAIMS", False):
            identifier = self._get_identifier(claims)
            aud = claims.get("aud")
            self.logger.warning(
                "OIDC claims debug: keys=%s aud=%s email=%s preferred_username=%s upn=%s identifier=%s",
                sorted(claims.keys()),
                aud,
                bool(claims.get("email")),
                bool(claims.get("preferred_username")),
                bool(claims.get("upn")),
                bool(identifier),
            )
        if getattr(settings, "OIDC_RELAX_CLAIMS", False):
            identifier = self._get_identifier(claims)
            aud = claims.get("aud")
            if aud is None:
                aud_ok = True
            elif isinstance(aud, list):
                aud_ok = settings.OIDC_RP_CLIENT_ID in aud
            else:
                aud_ok = aud == settings.OIDC_RP_CLIENT_ID
            return bool(identifier and aud_ok)

        if super().verify_claims(claims):
            return True

        # If email is missing, accept preferred_username/upn when the audience matches.
        if not claims.get("email"):
            identifier = self._get_identifier(claims)
            aud = claims.get("aud")
            if isinstance(aud, list):
                aud_ok = settings.OIDC_RP_CLIENT_ID in aud
            else:
                aud_ok = aud == settings.OIDC_RP_CLIENT_ID
            return bool(identifier and aud_ok)

        return False

    def _get_client_assertion(self):
        private_key = settings.OIDC_CLIENT_ASSERTION_PRIVATE_KEY
        if not private_key:
            raise ValueError("OIDC_CLIENT_ASSERTION_PRIVATE_KEY is not configured")
        # Handle escaped newlines if provided via env var.
        private_key = private_key.replace("\\n", "\n").replace("\r", "")
        if getattr(settings, "OIDC_DEBUG_CLAIMS", False):
            first_line = private_key.splitlines()[0] if private_key else ""
            self.logger.warning("OIDC client assertion key header: %s", first_line)
        now = int(time.time())
        payload = {
            "aud": settings.OIDC_OP_TOKEN_ENDPOINT,
            "iss": settings.OIDC_RP_CLIENT_ID,
            "sub": settings.OIDC_RP_CLIENT_ID,
            "exp": now + 300,
            "iat": now,
            "jti": uuid.uuid4().hex,
        }
        headers = {"typ": "JWT"}
        if settings.OIDC_CLIENT_ASSERTION_KID:
            headers["kid"] = settings.OIDC_CLIENT_ASSERTION_KID
        return jwt.encode(payload, private_key, algorithm=settings.OIDC_CLIENT_ASSERTION_ALG, headers=headers)

    def get_token(self, payload):
        if settings.OIDC_TOKEN_AUTH_METHOD != "private_key_jwt":
            return super().get_token(payload)

        data = dict(payload)
        data["client_id"] = settings.OIDC_RP_CLIENT_ID
        data["client_assertion_type"] = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
        data["client_assertion"] = self._get_client_assertion()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": settings.OIDC_USER_AGENT,
        }
        response = requests.post(settings.OIDC_OP_TOKEN_ENDPOINT, data=data, headers=headers, timeout=10)
        if getattr(settings, "OIDC_DEBUG_CLAIMS", False):
            self.logger.warning(
                "OIDC token error: status=%s body=%s",
                response.status_code,
                response.text,
            )
        response.raise_for_status()
        return response.json()

    def get_userinfo(self, access_token, id_token, payload):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": settings.OIDC_USER_AGENT,
        }
        response = requests.get(settings.OIDC_OP_USER_ENDPOINT, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def create_user(self, claims):
        """
        Create a new local user based on OIDC claims.

        Extracts user information from the OIDC claims and creates a Django user
        with email as the username. The user's first and last names are populated
        from the claims if available.

        Args:
            claims (dict): Dictionary of OIDC claims containing user information.
                Expected keys include 'email', 'given_name', 'family_name', and 'name'.

        Returns:
            User: The newly created Django user instance.

        Example claims structure:
            {
                'email': 'user@example.com',
                'given_name': 'John',
                'family_name': 'Doe',
                'name': 'John Doe'
            }
        """
        identifier = self._get_identifier(claims)
        self.logger.info(mask_email(f"Create user for {identifier}"))
        user = super().create_user(claims)
        if identifier and "@" in identifier:
            user.email = claims.get("email") or identifier
        user.username = identifier
        user.first_name = claims.get("given_name", claims.get("name", ""))
        user.last_name = claims.get("family_name", "")
        user.save()
        self.logger.info(mask_email(f"Created user {user.pk} {user.email}"))
        return user

    def update_user(self, user, claims):
        """
        Update an existing user's information based on OIDC claims.

        Synchronizes the local user record with any changes from the OIDC provider.
        This method is called during login to ensure user information remains up-to-date.

        Args:
            user (User): The Django user instance to update.
            claims (dict): Dictionary of OIDC claims containing updated user information.
                Expected keys include 'given_name', 'family_name', and 'name'.

        Returns:
            User: The updated Django user instance.

        Note:
            Falls back to existing user values if claims are missing or empty.
        """
        self.logger.info(mask_email(f"User  {user.id} {user.email} logged in to the system"))
        identifier = self._get_identifier(claims)
        if identifier and "@" in identifier:
            user.email = claims.get("email") or identifier
        user.username = identifier or user.username
        user.first_name = claims.get("given_name", user.first_name) or claims.get("name", user.first_name)
        user.last_name = claims.get("family_name", user.last_name)
        user.save()
        return user


class LoginRequiredMiddleware:
    """
    Django middleware that enforces authentication for all requests except exempted URLs.

    This middleware redirects unauthenticated users to the OIDC authentication
    initialization endpoint, with exceptions for authentication-related URLs,
    static assets, and public pages.

    Attributes:
        logger: Logger instance for tracking middleware events.
        exempt_url_prefixes (list): URL path prefixes that don't require authentication.
        exempt_exact_urls (list): Exact URL paths that don't require authentication.
    """

    logger = logging.getLogger("LoginRequiredMiddleware")

    def __init__(self, get_response):
        """
        Initialize the middleware with exempted URLs.

        Args:
            get_response (callable): The next middleware or view in the chain.
        """
        self.get_response = get_response
        self.exempt_url_prefixes = [
            reverse("oidc_authentication_init"),
            reverse("oidc_authentication_callback"),
            reverse("oidc_logout"),
            # Admin authentication is done separately
            "/admin/",
            # public pages and static assets
            "/assets/",
            "/static/",
            "/media",
            "/public/",
            "/session-expired/",
            "/logout/",
        ]
        login_url = getattr(settings, "LOGIN_URL", "")
        if login_url and login_url not in self.exempt_url_prefixes:
            self.exempt_url_prefixes.append(login_url)
        self.exempt_exact_urls = [
            # index page
            "/"
        ]

    def __call__(self, request):
        """
        Process the request and enforce authentication requirements.

        Checks if the user is authenticated or if the requested path is exempted.
        Unauthenticated requests to non-exempted paths are redirected to the
        OIDC authentication flow.

        Args:
            request: Django HTTP request object.

        Returns:
            HttpResponse: Either the response from the next middleware/view or
                a redirect to the authentication initialization endpoint.
        """
        if (
            not any(request.path.startswith(url) for url in self.exempt_url_prefixes)
            and request.path not in self.exempt_exact_urls
        ):
            # you need to be authenticated to access any page outside the non secure list
            if not request.user.is_authenticated or request.user.is_anonymous:
                if request.path == reverse("verify-2fa-token") and request.method == "POST":
                    # The only possibility of this happening is that the session timing out
                    # while the user is trying to submit the 2FA token.
                    # So, reset the flow and get a new token
                    self.logger.info("Session expired while submitting 2FA token. Redirecting to session-expired")
                    return redirect("session-expired")
                self.logger.debug("Force authentication for %s", request.path)
                if getattr(settings, "SSO_MODE", "external").lower() == "none":
                    return redirect(settings.LOGIN_URL)
                return redirect("oidc_authentication_init")

            # If the user is authenticated, check if they're verified'
            if not settings.ENABLED_2FA:
                # handle the local dev for when 2FA is disabled
                self.logger.debug("Allowing access for local development or testing")
                return self.get_response(request)
            elif not request.user.is_verified():
                if not request.user.is_staff:
                    # No varification support yet for the staff users
                    # Allow access to the verification page
                    if request.path == reverse("verify-2fa-token"):
                        return self.get_response(request)
                    # Any other unverified user access to urls is redirected to the verification page
                    verify_url = reverse("verify-2fa-token")
                    return redirect(verify_url)

        self.logger.debug(
            "Allowing access to %s, authenticated %s is_staff %s",
            request.path,
            request.user.is_authenticated,
            request.user.is_staff,
        )
        return self.get_response(request)
