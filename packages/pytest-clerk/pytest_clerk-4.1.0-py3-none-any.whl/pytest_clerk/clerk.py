import logging
import re
from contextlib import suppress
from time import sleep

import httpx
import pytest
from decouple import UndefinedValueError, config
from limits import RateLimitItemPerSecond, storage, strategies
from tenacity import retry, stop_after_attempt, wait_random_exponential

logger = logging.getLogger(__name__)


class ClerkRateLimiter:
    """This class manages all of the rate limits for the various API endpoints of Clerk
    for both the front end and back end APIs.
    """

    def __init__(self):
        """Initialize all of the rate limits."""
        # Use an instance of an object to specify the "no limits" default. This is so
        # that we don't pass any `is None` checks when the default is specified as no
        # limits.
        self.no_limit = object()
        self.backend_rate_limits = {
            # 19 requests per 10 seconds.
            "POST": {r"/v1/users": RateLimitItemPerSecond(amount=19, multiples=10)},
            # No rate limits.
            "GET": {r"/v1/jwks": self.no_limit},
            # 99 requests per 10 seconds.
            "DEFAULT": RateLimitItemPerSecond(amount=99, multiples=10),
        }
        self.frontend_rate_limits = {
            "POST": {
                # 2 requests per 10 seconds.
                r"/v1/client/sign_ins/(?P<sign_in_id>.*?)/attempt_first_factor": RateLimitItemPerSecond(
                    amount=2, multiples=10
                ),
                # 2 requests per 10 seconds.
                r"/v1/client/sign_ins/(?P<sign_in_id>.*?)/attempt_second_factor": RateLimitItemPerSecond(
                    amount=2, multiples=10
                ),
                # 2 requests per 10 seconds.
                r"/v1/client/sign_ups/(?P<sign_up_id>.*?)/attempt_verification": RateLimitItemPerSecond(
                    amount=2, multiples=10
                ),
                # 4 requests per 10 seconds.
                r"/v1/client/sign_ins": RateLimitItemPerSecond(amount=4, multiples=10),
                # 4 requests per 10 seconds.
                r"/v1/client/sign_ups": RateLimitItemPerSecond(amount=4, multiples=10),
            }
        }
        self.storage = storage.MemoryStorage()
        self.strategy = strategies.FixedWindowRateLimiter(self.storage)

    def get_rate_limit_item(self, request, rate_limits):
        """Return the found rate limit item and namespace to use when checking the rate
        limit for this request.

        The returned namespace should be used as the unique identifier in order to group
        the various rate limit checks.

        If there is no rate limit specified, the rate limit item will be `None`. If
        there is a rate limit specified, but it is unlimited, the rate limit item will
        be `self.no_limit`.
        """
        path = request.url.path
        method = request.method
        host = request.url.host

        logger.debug(
            "Searching for rate limit for method %s, host %s, and path %s.",
            method,
            host,
            path,
        )

        rate_limit_item = None
        namespace = None

        # Check all the configured rate limits for the method.
        method_limits = rate_limits.get(method, {})
        for path_regex, rate_limit in method_limits.items():
            logger.debug(
                "Checking if regex %s and rate limit %s matches for method %s, host %s,"
                " and path %s.",
                path_regex,
                rate_limit,
                method,
                host,
                path,
            )

            if re.match(path_regex, path):
                rate_limit_item = rate_limit
                namespace = f"{host}:{path}:{method}"
                break

        # If we didn't get a limit for the method + path, try the default for that
        # method.
        if rate_limit_item is None:
            logger.debug(
                "No rate limit found for method %s, host %s, and path %s. Trying"
                " default rate limit for method %s and host %s.",
                method,
                host,
                path,
                method,
                host,
            )
            rate_limit_item = method_limits.get("DEFAULT")
            namespace = f"{host}:{method}"

        # If there was no default limit for the method, try the overall default.
        if rate_limit_item is None:
            logger.debug(
                "No rate limit found for method %s and host %s. Trying global default.",
                method,
                host,
            )
            rate_limit_item = rate_limits.get("DEFAULT")
            namespace = host

        logger.debug(
            "Found rate limit %s with namespace %s for method %s, host %s, and path"
            " %s.",
            rate_limit_item,
            namespace,
            method,
            host,
            path,
        )
        return rate_limit_item, namespace

    def rate_limit_hook(self, request):
        """Check the requeste URL and hit the appropriate rate limit."""
        # Get the rate limit for the request.
        if request.url.host == "api.clerk.com":
            logger.debug("Checking back end rate limits for request %s.", request)
            rate_limit_item, namespace = self.get_rate_limit_item(
                request=request, rate_limits=self.backend_rate_limits
            )
        else:
            logger.debug("Checking front end rate limits for request %s.", request)
            rate_limit_item, namespace = self.get_rate_limit_item(
                request=request, rate_limits=self.frontend_rate_limits
            )

        # If the rate limit was specified as unlimited, do nothing.
        if rate_limit_item is self.no_limit:
            logger.debug("The rate limit is unlimited for request %s.", request)
            return

        # If there is no rate limit, do nothing.
        if rate_limit_item is None:
            logger.debug("There was no rate limit found for request %s.", request)
            return

        logger.debug("The rate limit is %s for request %s.", rate_limit_item, request)

        # Check if we hit the rate limit.
        while not self.strategy.hit(rate_limit_item, namespace):
            logger.info(
                "Hit rate limit for namespace %s while making request %s.",
                namespace,
                request,
            )
            sleep(1)


