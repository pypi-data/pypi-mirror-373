"""Simplifies interacting with an ActivityPub server / instance.

This is a minimal implementation only implementing some API calls. API
calls supported will likely be expanded over time. However, do not
expect a full or complete implementation of the ActivityPub API.
"""

import asyncio
import json
import logging
import random
import uuid
from json import JSONDecodeError
from typing import IO
from typing import Any
from typing import Final
from typing import TypeVar
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import urlparse

from httpx import AsyncClient
from httpx import HTTPError
from httpx import Response
from whenever import Instant

from minimal_activitypub import USER_AGENT
from minimal_activitypub import SearchType
from minimal_activitypub import Status
from minimal_activitypub import Visibility
from minimal_activitypub import __display_name__
from minimal_activitypub import __version__

PAGINATION_UNDEFINED: dict[str, dict[str, str | None]] = {
    "next": {"max_id": None, "min_id": None},
    "prev": {"max_id": None, "min_id": None},
}

logger = logging.getLogger(__display_name__)


ActivityPubClass = TypeVar("ActivityPubClass", bound="ActivityPub")
REDIRECT_URI: Final[str] = "urn:ietf:wg:oauth:2.0:oob"

# HTTP status codes of interest (more detail at https://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
STATUS_BAD_REQUEST: Final[int] = 400
STATUS_UNAUTHORIZED: Final[int] = 401
STATUS_FORBIDDEN: Final[int] = 403
STATUS_NOT_FOUND: Final[int] = 404
STATUS_CONFLICT: Final[int] = 409
STATUS_GONE: Final[int] = 410
STATUS_UNPROCESSABLE_ENTITY: Final[int] = 422
STATUS_TOO_MANY_REQUESTS: Final[int] = 429
STATUS_INTERNAL_SERVER_ERROR: Final[int] = 500

INSTANCE_TYPE_MASTODON: Final[str] = "Mastodon"
INSTANCE_TYPE_PLEROMA: Final[str] = "Pleroma"
INSTANCE_TYPE_TAKAHE: Final[str] = "takahe"

MAX_ATTACHMENTS_MASTODON: Final[int] = 4
MAX_ATTACHMENTS_PLEROMA: Final[int] = 10  # 10 is a placeholder, reasonable stand in
MAX_ATTACHMENTS_TAKAHE: Final[int] = 10  # 10 is a placeholder, reasonable stand in


