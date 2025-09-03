#  Copyright (c) 2022 bastien.saltel
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
import asyncio
import logging
from abc import ABC,                                                    \
                abstractmethod
from typing import Any
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.file_attachment import FileAttachment
from tenacity.asyncio import AsyncRetrying
from tenacity.retry import retry_if_not_result,                         \
                           retry_if_result,                             \
                           retry_if_exception_type
from tenacity.stop import stop_after_attempt,                           \
                          stop_after_delay
from tenacity.wait import wait_fixed
from tenacity import RetryError
from tenacity.before import before_log
from tenacity.after import after_log

from galaxy.service import constant
from galaxy.utils.base import Component,                                \
                              Configurable
from galaxy.utils.pattern import Builder
from galaxy.service.service import Manager,                             \
                                   AsyncManager,                        \
                                   Service,                             \
                                   AsyncService,                        \
                                   LogService,                          \
                                   LogAsyncService
from galaxy.comm.graphql.graphql import MSGraphAsyncClient
from galaxy.perfo.decorator import timed,                               \
                                   async_timed

class MailBuilder(Component, Configurable, Builder, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        Builder.__init__(self)
        self.log: [LogService, LogAsyncService, None] = None
        self._title: str | None = None
        self._to: str | None = None
        self._text_body: str | None = None
        self._html_body: str | None = None
        self._cc: list | None = None
        self._bcc: list | None = None
        self._from: str | None = None
        self._attachments: list | None = None

    def _load(self) -> None:
        super(MailBuilder, self)._load()

    def title(self, title: str) -> "MailBuilder":
        self._title = title
        return self

    def to(self, to: str) -> "MailBuilder":
        self._to = to
        return self

    def text_body(self, text_body: str) -> "MailBuilder":
        self._text_body = text_body
        return self

    def html_body(self, html_body: str) -> "MailBuilder":
        self._html_body = html_body
        return self

    def cc(self, cc: list) -> "MailBuilder":
        self._cc = cc
        return self

    def bcc(self, bcc: list) -> "MailBuilder":
        self._bcc = bcc
        return self

    def from_(self, from_: str) -> "MailBuilder":
        self._from = from_
        return self

    def attachments(self, attachments: list) -> "MailBuilder":
        self._attachments = attachments
        return self

    def from_conf(self, conf: dict, **kwargs) -> "MailBuilder":
        # To
        if "to" in conf:
            self._to = conf["to"]

        # CC
        if "cc" in conf:
            self._cc = conf["cc"]

        # BCC
        if "bcc" in conf:
            self._bcc = conf["bcc"]

        # From
        if "from" in conf:
            self._from = conf["from"]

        return self

    @abstractmethod
    def build(self) -> Any:
        raise NotImplementedError("Should implement build()")


class MSGraphMailBuilder(MailBuilder):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(MSGraphMailBuilder, self).__init__()

    def build(self) -> SendMailPostRequestBody:
        message = Message()
        message.subject = self._title

        if self._text_body is not None:
            message.body = ItemBody(content_type=BodyType.Text, content=self._text_body)
        elif self._html_body is not None:
            message.body = ItemBody(content_type=BodyType.Html, content=self._html_body)
        if self._from is not None:
            message.from_escaped = Recipient(email_address=EmailAddress(address=self._from))
        message.to_recipients = [Recipient(email_address=EmailAddress(address=to_recipient)) for to_recipient in self._to]
        if self._cc is not None:
            message.cc_recipients = [Recipient(email_address=EmailAddress(address=cc_recipient)) for cc_recipient in self._cc]
        if self._bcc is not None:
            message.bcc_recipients = [Recipient(email_address=EmailAddress(address=bcc_recipient)) for bcc_recipient in self._bcc]
        if self._attachments is not None:
            message.attachments = []
            for attachment in self._attachments:
                with open(attachment, "rb") as f:
                    message.attachments.append(FileAttachment(odata_type="#microsoft.graph.fileAttachment",
                                                              name=os.path.basename(attachment),
                                                              content_type="application/vnd.ms-excel",
                                                              content_bytes=f.read()))
        return SendMailPostRequestBody(message=message)


class MailService(Service, ABC):
    """
    classdocs
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super(MailService, self).__init__()
        self.log: LogService | None = None

    @abstractmethod
    def send(self) -> None:
        raise NotImplementedError("Should implement send()")

    def __repr__(self) -> str:
        return "<MailService(id='{}')>".format(self.id)


class MailAsyncService(AsyncService, ABC):
    """
    classdocs
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super(MailAsyncService, self).__init__()
        self.log: LogAsyncService | None = None

    @abstractmethod
    async def send(self, mail: Any) -> None:
        raise NotImplementedError("Should implement send()")

    def __repr__(self) -> str:
        return "<MailAsyncService(id='{}')>".format(self.id)


class MSGraphMailAsyncService(MailAsyncService):
    """
    classdocs
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super(MSGraphMailAsyncService, self).__init__()
        self.mail_builders: dict[str, MSGraphMailBuilder] | None = None
        self.client: MSGraphAsyncClient | None = None

    async def _load(self) -> None:
        await super(MailAsyncService, self)._load()
        for mail_builder in self.mail_builders.values():
            mail_builder._load()
            mail_builder.from_conf(mail_builder.conf)

    async def _start(self) -> None:
        pass

    async def _stop(self) -> None:
        pass

    @async_timed
    async def send(self, mail: SendMailPostRequestBody) -> None:
        await self.client.send(mail)

    def __repr__(self) -> str:
        return "<MSGraphMailAsyncService(id='{}')>".format(self.id)


class MailManager(Manager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(MailManager, self).__init__()

    def __repr__(self) -> str:
        return "<MailManager(id='{}')>".format(self.id)


class MailAsyncManager(AsyncManager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(MailAsyncManager, self).__init__()

    def __repr__(self) -> str:
        return "<MailAsyncManager(id='{}')>".format(self.id)