@pytest.fixture(scope="session")
def clerk_rate_limiter():
    """Return an instance of the Clerk rate limiter for use with HTTPX request hooks."""
    return ClerkRateLimiter()


@pytest.fixture(scope="session")
def clerk_secret_key(request):
    """Retrieve the clerk secret key to use for the test.

    If using AWS Secrets Manager, the CLERK_SECRET_ID variable be set to the ID of the
    SecretsManager secret that contains the Clerk secret key. This can be set in a .env
    file or an environment variable.

    If not using AWS Secrets Manager, the CLERK_SECRET_KEY variable must be set to the
    value of the clerk secret key to use. This can be set in a .env file or an
    environment variable.
    """
    with suppress(UndefinedValueError, pytest.FixtureLookupError):
        secretsmanager_client = request.getfixturevalue("secretsmanager_client")
        return secretsmanager_client.get_secret_value(
            SecretId=config("CLERK_SECRET_ID")
        )["SecretString"]

    with suppress(UndefinedValueError):
        return config("CLERK_SECRET_KEY")

    pytest.skip(
        reason="Neither CLERK_SECRET_ID nor CLERK_SECRET_KEY was found in the"
        " environment or a .env file and is required for this test. If CLERK_SECRET_ID"
        " is set, and you're still seeing this message, ensure the aws extra"
        " dependencies are installed."
    )


@pytest.fixture(scope="session")
def clerk_backend_httpx_client(clerk_secret_key, clerk_rate_limiter):
    """A fixture that creates a HTTPX Client instance with the required backend Clerk
    Authorization headers set and the correct Clerk backend API base URL.

    Please be mindful of the Clerk API rate limits:
    https://clerk.com/docs/reference/rate-limits
    """
    client = httpx.Client(
        headers={"Authorization": f"Bearer {clerk_secret_key}"},
        base_url="https://api.clerk.com/v1",
        event_hooks={"request": [clerk_rate_limiter.rate_limit_hook]},
        timeout=10,
    )

    yield client

    client.close()


@pytest.fixture(scope="session")
def clerk_frontend_api_url():
    """This fixture returns the value of the CLERK_FRONTEND_URL variable and is used to
    make calls to the Clerk frontend API.

    CLERK_FRONTEND_URL can be set via environment variables or in a .env file. This URL
    can be found under Developers -> API Keys -> Show API URLs.
    """
    with suppress(UndefinedValueError):
        return config("CLERK_FRONTEND_URL")

    pytest.skip(
        reason="CLERK_FRONTEND_URL was not found in the environment or a .env file and"
        " is required for this test."
    )


@pytest.fixture(scope="session")
def clerk_frontend_httpx_client(clerk_frontend_api_url, clerk_rate_limiter):
    """This fixture returns a function that creates an HTTPX Client instance with the
    required frontend Clerk Authorization parameters set and the correct Clerk frontend
    API base URL.

    This requires the CLERK_FRONTEND_URL variable to be set. CLERK_FRONTEND_URL can be
    set via environment variables or in a .env file. This URL can be found under
    Developers -> API Keys -> Show API URLs.
    """
    with httpx.Client(base_url=f"{clerk_frontend_api_url}/v1", timeout=10) as client:
        result = client.post(url="/dev_browser")

    result.raise_for_status()

    client = httpx.Client(
        params={"__dev_session": result.json()["token"]},
        base_url=f"{clerk_frontend_api_url}/v1",
        event_hooks={"request": [clerk_rate_limiter.rate_limit_hook]},
        timeout=10,
    )

    yield client

    client.close()