class ActivityPub:
    """Simplifies interacting with an ActivityPub server / instance.

    This is a minimal implementation only implementing methods needed
    for the function of MastodonAmnesia
    """

    def __init__(
        self: ActivityPubClass,
        instance: str,
        client: AsyncClient,
        access_token: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """Initialise ActivityPub instance with reasonable default values.

        :param instance: domain name or url to instance to connect to
        :param client: httpx AsyncClient to use for communicating with instance
        :param access_token: authentication token
        :param timeout: Optional number of seconds to wait for a response from the instance server.
            Defaults to None which equates to 120 seconds / 2 minutes timeout

        """
        self.instance = instance.rstrip("/")
        self.headers: list[tuple[str, str]] = []
        if access_token:
            self.headers.append(("Authorization", f"Bearer {access_token}"))
        self.client = client
        self.pagination: dict[str, dict[str, str | None]] = {
            "next": {"max_id": None, "min_id": None},
            "prev": {"max_id": None, "min_id": None},
        }
        self.timeout = timeout if timeout else 120
        self.instance_type = INSTANCE_TYPE_MASTODON  # default until determined otherwise with determine_instance_type()
        self.max_attachments = MAX_ATTACHMENTS_MASTODON
        self.max_att_size = 10000000
        self.supported_mime_types: list[str] = []
        self.max_status_len = 500
        self.ratelimit_limit = 300
        self.ratelimit_remaining = 300
        self.ratelimit_reset = Instant.now().py_datetime()
        logger.debug(
            "client_2_server.ActivityPub(instance=%s, client=%s, access_token=<redacted>)",
            instance,
            client,
        )
        logger.debug("client_2_server.ActivityPub() ... version=%s", __version__)

    async def verify_credentials(self: ActivityPubClass) -> Any:
        """Verify the credentials of the user.

        :returns: The response is a JSON object containing the account's information.

        """
        url = f"{self.instance}/api/v1/accounts/verify_credentials"
        logger.debug("ActivityPub.verify_credentials() - url=%s", url)
        try:
            response = await self.client.get(url=url, headers=self.headers, timeout=self.timeout)
            logger.debug(
                "ActivityPub.verify_credentials - response: \n%s",
                response,
            )
            self._update_ratelimit(response.headers)
            await ActivityPub.__check_exception(response=response)
            self._parse_next_prev(links=response.headers.get("Link"))
            json_response = response.json()
        except HTTPError as error:
            raise NetworkError from error

        return json_response

    async def determine_instance_type(self: ActivityPubClass) -> None:
        """Check if the instance is a Pleroma instance or not."""
        instance = self.instance
        if "http" not in self.instance:
            instance = f"https://{self.instance}"

        try:
            response = await self.client.get(url=f"{instance}/api/v1/instance", timeout=self.timeout)
            await ActivityPub.__check_exception(response=response)
            response_dict = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.determine_instance_type -> response.dict:\n%s",
            json.dumps(response_dict, indent=4),
        )
        self.instance = instance

        self._set_instance_parameters(response_dict)

        logger.debug(
            "ActivityPub.determine_instance_type() ... instance_type=%s",
            self.instance_type,
        )

    def _set_instance_parameters(self, response_dict: dict[str, Any]) -> None:
        """Set instance parameters. The following parameters are set.

        - instance-type: Type of instance, Mastodon, Takahe, Pleroma
        - max_status_len: Maximum length in characters for a status
        - max_attachments: Maximum number of attachments for a status
        - max_att_size: Maximum size supported for attachments
        - supported_mime_types: list of supported mime types for attachments

        :param response_dict: Dictionary returned by call to .../api/v1/instance
        """
        version = response_dict.get("version", "")
        if INSTANCE_TYPE_TAKAHE in version:
            self.instance_type = INSTANCE_TYPE_TAKAHE
            self.max_attachments = MAX_ATTACHMENTS_TAKAHE
        elif INSTANCE_TYPE_PLEROMA in version:
            self.instance_type = INSTANCE_TYPE_PLEROMA
            self.max_attachments = MAX_ATTACHMENTS_PLEROMA

        instance_config = response_dict.get("configuration", {})

        if (max_status_len := instance_config.get("statuses", {}).get("max_characters")) or (
            max_status_len := response_dict.get("max_characters")
        ):
            self.max_status_len = max_status_len

        if (max_attachments := instance_config.get("statuses", {}).get("max_media_attachments")) or (
            max_attachments := response_dict.get("max_media_attachments")
        ):
            self.max_attachments = max_attachments

        if max_att_size := instance_config.get("media_attachments", {}).get("image_size_limit"):
            self.max_att_size = max_att_size

        if mime_types := instance_config.get("media_attachments", {}).get("supported_mime_types"):
            self.supported_mime_types = mime_types

    async def get_account_statuses(
        self: ActivityPubClass,
        account_id: str,
        max_id: str | None = None,
        min_id: str | None = None,
    ) -> list[Status]:
        """Get statuses of a given account.

        :param account_id: The account ID of the account you want to get the statuses of
        :param max_id: The ID of the last status you want to get
        :param min_id: The ID of the oldest status you want to retrieve

        :returns: A list of statuses.

        """
        logger.debug(
            "ActivityPub.get_account_statuses(account_id=%s, max_id=%s, min_id=%s)",
            account_id,
            max_id,
            min_id,
        )

        await self._pre_call_checks()

        paging = "?"
        url = f"{self.instance}/api/v1/accounts/{account_id}/statuses"
        if max_id:
            paging += f"max_id={max_id}"
        if min_id:
            if len(paging) > 1:
                paging += "&"
            paging += f"min_id={min_id}"
        if max_id or min_id:
            url += paging
        logger.debug("ActivityPub.get_account_statuses - url = %s", url)
        try:
            response = await self.client.get(url=url, headers=self.headers, timeout=self.timeout)
            self._update_ratelimit(response.headers)
            await ActivityPub.__check_exception(response=response)
            self._parse_next_prev(links=response.headers.get("Link"))
            result: list[Status] = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.get_account_statuses -> result:\n%s",
            json.dumps(result, indent=4),
        )
        return result

    async def get_public_timeline(  # noqa: PLR0913 This method has this many arguments
        self: ActivityPubClass,
        local: bool = False,
        remote: bool = False,
        only_media: bool = False,
        max_id: str | None = None,
        since_id: str | None = None,
        min_id: str | None = None,
        limit: int = 20,
    ) -> list[Status]:
        """Get statuses of the public timeline.

        :param local: Show only local statuses? Defaults to False.
        :param remote: Show only remote statuses? Defaults to False.
        :param only_media: Show only statuses with media attached? Defaults to False.
        :param max_id: All results returned will be lesser than this ID. In effect, sets an upper bound on results.
        :param since_id: All results returned will be greater than this ID. In effect, sets a lower bound on results.
        :param min_id: Returns results immediately newer than this ID. In effect, sets a cursor at this ID and
            paginates forward.
        :param limit: Maximum number of results to return. Defaults to 20 statuses. Max 40 statuses.

        :returns: A list of statuses.

        """
        logger.debug(
            "ActivityPub.get_timeline(local=%s, remote=%s, only_media=%s, max_id=%s, since_id=%s, min_id=%s, limit=%s)",
            local,
            remote,
            only_media,
            max_id,
            since_id,
            min_id,
            limit,
        )

        await self._pre_call_checks()

        url = f"{self.instance}/api/v1/timelines/public"

        params: dict[str, Any] = {"limit": limit}
        if local:
            params["local"] = local
        if remote:
            params["remote"] = remote
        if only_media:
            params["only_media"] = only_media
        if max_id:
            params["max_id"] = max_id
        if min_id:
            params["min_id"] = min_id
        if since_id:
            params["since-id"] = since_id

        logger.debug("ActivityPub.get_public_timeline - url = %s", url)
        logger.debug("ActivityPub.get_public_timeline - params = %s", params)
        try:
            response = await self.client.get(url=url, headers=self.headers, params=params, timeout=self.timeout)
            self._update_ratelimit(response.headers)
            await ActivityPub.__check_exception(response=response)
            self._parse_next_prev(links=response.headers.get("Link"))
            result: list[Status] = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.get_timeline -> result:\n%s",
            json.dumps(result, indent=4),
        )
        return result

    async def get_home_timeline(
        self: ActivityPubClass,
        max_id: str | None = None,
        since_id: str | None = None,
        min_id: str | None = None,
        limit: int = 20,
    ) -> list[Status]:
        """Get statuses of the home timeline.

        :param max_id: All results returned will be lesser than this ID. In effect, sets an upper bound on results.
        :param since_id: All results returned will be greater than this ID. In effect, sets a lower bound on results.
        :param min_id: Returns results immediately newer than this ID. In effect, sets a cursor at this ID and
            paginates forward.
        :param limit: Maximum number of results to return. Defaults to 20 statuses. Max 40 statuses.

        :returns: A list of statuses.

        """
        logger.debug(
            "ActivityPub.get_timeline(max_id=%s, since_id=%s, min_id=%s, limit=%s)",
            max_id,
            since_id,
            min_id,
            limit,
        )

        await self._pre_call_checks()

        url = f"{self.instance}/api/v1/timelines/home"

        params: dict[str, Any] = {"limit": limit}
        if max_id:
            params["max_id"] = max_id
        if min_id:
            params["min_id"] = min_id
        if since_id:
            params["since-id"] = since_id

        logger.debug("ActivityPub.get_home_timeline - url = %s", url)
        logger.debug("ActivityPub.get_home_timeline - params = %s", params)
        try:
            response = await self.client.get(url=url, headers=self.headers, params=params, timeout=self.timeout)
            self._update_ratelimit(response.headers)
            await ActivityPub.__check_exception(response=response)
            self._parse_next_prev(links=response.headers.get("Link"))
            result: list[Status] = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.get_timeline -> result:\n%s",
            json.dumps(result, indent=4),
        )
        return result

    async def delete_status(self: ActivityPubClass, status: str | Status, delete_only_one: bool = False) -> Status:
        """Delete a status.

        :param status: The ID of the status you want to delete or a dict containing the status details
        :param delete_only_one: Set this to True if this delete is the only one. Set it to False if this delete is part
            of a batch of deletes. With this set to False it will introduce a random wait of up to 3 seconds.
            This hopefully should help with instance saturation.
            Defaults to False

        :returns: Status that has just been deleted
        """
        if not delete_only_one:
            # add random delay of up to 3 seconds in case we are deleting many
            # statuses in a batch
            sleep_for = random.SystemRandom().random() * 3
            logger.debug(
                "ActivityPub.delete_status - status_id = %s - sleep_for = %s",
                status if isinstance(status, str) else status["id"],
                sleep_for,
            )
            await asyncio.sleep(delay=sleep_for)

        if isinstance(status, str):
            status_id = status
        elif isinstance(status, dict):
            status_id = status["id"]
            if self.instance_type == INSTANCE_TYPE_PLEROMA and status["reblogged"]:
                undo_reblog_response = await self.undo_reblog(status=status)
                return undo_reblog_response
            if self.instance_type == INSTANCE_TYPE_PLEROMA and status["favourited"]:
                undo_favourite_response = await self.undo_favourite(status=status)
                return undo_favourite_response

        await self._pre_call_checks()

        url = f"{self.instance}/api/v1/statuses/{status_id}"
        try:
            response = await self.client.delete(url=url, headers=self.headers, timeout=self.timeout)
            self._update_ratelimit(response.headers)
            await ActivityPub.__check_exception(response=response)
            self._parse_next_prev(links=response.headers.get("Link"))
            result: Status = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.delete_status -> result:\n%s",
            json.dumps(result, indent=4),
        )
        return result

    async def undo_reblog(self: ActivityPubClass, status: str | dict[Any, Any]) -> Status:
        """Remove a reblog.

        :param status: The ID of the status you want to delete or a dict containing the status details

        :returns: The response from the server.
        """
        logger.debug(
            "ActivityPub.undo_reblog(status=%s",
            status,
        )

        if isinstance(status, str):
            status_id = status
        elif isinstance(status, dict):
            status_id = status["reblog"]["id"]

        await self._pre_call_checks()
        url = f"{self.instance}/api/v1/statuses/{status_id}/unreblog"
        try:
            response = await self.client.post(url=url, headers=self.headers, timeout=self.timeout)
            self._update_ratelimit(response.headers)
            await ActivityPub.__check_exception(response=response)
            self._parse_next_prev(links=response.headers.get("Link"))
            result: Status = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.undo_reblog -> result:\n%s",
            json.dumps(result, indent=4),
        )
        return result

    async def reblog(self: ActivityPubClass, status_id: str) -> Status:
        """Reblog a status.

        :param status_id: The ID of the status you want to delete or a dict containing the status details

        :returns: The response from the server.
        """
        logger.debug(
            "ActivityPub.reblog(status_id=%s)",
            status_id,
        )

        await self._pre_call_checks()
        url = f"{self.instance}/api/v1/statuses/{status_id}/reblog"
        try:
            response = await self.client.post(url=url, headers=self.headers, timeout=self.timeout)
            self._update_ratelimit(response.headers)
            await ActivityPub.__check_exception(response=response)
            self._parse_next_prev(links=response.headers.get("Link"))
            result: Status = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.reblog -> result:\n%s",
            json.dumps(result, indent=4),
        )
        return result

    async def undo_favourite(
        self: ActivityPubClass,
        status: str | dict[Any, Any],
    ) -> Status:
        """Remove a favourite.

        :param status: The ID of the status you want to delete or a dict containing the status details

        :returns: The Status that has just been un-favourited.
        """
        logger.debug(
            "ActivityPub.undo_favourite(status=%s)",
            status,
        )

        if isinstance(status, str):
            status_id = status
        elif isinstance(status, dict):
            status_id = status["id"]

        await self._pre_call_checks()
        url = f"{self.instance}/api/v1/statuses/{status_id}/unfavourite"
        try:
            response = await self.client.post(url=url, headers=self.headers, timeout=self.timeout)
            self._update_ratelimit(response.headers)
            await ActivityPub.__check_exception(response=response)
            self._parse_next_prev(links=response.headers.get("Link"))
            result: Status = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.undo_favourite -> result:\n%s",
            json.dumps(result, indent=4),
        )
        return result

    @staticmethod
    async def generate_authorization_url(
        instance_url: str,
        client_id: str,
        user_agent: str = USER_AGENT,
    ) -> str:
        """Create URL to get access token interactively from website.

        :param instance_url: The URL of the Mastodon instance you want to connect to
        :param client_id: Client id of app as generated by create_app method
        :param user_agent: User agent identifier to use. Defaults to minimal_activitypub related one.

        :returns: String containing URL to visit to get access token interactively from instance.
        """
        logger.debug(
            "ActivityPub.get_auth_token_interactive(instance_url=%s, client=...,client_id=%s, user_agent=%s)",
            instance_url,
            client_id,
            user_agent,
        )
        if "http" not in instance_url:
            instance_url = f"https://{instance_url}"

        url_params = urlencode(
            {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": REDIRECT_URI,
                "scope": "read write",
            }
        )
        auth_url = f"{instance_url}/oauth/authorize?{url_params}"
        logger.debug(
            "ActivityPub.get_auth_token_interactive(...) -> %s",
            auth_url,
        )

        return auth_url

    @staticmethod
    async def validate_authorization_code(
        client: AsyncClient,
        instance_url: str,
        authorization_code: str,
        client_id: str,
        client_secret: str,
    ) -> str:
        """Validate an authorization code and get access token needed for API access.

        :param client: httpx.AsyncClient
        :param instance_url: The URL of the Mastodon instance you want to connect to
        :param authorization_code: authorization code
        :param client_id: client id as returned by create_app method
        :param client_secret: client secret as returned by create_app method

        :returns: access token
        """
        logger.debug(
            "ActivityPub.validate_authorization_code(authorization_code=%s, client_id=%s, client_secret=<redacted>)",
            authorization_code,
            client_id,
        )
        if "http" not in instance_url:
            instance_url = f"https://{instance_url}"

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "read write",
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
            "code": authorization_code,
        }
        try:
            response = await client.post(url=f"{instance_url}/oauth/token", data=data)
            logger.debug(
                "ActivityPub.validate_authorization_code - response:\n%s",
                response,
            )
            await ActivityPub.__check_exception(response)
            response_dict = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.validate_authorization_code - response.json: \n%s",
            json.dumps(response_dict, indent=4),
        )
        return str(response_dict["access_token"])

    @staticmethod
    async def get_auth_token(  # noqa: PLR0913  - No way around needing all this parameters
        instance_url: str,
        username: str,
        password: str,
        client: AsyncClient,
        user_agent: str = USER_AGENT,
        client_website: str = "https://pypi.org/project/minimal-activitypub/",
    ) -> str:
        """Create an app and use it to get an access token.

        :param instance_url: The URL of the Mastodon instance you want to connect to
        :param username: The username of the account you want to get an auth_token for
        :param password: The password of the account you want to get an auth_token for
        :param client: httpx.AsyncClient
        :param user_agent: User agent identifier to use. Defaults to minimal_activitypub related one.
        :param client_website: Link to site for user_agent. Defaults to link to minimal_activitypub on Pypi.org

        :returns: The access token is being returned.
        """
        logger.debug(
            "ActivityPub.get_auth_token(instance_url=%s, username=%s, password=<redacted>, client=..., "
            "user_agent=%s, client_website=%s)",
            instance_url,
            username,
            user_agent,
            client_website,
        )
        if "http" not in instance_url:
            instance_url = f"https://{instance_url}"

        client_id, client_secret = await ActivityPub.create_app(
            client_website=client_website,
            instance_url=instance_url,
            client=client,
            user_agent=user_agent,
        )

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "read write",
            "redirect_uris": REDIRECT_URI,
            "grant_type": "password",
            "username": username,
            "password": password,
        }

        try:
            response = await client.post(url=f"{instance_url}/oauth/token", data=data)
            logger.debug("ActivityPub.get_auth_token - response:\n%s", response)
            await ActivityPub.__check_exception(response)
            response_dict = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.get_auth_token - response.json: \n%s",
            json.dumps(response_dict, indent=4),
        )
        return str(response_dict["access_token"])

    @staticmethod
    async def create_app(
        instance_url: str,
        client: AsyncClient,
        user_agent: str = USER_AGENT,
        client_website: str = "https://pypi.org/project/minimal-activitypub/",
    ) -> tuple[str, str]:
        """Create an app.

        :param instance_url: The URL of the Mastodon instance you want to connect to
        :param client: httpx.AsyncClient
        :param user_agent: User agent identifier to use. Defaults to minimal_activitypub related one.
        :param client_website: Link to site for user_agent. Defaults to link to minimal_activitypub on Pypi.org

        :returns: tuple(client_id, client_secret)
        """
        logger.debug(
            "ActivityPub.create_app(instance_url=%s, client=..., user_agent=%s, client_website=%s)",
            instance_url,
            user_agent,
            client_website,
        )

        if "http" not in instance_url:
            instance_url = f"https://{instance_url}"

        data = {
            "client_name": user_agent,
            "client_website": client_website,
            "scopes": "read write",
            "redirect_uris": REDIRECT_URI,
        }
        try:
            response = await client.post(url=f"{instance_url}/api/v1/apps", data=data)
            logger.debug("ActivityPub.create_app response: \n%s", response)
            await ActivityPub.__check_exception(response)
            response_dict = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.create_app response.json: \n%s",
            json.dumps(response_dict, indent=4),
        )
        return (response_dict["client_id"]), (response_dict["client_secret"])

    async def post_status(
        self: ActivityPubClass,
        status: str,
        visibility: Visibility = Visibility.PUBLIC,
        media_ids: list[str] | None = None,
        sensitive: bool = False,
        spoiler_text: str | None = None,
    ) -> Status:
        """Post a status to the fediverse.

        :param status: The text to be posted on the timeline.
        :param visibility: Visibility of the posted status. Enumerable one of `public`, `unlisted`,
            `private`, or `direct`. Defaults to `public`
        :param media_ids: list of ids for media (pictures, videos, etc) to be attached to this post.
            Can be `None` if no media is to be attached. Defaults to `None`
        :param sensitive: Set to true the post is of a sensitive nature and should be marked as such.
            For example overly political or explicit material is often marked as sensitive.
            Applies particularly to attached media. Defaults to `False`
        :param spoiler_text: Text to be shown as a warning or subject before the actual content.
            Statuses are generally collapsed behind this field. Defaults to `None`

        :return: dict of the status just posted.
        """
        logger.debug(
            "ActivityPub.post_status(status=%s, visibility=%s, media_ids=%s, sensitive=%s, spoiler_text=%s)",
            status,
            visibility,
            media_ids,
            sensitive,
            spoiler_text,
        )
        await self._pre_call_checks()

        url = f"{self.instance}/api/v1/statuses"
        headers = self.headers.copy()
        headers.append(("Idempotency-Key", uuid.uuid4().hex))

        logger.debug("ActivityPub.post_status(...) - using URL=%s", url)

        data = {
            "status": status,
            "visibility": visibility.value,
        }
        if sensitive:
            data["sensitive"] = "true"
        if media_ids:
            data["media_ids[]"] = media_ids  # type: ignore
        if spoiler_text:
            data["spoiler_text"] = spoiler_text

        logger.debug("data=%s", data)

        try:
            response = await self.client.post(
                url=url,
                headers=headers,
                data=data,
                timeout=self.timeout,
            )
            self._update_ratelimit(headers=response.headers)
            await ActivityPub.__check_exception(response=response)
            result: Status = response.json()
            logger.debug("ActivityPub.post_status - request:\n%s", response.request)
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.post_status -> result:\n%s",
            json.dumps(result, indent=4),
        )
        return result

    async def post_media(
        self: ActivityPubClass,
        file: IO[bytes],
        mime_type: str,
        description: str | None = None,
        focus: tuple[float, float] | None = None,
    ) -> Any:
        """Post a media file (image or video).

        :param file: The file to be uploaded
        :param mime_type: Mime type
        :param description: A plain-text description of the media, for accessibility purposes
        :param focus: Two floating points (x,y), comma-delimited, ranging from -1.0 to 1.0
            (see “Focal points <https://docs.joinmastodon.org/methods/statuses/media/#focal-points>”_)

        :returns: dict containing details for this media on server, such a `id`, `url` etc
        """
        logger.debug(
            "ActivityPub.post_media(file=..., mime_type=%s, description=%s, focus=%s)",
            mime_type,
            description,
            focus,
        )

        await self._pre_call_checks()

        url = f"{self.instance}/api/v1/media"
        upload_file = {"file": (uuid.uuid4().hex, file, mime_type)}
        data = {}
        if description:
            data["description"] = description
        if focus and len(focus) >= 2:
            data["focus"] = f"{focus[0]},{focus[1]}"

        try:
            response = await self.client.post(
                url=url,
                headers=self.headers,
                data=data,
                files=upload_file,
                timeout=self.timeout,
            )
            self._update_ratelimit(headers=response.headers)
            await ActivityPub.__check_exception(response=response)
            result = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug(
            "ActivityPub.post_media -> result:\n%s",
            json.dumps(result, indent=4),
        )
        return result

    async def search(  # noqa PLR0913
        self: ActivityPubClass,
        query: str,
        query_type: SearchType,
        resolve: bool = True,
        following: bool = False,
        account_id: str | None = None,
        exclude_unreviewed: bool = False,
        max_id: str | None = None,
        min_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Any:
        """Search for accounts, statuses and hashtags.

        :param query: The search query.
        :param query_type: Specify whether to search for only accounts, hashtags, statuses.
            Use SearchType enum for this.
        :param resolve: Only relevant if type includes accounts. If true and (a) the search query is for a remote
            account (e.g., someaccount@someother.server) and (b) the local server does not know about the account,
            WebFinger is used to try and resolve the account at some other.server. This provides the best recall at
            higher latency. If false only accounts the server knows about are returned. Defaults to True.
        :param following: Only include accounts that the user is following? Defaults to False.
        :param account_id: If provided, will only return statuses authored by this account.
        :param exclude_unreviewed: Filter out unreviewed tags? Defaults to False. Use True when trying to find
            trending tags.
        :param max_id: All results returned will be lesser than this ID. In effect, sets an upper bound on results.
        :param min_id: Returns results immediately newer than this ID. In effect, sets a cursor at this ID and paginates
        :param limit: Maximum number of results to return, per type. Mastodon servers default this to 20 results per
            category. Max 40 results per category.
        :param offset: Skip the first n results.
        """
        url = f"{self.instance}/api/v2/search"

        params: dict[str, int | str | bool] = {
            "q": query,
            "type": query_type.value,
            "resolve": resolve,
        }
        if following:
            params["following"] = following
        if account_id:
            params["account_id"] = account_id
        if exclude_unreviewed:
            params["exclude_unreviewed"] = exclude_unreviewed
        if max_id:
            params["max_id"] = max_id
        if min_id:
            params["min_id"] = min_id
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        logger.debug("Params=%s", params)
        try:
            response = await self.client.get(
                url=url,
                headers=self.headers,
                params=params,
                timeout=self.timeout,
            )
            self._update_ratelimit(headers=response.headers)
            await ActivityPub.__check_exception(response=response)
            result = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug("ActivityPub.search -> result:\n%s", json.dumps(result, indent=4))

        return result

    async def get_hashtag_timeline(  # noqa: PLR0913
        self: ActivityPubClass,
        hashtag: str,
        any_tags: list[str] | None = None,
        all_tags: list[str] | None = None,
        none_tags: list[str] | None = None,
        local: bool = False,
        remote: bool = False,
        only_media: bool = False,
        max_id: str | None = None,
        since_id: str | None = None,
        min_id: str | None = None,
        limit: int = 20,
    ) -> list[Status]:
        """Get timeline of statuses with hashtags.

        :param hashtag: Hashtag excluding "#" to list statuses for
        :param any_tags: Return statuses that also contain any of these additional tags.
        :param all_tags: Return statuses that also contain all of these additional tags.
        :param none_tags: Return statuses that contain none of these additional tags.
        :param local: Return only local statuses? Defaults to False.
        :param remote: Return only remote statuses? Defaults to False.
        :param only_media: Return only statuses with media attachments? Defaults to False.
        :param max_id: All results returned will be lesser than this ID. In effect, sets an upper bound on results.
        :param since_id: All results returned will be greater than this ID. In effect, sets a lower bound on results.
        :param min_id: Returns results immediately newer than this ID. In effect, sets a cursor at this ID and
            paginates forward.
        :param limit: Maximum number of results to return, per type. Defaults to 20 results per category.
            Max 40 results per category.
        """
        url = f"{self.instance}/api/v1/timelines/tag/:{hashtag}"

        params: dict[str, int | str | bool | list[Any]] = {
            "local": local,
            "remote": remote,
            "only_media": only_media,
            "limit": limit,
        }
        if any_tags:
            params["any[]"] = any_tags
        if all_tags:
            params["all[]"] = all_tags
        if none_tags:
            params["none[]"] = none_tags
        if max_id:
            params["max_id"] = max_id
        if since_id:
            params["since-id"] = since_id
        if min_id:
            params["min_id"] = min_id

        logger.debug("Params=%s", params)
        try:
            response = await self.client.get(
                url=url,
                headers=self.headers,
                params=params,
                timeout=self.timeout,
            )
            self._update_ratelimit(headers=response.headers)
            await ActivityPub.__check_exception(response=response)
            result: list[Status] = response.json()
        except HTTPError as error:
            raise NetworkError from error

        logger.debug("ActivityPub.search -> result:\n%s", json.dumps(result, indent=4))

        return result

    async def _pre_call_checks(self: ActivityPubClass) -> None:
        """Do checks contacting the instance server.

        For now just looking at rate limits by checking if the rate
        limit is 0 and the rate limit reset time is in the future, raise
        a RatelimitError
        """
        logger.debug(
            "ActivityPub.__pre_call_checks - Limit remaining: %s - Limit resetting at %s",
            self.ratelimit_remaining,
            self.ratelimit_reset,
        )
        if self.ratelimit_remaining == 0 and self.ratelimit_reset > Instant.now().py_datetime():
            raise RatelimitError(429, None, "Rate limited")

    def _parse_next_prev(self: ActivityPubClass, links: str | None) -> None:
        """Extract min_id and max_id from a string like `https://example.com/api/v1/timelines/
        home?min_id=12345&max_id=67890` and store them in the instance attributes
        pagination_min_id and pagination_max_id.

        :param links: The links header from the response
        """
        logger.debug("ActivityPub.__parse_next_prev - links = %s", links)

        if not links:
            # No pagination information provided
            return

        self.pagination = PAGINATION_UNDEFINED

        for comma_links in links.split(sep=", "):
            pagination_rel: str | None = None
            if 'rel="next"' in comma_links:
                pagination_rel = "next"
            elif 'rel="prev"' in comma_links:
                pagination_rel = "prev"
            else:
                # No pagination reference
                continue

            urls = comma_links.split(sep="; ")

            logger.debug("ActivityPub.__parse_next_prev - rel = %s - urls = %s", pagination_rel, urls)

            for url in urls:
                parsed_url = urlparse(url=url.lstrip("<").rstrip(">"))
                queries_dict = parse_qs(str(parsed_url.query))
                logger.debug("ActivityPub.__parse_next_prev - queries_dict = %s", queries_dict)
                min_id = queries_dict.get("min_id")
                max_id = queries_dict.get("max_id")
                if min_id:
                    self.pagination[pagination_rel]["min_id"] = min_id[0]
                if max_id:
                    self.pagination[pagination_rel]["max_id"] = max_id[0]

        logger.debug("ActivityPub.__parse_next_prev - pagination = %s", self.pagination)

    @staticmethod
    def _parse_rate_limit_reset(time_value: str | None) -> Instant | None:
        """Determine date and time when rate limit will be reset."""
        if not time_value:
            return None
        try:
            # Try to parse as Unix timestamp (integer seconds)
            timestamp = int(time_value)
            return Instant.from_timestamp(timestamp)
        except (ValueError, TypeError):
            pass

        try:
            # Fallback: parse as ISO 8601 string using OffsetDateTime
            return Instant.parse_common_iso(time_value)
        except (ValueError, TypeError):
            pass

        return None

    def _update_ratelimit(self: ActivityPubClass, headers: Any) -> None:
        """If the instance is not Pleroma, update the ratelimit variables.

        :param headers: The headers of the response
        """
        temp_ratelimit_limit = temp_ratelimit_remaining = temp_ratelimit_reset = None

        if self.instance_type in (INSTANCE_TYPE_TAKAHE, INSTANCE_TYPE_PLEROMA):
            # Takahe and Pleroma do not seem to return rate limit headers.
            # Default to 5 minute rate limit reset time
            temp_ratelimit_reset = (Instant.now().add(minutes=5)).format_common_iso()

        else:
            temp_ratelimit_limit = headers.get("X-RateLimit-Limit")
            temp_ratelimit_remaining = headers.get("X-RateLimit-Remaining")
            temp_ratelimit_reset = headers.get("X-RateLimit-Reset")

        if temp_ratelimit_limit:
            self.ratelimit_limit = int(temp_ratelimit_limit)
        if temp_ratelimit_remaining:
            self.ratelimit_remaining = int(temp_ratelimit_remaining)
        if temp_ratelimit_reset:
            parsed_reset = ActivityPub._parse_rate_limit_reset(temp_ratelimit_reset)
            if parsed_reset:
                self.ratelimit_reset = parsed_reset.py_datetime()

        logger.debug(
            "ActivityPub.__update_ratelimit - Pleroma Instance: %s - RateLimit Limit %s",
            self.instance_type == INSTANCE_TYPE_PLEROMA,
            self.ratelimit_limit,
        )
        logger.debug(
            "ActivityPub.__update_ratelimit - Limit remaining: %s - Limit resetting at %s",
            self.ratelimit_remaining,
            self.ratelimit_reset,
        )

    @staticmethod
    async def __check_exception(response: Response) -> None:
        """If the response status is greater than or equal to 400, then raise
        an appropriate exception.

        :param response: aiohttp.ClientResponse
        """
        logger.debug("ActivityPub.__check_exception - response.headers = %s", response.headers)
        logger.debug("ActivityPub.__check_exception - response.status_code = %s", response.status_code)

        if response.status_code < STATUS_BAD_REQUEST:
            # No error
            return

        error_message = await ActivityPub.__determine_error_message(response)

        if response.status_code == STATUS_UNAUTHORIZED:
            raise UnauthorizedError(response.status_code, response.reason_phrase, error_message)
        if response.status_code == STATUS_FORBIDDEN:
            raise ForbiddenError(response.status_code, response.reason_phrase, error_message)
        if response.status_code == STATUS_NOT_FOUND:
            raise NotFoundError(response.status_code, response.reason_phrase, error_message)
        if response.status_code == STATUS_CONFLICT:
            raise ConflictError(response.status_code, response.reason_phrase, error_message)
        if response.status_code == STATUS_GONE:
            raise GoneError(response.status_code, response.reason_phrase, error_message)
        if response.status_code == STATUS_UNPROCESSABLE_ENTITY:
            raise UnprocessedError(response.status_code, response.reason_phrase, error_message)
        if response.status_code == STATUS_TOO_MANY_REQUESTS:
            raise RatelimitError(response.status_code, response.reason_phrase, error_message)
        if response.status_code < STATUS_INTERNAL_SERVER_ERROR:
            raise ClientError(response.status_code, response.reason_phrase, error_message)

        raise ServerError(response.status_code, response.reason_phrase, error_message)

    @staticmethod
    async def __determine_error_message(response: Response) -> str:
        """If the response is JSON, return the error message from the JSON,
        otherwise return the response text.

        :param response: aiohttp.ClientResponse
        :returns: The error message as string.
        """
        error_message = "Exception has occurred"
        try:
            content = response.json()
            error_message = content["error"]
        except (HTTPError, KeyError, JSONDecodeError):
            try:
                error_message = response.text
            except (HTTPError, LookupError) as lookup_error:
                logger.debug(
                    "ActivityPub.__determine_error_message - Error when determining response.text  = %s",
                    lookup_error,
                )
        logger.debug("ActivityPub.__determine_error_message - error_message = %s", error_message)
        return error_message


class ActivityPubError(Exception):
    """Base class for all mastodon exceptions."""


class NetworkError(ActivityPubError):
    """`NetworkError` is a subclass of `ActivityPubError` that is raised when
    there is a network error.
    """

    pass


class ApiError(ActivityPubError):
    """`ApiError` is a subclass of `ActivityPubError` that is raised when there
    is an API error.
    """

    pass


class ClientError(ActivityPubError):
    """`ClientError` is a subclass of `ActivityPubError` that is raised when
    there is a client error.
    """

    pass


class UnauthorizedError(ClientError):
    """`UnauthorizedError` is a subclass of `ClientError` that is raised when
    the user represented by the auth_token is not authorized to perform a
    certain action.
    """

    pass


class ForbiddenError(ClientError):
    """`ForbiddenError` is a subclass of `ClientError` that is raised when the
    user represented by the auth_token is forbidden to perform a certain
    action.
    """

    pass


class NotFoundError(ClientError):
    """`NotFoundError` is a subclass of `ClientError` that is raised when an
    object for an action cannot be found.
    """

    pass


class ConflictError(ClientError):
    """`ConflictError` is a subclass of `ClientError` that is raised when there
    is a conflict with performing an action.
    """

    pass


class GoneError(ClientError):
    """`GoneError` is a subclass of `ClientError` that is raised when an object
    for an action has gone / been deleted.
    """

    pass


class UnprocessedError(ClientError):
    """`UnprocessedError` is a subclass of `ClientError` that is raised when an
    action cannot be processed.
    """

    pass


class RatelimitError(ClientError):
    """`RatelimitError` is a subclass of `ClientError` that is raised when
    we've reached a limit of number of actions performed quickly.
    """

    pass


class ServerError(ActivityPubError):
    """`ServerError` is a subclass of `ActivityPubError` that is raised when
    the server / instance encountered an error.
    """

    pass
