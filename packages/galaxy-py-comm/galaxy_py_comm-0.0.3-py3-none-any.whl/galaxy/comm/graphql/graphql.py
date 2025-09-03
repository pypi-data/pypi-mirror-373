#  Copyright (c) 2024 bsaltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import sys
import certifi
import logging
import asyncio
from typing import Any
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from tenacity.asyncio import AsyncRetrying
from tenacity.retry import retry_if_result,                             \
                           retry_if_exception_type
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed
from tenacity import RetryError
from tenacity.before import before_log
from tenacity.after import after_log

from galaxy.service import constant
from galaxy.net.net import Client,                                                                          \
                           AsyncClient
from galaxy.net.auth import CredentialBuilder
from galaxy.perfo.decorator import async_timed


class GraphqlClient(Client):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(GraphqlClient, self).__init__()

    def _load(self) -> None:
        super(GraphqlClient, self)._load()

    def _connect(self) -> None:
        super(GraphqlClient, self)._connect()

    def _close(self) -> None:
        super(GraphqlClient, self)._close()

    def __repr__(self) -> str:
        return "<GraphqlClient(id='{}')>".format(self.id)


class GraphqlAsyncClient(AsyncClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(GraphqlAsyncClient, self).__init__()

    async def _load(self) -> None:
        await super(GraphqlAsyncClient, self)._load()

    async def _connect(self) -> None:
        await super(GraphqlAsyncClient, self)._connect()

    async def _close(self) -> None:
        await super(GraphqlAsyncClient, self)._close()

    def __repr__(self) -> str:
        return "<GraphqlAsyncClient(id='{}')>".format(self.id)


class MSGraphAsyncClient(GraphqlAsyncClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(MSGraphAsyncClient, self).__init__()
        self.client: GraphServiceClient | None = None

    @async_timed
    async def _load(self) -> None:
        await super(MSGraphAsyncClient, self)._load()

    @async_timed
    async def _connect(self) -> None:
        cred = CredentialBuilder().from_conf(self.conf["cred"]).build()

        # Sets the path to the certificate file
        if getattr(sys, "frozen", False):
            cacert = os.path.join(os.path.dirname(sys.executable), "lib", "certifi", "cacert.pem")
        else:
            cacert = certifi.where()
        os.environ["REQUESTS_CA_BUNDLE"] = cacert

        credential = ClientSecretCredential(tenant_id=cred.tenant_id,
                                            client_id=cred.client_id,
                                            client_secret=cred.secret,
                                            connection_verify=False)
        self.client = GraphServiceClient(credential, self.conf["scopes"])
        if self.client is None:
            raise

    @async_timed
    async def _send(self, mail: SendMailPostRequestBody, attempt_nb: int) -> Any:
        self.log.logger.debug("Send the mail '{}' (Attempt {})".format(mail.message.subject, attempt_nb))
        try:
            resp = await self.client.users.by_user_id(mail.message.from_escaped.email_address.address).send_mail.post(mail)
            if resp is None:
                self.log.logger.debug("The mail '{}' (Attempt {}) has been sent successfully".format(mail.message.subject,
                                                                                                     attempt_nb))
        except Exception as e:
            self.log.logger.error("The mail '{}' (Attempt {}) fails with the exception '{}'".format(mail.message.subject,
                                                                                                    attempt_nb,
                                                                                                    str(e)))
            raise e
        return resp

    @async_timed
    async def _send_with_retries(self, mail: SendMailPostRequestBody) -> Any:
        resp = None
        kwargs = {
                  "retry": (retry_if_result(lambda resp: resp is not None) |
                            retry_if_exception_type(asyncio.TimeoutError) |
                            retry_if_exception_type(asyncio.CancelledError)),
                  "before": before_log(self.log.logger, logging.DEBUG),
                  "after": after_log(self.log.logger, logging.DEBUG),
                  "reraise": True
                 }
        if self.is_connected:
            if "retries" in self.conf:
                retries = self.conf["retries"].get("total", 1)
                kwargs["stop"] = stop_after_attempt(retries)
        if "req_interval" in self.conf:
            kwargs["wait"] = wait_fixed(self.conf["req_interval"])
        try:
            async for attempt in AsyncRetrying(**kwargs):
                with attempt:
                    resp = await self._send(mail, attempt.retry_state.attempt_number)
                if not attempt.retry_state.outcome.failed:
                    attempt.retry_state.set_result(resp)
                    if resp is not None:
                        self.log.logger.error("The mail '{}' (Attempt {}) fails with the error '{}'".format(mail.message.subject,
                                                                                                            attempt.retry_state.attempt_number,
                                                                                                            resp))
        except RetryError:
            pass
        return resp

    @async_timed
    async def send(self, mail: SendMailPostRequestBody) -> None:
        kwargs = {
                  "retry": (retry_if_result(lambda resp: resp is not None) |
                            retry_if_exception_type(ValueError)),
                  "before": before_log(self.log.logger, logging.DEBUG),
                  "after": after_log(self.log.logger, logging.DEBUG)
                 }
        if "reconnect_interval" in self.conf:
            kwargs["wait"] = wait_fixed(self.conf["reconnect_interval"])
        reconnecting = False
        try:
            async for attempt in AsyncRetrying(**kwargs):
                resp = None
                with attempt:
                    if reconnecting:
                        await self.connect()
                        reconnecting = False
                    try:
                        resp = await self._send_with_retries(mail)
                    except ValueError as e:
                        if self.state != constant.STATE_CLOSED:
                            if "reconnect_interval" in self.conf:
                                self.log.logger.error("The mail '{}' fails : starting to reconnect after {} sec".format(mail.message.subject,
                                                                                                                        self.conf["reconnect_interval"]))
                            else:
                                self.log.logger.error("The mail '{}' fails : starting to reconnect".format(mail.message.subject))
                            await self.close()
                            reconnecting = True
                        raise e
                    if resp is not None and self.state != constant.STATE_CLOSED:
                        if "reconnect_interval" in self.conf:
                            self.log.logger.error("The mail '{}' fails : starting to reconnect after {} sec".format(
                                mail.message.subject,
                                self.conf["reconnect_interval"]))
                        else:
                            self.log.logger.error(
                                "The mail '{}' fails : starting to reconnect".format(mail.message.subject))
                        await self.close()
                        reconnecting = True
                if not attempt.retry_state.outcome.failed:
                    attempt.retry_state.set_result(resp)
        except RetryError:
            pass
        return resp

    @async_timed
    async def _close(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<MSGraphAsyncClient(id='{}')>".format(self.id)