@pytest.fixture
def clerk_delete_org(clerk_backend_httpx_client):
    """This fixture provides a function to delete an organization given an org ID. Any
    additional kwargs are passed through to the httpx.Client.delete call.

    The API documentation for this call can be found below:
    https://clerk.com/docs/reference/backend-api/tag/Organizations#operation/DeleteOrganization
    """

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        reraise=True,
    )
    def _inner(org_id, **kwargs):
        """Delete the org with the given org ID. Any additional kwargs are passed
        through to the httpx.Client.delete call.

        This will retry rate limit errors.

        The API documentation for this call can be found below:
        https://clerk.com/docs/reference/backend-api/tag/Organizations#operation/DeleteOrganization
        """
        result = clerk_backend_httpx_client.delete(
            url=f"/organizations/{org_id}", **kwargs
        )
        # Ignore 404 errors indicating it was already deleted. Raise other errors.
        if result.status_code != httpx.codes.NOT_FOUND:
            result.raise_for_status()

        return result

    return _inner


@pytest.fixture
def clerk_create_org(clerk_backend_httpx_client, clerk_delete_org):
    """This fixture provides a function to create an organization that will
    automatically be deleted on fixture teardown.

    The API documentation for this call can be found below:
    https://clerk.com/docs/reference/backend-api/tag/Organizations#operation/CreateOrganization
    """
    orgs_to_delete = []

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        reraise=True,
    )
    def _inner(organization_data, **kwargs):
        """This function creates an Organization with the provided organization_data,
        and saves the reference to delete it at a later time. All additional kwargs are
        passed through to the httpx.Client.post call.

        This will retry rate limit errors.

        The API documentation for this call can be found below:
        https://clerk.com/docs/reference/backend-api/tag/Organizations#operation/CreateOrganization
        """
        result = clerk_backend_httpx_client.post(
            url="/organizations", json=organization_data, **kwargs
        )
        result.raise_for_status()
        result = result.json()
        orgs_to_delete.append(result)
        return result

    yield _inner

    # Now remove all of the orgs.
    for org in orgs_to_delete:
        clerk_delete_org(org_id=org["id"])


@pytest.fixture
def clerk_update_org(clerk_backend_httpx_client):
    """This fixture provides a function to update an organization with the provided
    `organization_data`. All additional kwargs are passed through to the
    httpx.Client.patch call.

    The API documentation for this call can be found below:
    https://clerk.com/docs/reference/backend-api/tag/Organizations#operation/UpdateOrganization
    """

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        reraise=True,
    )
    def _inner(org_id_or_slug, organization_data, **kwargs):
        """This function attempts to update an organization with the provided
        `organization_data`. All additional kwargs are passed through to the
        httpx.Client.patch call.

        This will retry rate limit errors.

        The API documentation for this call can be found below:
        https://clerk.com/docs/reference/backend-api/tag/Organizations#operation/UpdateOrganization
        """
        result = clerk_backend_httpx_client.patch(
            url=f"/organizations/{org_id_or_slug}", json=organization_data, **kwargs
        )
        result.raise_for_status()
        return result.json()

    yield _inner


@pytest.fixture
def clerk_get_org(clerk_backend_httpx_client):
    """This fixture provides a function to get an organization by its ID or slug. All
    additional kwargs are passed through to the httpx.Client.get call.

    The API documentation for this call can be found below:
    https://clerk.com/docs/reference/backend-api/tag/Organizations#operation/GetOrganization
    """

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        reraise=True,
    )
    def _inner(org_id_or_slug, **kwargs):
        """This function attempts to find and return the org with the given ID or slug.
        All additional kwargs are passed through to the httpx.Client.get call.

        This will retry rate limit errors.

        The API documentation for this call can be found below:
        https://clerk.com/docs/reference/backend-api/tag/Organizations#operation/GetOrganization
        """
        result = clerk_backend_httpx_client.get(
            url=f"/organizations/{org_id_or_slug}", **kwargs
        )
        result.raise_for_status()
        return result.json()

    yield _inner


