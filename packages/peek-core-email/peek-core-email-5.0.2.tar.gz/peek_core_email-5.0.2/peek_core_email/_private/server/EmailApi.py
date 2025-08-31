import logging
import os
import smtplib
from email.mime.text import MIMEText
from smtplib import SMTPException
from typing import List

from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_core_email._private.storage import Setting
from peek_core_email._private.storage.Setting import globalSetting
from peek_core_email.server.EmailApiABC import EmailApiABC

logger = logging.getLogger(__name__)


class EmailApi(EmailApiABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    def shutdown(self):
        pass

    @deferToThreadWrapWithLogger(logger)
    def sendSms(self, mobile: str, contents: str) -> None:
        session = self._ormSessionCreator()

        try:
            settings = globalSetting(session)

            if not settings[Setting.EMAIL_ENABLED]:
                logger.debug(
                    "SMS sending is disabled, not sending to '%s' for : %s",
                    mobile,
                    contents,
                )
                return

            smsEmailPostfix = settings[Setting.SMS_NUMBER_EMAIL_POSTFIX]

            if "@" in mobile:
                email = mobile
            else:
                email = mobile + smsEmailPostfix

            email = email.replace("+", "")

            self._sendBlocking(
                smtpHost=settings[Setting.EMAIL_SMTP_HOST],
                sender=settings[Setting.EMAIL_SENDER],
                message=contents,
                subject="",
                recipients=[email],
                html=False,
            )

        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def sendEmail(
        self, addresses: List[str], subject: str, contents: str, isHtml: bool
    ) -> None:
        session = self._ormSessionCreator()

        try:
            settings = globalSetting(session)

            if not settings[Setting.EMAIL_ENABLED]:
                logger.debug(
                    "Email sending is disabled, not sending to '%s' for : %s",
                    addresses,
                    subject,
                )
                return

            self._sendBlocking(
                smtpHost=settings[Setting.EMAIL_SMTP_HOST],
                sender=settings[Setting.EMAIL_SENDER],
                message=contents,
                subject=subject,
                recipients=addresses,
                html=isHtml,
            )

        finally:
            session.close()

    def _sendBlocking(
        self,
        smtpHost: str,
        sender: str,
        message: str,
        subject: str,
        recipients: List[str],
        html=False,
    ):
        """
        Send email to one or more addresses.
        """

        if not recipients:
            raise Exception("Recipient is missing")

        msg = MIMEText(message, "html" if html else "plain")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)
        msg.preamble = subject

        try:
            # Send the message via our own SMTP server.
            s = smtplib.SMTP(smtpHost, timeout=10)
            if os.getenv("PEEK_SMTP_NEEDS_LOGIN_AND_TLS"):
                s.starttls()
                s.login(
                    os.getenv("PEEK_SMTP_USER"), os.getenv("PEEK_SMTP_PASS")
                )
            s.send_message(msg)
            s.quit()

        except SMTPException as e:
            logger.exception(e)
            raise Exception(
                "Peek failed to send your email, please contact Peek admins."
            )
