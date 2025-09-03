# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-05 14:10:19
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Email methods.
"""


from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from .rbase import Base, throw
from .rdata import unique
from .ros import FileSourceBytes, read_file_bytes


__all__ = (
    'Email',
)


class Email(Base):
    """
    Email type.
    """


    def __init__(
        self,
        username: str,
        password: str
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        username : Email username.
        password : Email password.
        """

        # Handle parameter.
        host, port = self.get_server_address(username)

        # Set attribute.
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.smtp = SMTP(host, port)


    def get_server_address(
        self,
        email: str
    ) -> tuple[str, str]:
        """
        Get server address of email.

        Parameters
        ----------
        email : Email address.

        Returns
        -------
        Server address.
        """

        # Get.
        domain_name = email.split('@')[-1]
        host = 'smtp.' + domain_name
        port = 25

        return host, port


    def get_smtp(self) -> SMTP:
        """
        Get `SMTP` connection instance and login.

        Returns
        -------
        Instance.
        """

        # Login.
        response = self.smtp.login(self.username, self.password)
        code = response[0]
        if code != 235:
            throw(ConnectionError, response)

        return self.smtp


    def create_email(
        self,
        title: str | None,
        text: str | None,
        attachment: dict[str, bytes],
        show_from: str | None,
        show_to: list[str] | None,
        show_cc: list[str] | None
    ) -> str:
        """
        Create email content.

        Parameters
        ----------
        title : Email title.
        text : Email text.
        attachment : Email attachments dictionary.
            - `Key`: File name.
            - `Value`: File bytes data.
        show_from : Show from email address.
        show_to : Show to email addresses list.
        show_cc : Show carbon copy email addresses list.
        """

        # Handle parameter.
        if type(show_to) == list:
            show_to = ','.join(show_to)
        if type(show_cc) == list:
            show_cc = ','.join(show_cc)

        # Instance.
        mimes = MIMEMultipart()

        # Add.

        ## Title.
        if title is not None:
            mimes['subject'] = title
        
        ## Text.
        if text is not None:
            mime_text = MIMEText(text)
            mimes.attach(mime_text)

        ## Attachment.
        for file_name, file_bytes in attachment.items():
            mime_file = MIMEApplication(file_bytes)
            mime_file.add_header('Content-Disposition', 'attachment', filename=file_name)
            mimes.attach(mime_file)

        ## Show from.
        if show_from is not None:
            mimes['from'] = show_from

        ## Show to.
        if show_to is not None:
            mimes['to'] = show_to

        ## Show cc.
        if show_cc is not None:
            mimes['cc'] = show_cc

        # Create.
        email = mimes.as_string()

        return email


    def send_email(
        self,
        to: str | list[str],
        title: str | None = None,
        text: str | None = None,
        attachment: dict[str, FileSourceBytes] = {},
        cc: str | list[str] | None = None,
        show_from: str | None = None,
        show_to: str | list[str] | None = None,
        show_cc: str | list[str] | None = None
    ) -> None:
        """
        Send email.

        Parameters
        ----------
        to : To email addresses.
            - `str`: Email address, multiple comma interval.
            - `list[str]`: Email addresses list.
        title : Email title.
        text : Email text.
        attachment : Email attachments dictionary.
            - `Key`: File name.
            - `Value`: File bytes data source.
                `bytes`: File bytes data.
                `str`: File path.
                `BufferedIOBase`: File bytes IO.
        cc : Carbon copy email addresses.
            - `str`: Email address, multiple comma interval.
            - `list[str]`: Email addresses list.
        show_from : Show from email address.
            - `None`: Use attribute `self.username`.
            - `str`: Email address.
        show_to : Show to email addresses.
            - `None`: Use parameter `to`.
            - `str`: Email address, multiple comma interval.
            - `list[str]`: Email addresses list.
        show_cc : Show carbon copy email addresses.
            - `None`: Use parameter `cc`.
            - `str`: Email address, multiple comma interval.
            - `list[str]`: Email addresses list.
        """

        # Handle parameter.

        ## To.
        if type(to) == str:
            to = to.split(',')

        ## Cc.
        match cc:
            case None:
                cc = []
            case str():
                cc = cc.split(',')

        ## Show from.
        show_from = show_from or self.username

        ## Show to.
        show_to = show_to or to
        if type(show_to) == str:
            show_to = show_to.split(',')

        ## Show cc.
        show_cc = show_cc or cc
        if type(show_cc) == str:
            show_cc = show_cc.split(',')

        ## Attachment.
        for file_name, file_source in attachment.items():
            file_bytes = read_file_bytes(file_source)
            attachment[file_name] = file_bytes

        # Create email.
        email = self.create_email(
            title,
            text,
            attachment,
            show_from,
            show_to,
            show_cc
        )

        # Get SMTP.
        smtp = self.get_smtp()

        # Send email.
        to += cc
        to = unique(to)
        smtp.sendmail(
            self.username,
            to,
            email
        )


    __call__ = send_email


    def __del__(self) -> None:
        """
        Delete instance.
        """

        # Quit.
        self.smtp.quit()