@pytest.fixture
def clerk_delete_user(clerk_backend_httpx_client):
    """This fixture provides a function to delete a user given the user ID. All
    additional kwargs are passed through to the httpx.Client.delete call.

    The API documentation for this call can be found below:
    https://clerk.com/docs/reference/backend-api/tag/Users#operation/DeleteUser
    """

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        reraise=True,
    )
    def _inner(user_id, **kwargs):
        """Delete the user with the given user ID. All additional kwargs are passed
        through to the httpx.Client.delete call.

        This will retry rate limit errors.

        The API documentation for this call can be found below:
        https://clerk.com/docs/reference/backend-api/tag/Users#operation/DeleteUser
        """
        result = clerk_backend_httpx_client.delete(url=f"/users/{user_id}", **kwargs)
        # Ignore 404 errors indicating it was already deleted. Raise other errors.
        if result.status_code != httpx.codes.NOT_FOUND:
            result.raise_for_status()

        return result

    return _inner


@pytest.fixture
def clerk_create_user(clerk_backend_httpx_client, clerk_delete_user):
    """This fixture provides a method to create a user that will automatically
    be deleted on fixture teardown.

    The API documentation for this call can be found below:
    https://clerk.com/docs/reference/backend-api/tag/Users#operation/CreateUser
    """
    users_to_delete = []

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        reraise=True,
    )
    def _inner(user_data, **kwargs):
        """This function uses user_data to create a User with the backend API, and
        saves the reference to delete it at a later time. All other kwargs are passed
        through to the httpx.Client.post call.

        This will retry rate limit errors.

        The API documentation for this call can be found below:
        https://clerk.com/docs/reference/backend-api/tag/Users#operation/CreateUser
        """
        result = clerk_backend_httpx_client.post(url="/users", json=user_data, **kwargs)
        result.raise_for_status()
        result = result.json()
        users_to_delete.append(result)
        return result

    yield _inner

    # Now remove all of the users.
    for user in users_to_delete:
        clerk_delete_user(user_id=user["id"])


@pytest.fixture
def clerk_update_user_metadata(clerk_backend_httpx_client):
    """This fixture provides a function to update a user's metadata given the user ID.
    All additional kwargs are passed through to the httpx.Client.patch call.

    The API documentation for this call can be found below:
    https://clerk.com/docs/reference/backend-api/tag/users/patch/users/%7Buser_id%7D/metadata
    """

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        reraise=True,
    )
    def _inner(user_id, metadata, **kwargs):
        """Update the metadata of the user with the given user ID. All additional kwargs
        are passed through to the httpx.Client.patch call.

        This will retry rate limit errors.

        The API documentation for this call can be found below:
        https://clerk.com/docs/reference/backend-api/tag/users/patch/users/%7Buser_id%7D/metadata
        """
        result = clerk_backend_httpx_client.patch(
            url=f"/users/{user_id}/metadata", json=metadata, **kwargs
        )
        result.raise_for_status()

        return result.json()

    return _inner


@pytest.fixture
def clerk_add_org_member(clerk_backend_httpx_client):
    """This fixture provides a function to add a user to an organization. All additional
    kwargs are passed through to the httpx.Client.post call.

    The API documentation for this call can be found below:
    https://clerk.com/docs/reference/backend-api/tag/Organization-Memberships#operation/CreateOrganizationMembership
    """

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        reraise=True,
    )
    def _inner(org_id, user_id, role, **kwargs):
        """Add's the provided user ID to the provided org ID with the provided role. All
        additional kwargs are passed through to the httpx.Client.post call.

        This will retry rate limit errors.

        The API documentation for this call can be found below:
        https://clerk.com/docs/reference/backend-api/tag/Organization-Memberships#operation/CreateOrganizationMembership
        """
        result = clerk_backend_httpx_client.post(
            url=f"/organizations/{org_id}/memberships",
            json={"user_id": user_id, "role": role},
            **kwargs,
        )
        result.raise_for_status()
        return result.json()

    return _inner


