"""
Kelvin API Client.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Union, cast

from typing_extensions import Literal

from kelvin.api.client.api_service_model import ApiServiceModel

from ..model import requests, response, responses


class Thread(ApiServiceModel):
    @classmethod
    def create_thread(
        cls,
        data: Optional[Union[requests.ThreadCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.ThreadCreate:
        """
        Create Thread

        **Permission Required:** `kelvin.permission.threads.create`.

        ``createThread``: ``POST`` ``/api/v4/threads/create``

        Parameters
        ----------
        data: requests.ThreadCreate, optional
        **kwargs:
            Extra parameters for requests.ThreadCreate
              - create_thread: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/threads/create",
            {},
            {},
            {},
            {},
            data,
            "requests.ThreadCreate",
            False,
            {"201": responses.ThreadCreate, "400": response.Error, "401": response.Error, "500": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def list_threads(
        cls,
        type: Optional[str] = None,
        related_to: Optional[str] = None,
        user_id: Optional[str] = None,
        _dry_run: bool = False,
        _client: Any = None,
    ) -> responses.ThreadsList:
        """
        List Threads

        **Pagination Sortable Columns:** `thread.id`

        **Permission Required:** `kelvin.permission.threads.read`.

        ``listThreads``: ``GET`` ``/api/v4/threads/list``

        Parameters
        ----------
        type : :obj:`str`
            Filter threads by type
        related_to : :obj:`str`
            Filter threads by related_to
        user_id : :obj:`str`
            Filter threads by user_id

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/threads/list",
            {},
            {"type": type, "related_to": related_to, "user_id": user_id},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.ThreadsList, "400": response.Error, "401": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def delete_thread(cls, thread_id: str, _dry_run: bool = False, _client: Any = None) -> None:
        """
        Delete Thread

        **Permission Required:** `kelvin.permission.threads.delete`.

        ``deleteThread``: ``POST`` ``/api/v4/threads/{thread_id}/delete``

        Parameters
        ----------
        thread_id : :obj:`str`, optional
            Thread ID

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/threads/{thread_id}/delete",
            {"thread_id": thread_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": None, "400": response.Error, "403": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_thread_follow(
        cls, thread_id: str, follow: Optional[bool] = None, _dry_run: bool = False, _client: Any = None
    ) -> responses.ThreadFollowUpdate:
        """
        Update Thread Follow

        **Permission Required:** `kelvin.permission.threads.read`.

        ``updateThreadFollow``: ``POST`` ``/api/v4/threads/{thread_id}/follow/update``

        Parameters
        ----------
        thread_id : :obj:`str`, optional
            Thread ID
        follow : :obj:`bool`
            Set user follow value to true or false

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/threads/{thread_id}/follow/update",
            {"thread_id": thread_id},
            {"follow": follow},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.ThreadFollowUpdate, "404": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def get_thread(cls, thread_id: str, _dry_run: bool = False, _client: Any = None) -> responses.ThreadGet:
        """
        Get Thread

        **Permission Required:** `kelvin.permission.threads.read`.

        ``getThread``: ``GET`` ``/api/v4/threads/{thread_id}/get``

        Parameters
        ----------
        thread_id : :obj:`str`, optional
            Thread ID

        """

        result = cls._make_request(
            _client,
            "get",
            "/api/v4/threads/{thread_id}/get",
            {"thread_id": thread_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.ThreadGet, "404": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def create_thread_reply(
        cls,
        thread_id: str,
        reply_id: Optional[str] = None,
        data: Optional[Union[requests.ThreadReplyCreate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.ThreadReplyCreate:
        """
        Create Thread Reply

        **Permission Required:** `kelvin.permission.threads.create`.

        ``createThreadReply``: ``POST`` ``/api/v4/threads/{thread_id}/replies/create``

        Parameters
        ----------
        thread_id : :obj:`str`, optional
            Thread ID
        reply_id : :obj:`str`
            Reply ID
        data: requests.ThreadReplyCreate, optional
        **kwargs:
            Extra parameters for requests.ThreadReplyCreate
              - create_thread_reply: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/threads/{thread_id}/replies/create",
            {"thread_id": thread_id},
            {"reply_id": reply_id},
            {},
            {},
            data,
            "requests.ThreadReplyCreate",
            False,
            {"200": responses.ThreadReplyCreate, "400": response.Error, "401": response.Error, "500": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def delete_thread_reply(cls, thread_id: str, reply_id: str, _dry_run: bool = False, _client: Any = None) -> str:
        """
        Delete Thread Reply

        **Permission Required:** `kelvin.permission.threads.delete`.

        ``deleteThreadReply``: ``POST`` ``/api/v4/threads/{thread_id}/replies/{reply_id}/delete``

        Parameters
        ----------
        thread_id : :obj:`str`, optional
            Thread ID
        reply_id : :obj:`str`, optional
            Reply ID

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/threads/{thread_id}/replies/{reply_id}/delete",
            {"thread_id": thread_id, "reply_id": reply_id},
            {},
            {},
            {},
            None,
            None,
            False,
            {"200": str, "400": response.Error, "401": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_thread_reply(
        cls,
        thread_id: str,
        reply_id: str,
        data: Optional[Union[requests.ThreadReplyUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.ThreadReplyUpdate:
        """
        Update Thread Reply

        **Permission Required:** `kelvin.permission.threads.update`.

        ``updateThreadReply``: ``POST`` ``/api/v4/threads/{thread_id}/replies/{reply_id}/update``

        Parameters
        ----------
        thread_id : :obj:`str`, optional
            Thread ID
        reply_id : :obj:`str`, optional
            Reply ID
        data: requests.ThreadReplyUpdate, optional
        **kwargs:
            Extra parameters for requests.ThreadReplyUpdate
              - update_thread_reply: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/threads/{thread_id}/replies/{reply_id}/update",
            {"thread_id": thread_id, "reply_id": reply_id},
            {},
            {},
            {},
            data,
            "requests.ThreadReplyUpdate",
            False,
            {"200": responses.ThreadReplyUpdate, "400": response.Error, "401": response.Error, "500": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result

    @classmethod
    def update_thread_seen(
        cls, thread_id: str, seen: Optional[bool] = None, _dry_run: bool = False, _client: Any = None
    ) -> responses.ThreadSeenUpdate:
        """
        Update Thread Seen

        **Permission Required:** `kelvin.permission.threads.read`.

        ``updateThreadSeen``: ``POST`` ``/api/v4/threads/{thread_id}/seen/update``

        Parameters
        ----------
        thread_id : :obj:`str`, optional
            Thread ID
        seen : :obj:`bool`
            Set user seen value to true or false

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/threads/{thread_id}/seen/update",
            {"thread_id": thread_id},
            {"seen": seen},
            {},
            {},
            None,
            None,
            False,
            {"200": responses.ThreadSeenUpdate, "404": response.Error, "500": response.Error},
            False,
            _dry_run,
        )
        return result

    @classmethod
    def update_thread(
        cls,
        thread_id: str,
        data: Optional[Union[requests.ThreadUpdate, Mapping[str, Any]]] = None,
        _dry_run: bool = False,
        _client: Any = None,
        **kwargs: Any,
    ) -> responses.ThreadUpdate:
        """
        Update Thread

        **Permission Required:** `kelvin.permission.threads.update`.

        ``updateThread``: ``POST`` ``/api/v4/threads/{thread_id}/update``

        Parameters
        ----------
        thread_id : :obj:`str`, optional
            Thread ID
        data: requests.ThreadUpdate, optional
        **kwargs:
            Extra parameters for requests.ThreadUpdate
              - update_thread: dict

        """

        result = cls._make_request(
            _client,
            "post",
            "/api/v4/threads/{thread_id}/update",
            {"thread_id": thread_id},
            {},
            {},
            {},
            data,
            "requests.ThreadUpdate",
            False,
            {"200": responses.ThreadUpdate, "400": response.Error, "401": response.Error, "500": response.Error},
            False,
            _dry_run,
            kwargs,
        )
        return result