@pytest.fixture
def clerk_sign_user_in(clerk_frontend_httpx_client):
    """This fixture returns a function that, given a Clerk User's email and password,
    will sign that user in and return the resulting sign in object from the front end
    API. All additional kwargs are passed through to the httpx.Client.post call.

    The API documentation for this call can be found below:
    https://clerk.com/docs/reference/frontend-api/tag/Sign-Ins#operation/createSignIn
    """

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        reraise=True,
    )
    def _inner(email, password, **kwargs):
        """Attempts to sign in the user using the provided email and password, and then
        returns the sign in object. All additional kwargs are passed through to the
        httpx.Client.post call.

        This will retry rate limit errors.

        The API documentation for this call can be found below:
        https://clerk.com/docs/reference/frontend-api/tag/Sign-Ins#operation/createSignIn
        """
        result = clerk_frontend_httpx_client.post(
            url="/client/sign_ins",
            data={"strategy": "password", "identifier": email, "password": password},
            **kwargs,
        )
        result.raise_for_status()
        result = result.json()
        assert result["response"]["status"] == "complete"
        return result

    return _inner


@pytest.fixture
def clerk_touch_user_session(clerk_frontend_httpx_client):
    """This fixture returns a function that, given a Clerk user session ID and any
    optional session_data, touch the session with the given ID with any session_data
    sent as form data. This passes through any additional kwargs to the
    httpx.Client.post call.

    The API documentation for this call can be found below:
    https://clerk.com/docs/reference/frontend-api/tag/Sessions#operation/touchSession
    """

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        reraise=True,
    )
    def _inner(session_id, session_data=None, **kwargs):
        """Given a Clerk user session ID and any optional session_data, touch the
        session with the given ID with any session_data sent as form data. This passes
        through any additional kwargs to the httpx.Client.post call.

        This will retry rate limit errors.

        The API documentation for this call can be found below:
        https://clerk.com/docs/reference/frontend-api/tag/Sessions#operation/touchSession
        """
        result = clerk_frontend_httpx_client.post(
            url=f"/client/sessions/{session_id}/touch", data=session_data, **kwargs
        )
        result.raise_for_status()
        return result.json()

    return _inner


@pytest.fixture
def clerk_set_user_active_org(clerk_touch_user_session):
    """This fixture returns a function that, given a Clerk user session ID and an
    organization ID, attempts to set that organization as active.

    The user must already be a member of the organization for this to work.

    Any additional kwargs are passed through to the httpx.Client.post call.
    """

    def _inner(session_id, org_id, **kwargs):
        """Given a Clerk user session ID and an organization ID, this function attempts
        to set that organization as active.

        The user must already be a member of the organization for this to work.

        Any additional kwargs are passed through to the httpx.Client.post call.
        """
        return clerk_touch_user_session(
            session_id=session_id,
            session_data={"active_organization_id": org_id},
            **kwargs,
        )

    return _inner


@pytest.fixture
def clerk_get_user_session_token(clerk_frontend_httpx_client):
    """This fixture returns a function that, given a Clerk session ID, will retrieve a
    currently valid session token for the user tied to that session.

    Any additional kwargs are passed through to the httpx.Client.post call.

    The API documentation for this call can be found below:
    https://clerk.com/docs/reference/frontend-api/tag/Sessions#operation/createSessionToken
    """

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        reraise=True,
    )
    def _inner(session_id, **kwargs):
        """Retrieves a currently valid session token for the user tied to the provided
        session ID.

        Any additional kwargs are passed through to the httpx.Client.post call.

        This will retry rate limit errors.

        The API documentation for this call can be found below:
        https://clerk.com/docs/reference/frontend-api/tag/Sessions#operation/createSessionToken
        """
        result = clerk_frontend_httpx_client.post(
            url=f"/client/sessions/{session_id}/tokens", **kwargs
        )
        result.raise_for_status()
        return result.json()["jwt"]

    return _inner


@pytest.fixture
def clerk_end_user_session(clerk_frontend_httpx_client):
    """This fixture returns a function that, given a Clerk user session ID, ends that
    session. This passes through any additional kwargs to the httpx.Client.post call.

    The API documentation for this call can be found below:
    https://clerk.com/docs/reference/frontend-api/tag/Sessions#operation/endSession
    """

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(multiplier=0.5, max=60),
        reraise=True,
    )
    def _inner(session_id, **kwargs):
        """Given a Clerk user session ID, ends that session. This passes through any
        additional kwargs to the httpx.Client.post call.

        This will retry rate limit errors.

        The API documentation for this call can be found below:
        https://clerk.com/docs/reference/frontend-api/tag/Sessions#operation/endSession
        """
        result = clerk_frontend_httpx_client.post(
            url=f"/client/sessions/{session_id}/end", **kwargs
        )
        result.raise_for_status()
        return result.json()

    return _inner
