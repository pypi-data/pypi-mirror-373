#!/usr/local/bin/python
from email.parser import Parser as EmailParser
from email.message import Message
from typing import List, Optional
import mimetypes
import hashlib


class NotSupportedMailFormat(Exception):
    """Exception raised for unsupported mail formats."""

    pass


class Attachment:
    """Represents an email attachment."""

    def __init__(self, name: str, data: bytes):
        self.name = name
        self.data = data
        self.ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        self.size = len(data)
        self.hash = hashlib.sha1(data).hexdigest()


def get_full_emails(addresses: List) -> List[str]:
    """Generates a list of formatted email addresses with names."""
    results = []
    for a in addresses:
        mailbox = a.mailbox.decode("utf-8")
        host = a.host.decode("utf-8")
        name = a.name.decode("utf-8") if a.name else None
        if name:
            results.append(f"{name} <{mailbox}@{host}>")
        else:
            results.append(f"{mailbox}@{host}")
    return results


def get_address_only(addresses: List) -> List[str]:
    """Generates a list of email addresses without names."""
    return [f"{a.mailbox.decode('utf-8')}@{a.host.decode('utf-8')}" for a in addresses]


def parse_attachment(part: Message) -> Optional[Attachment]:
    """Parses an attachment from a message part if present."""
    content_disposition = part.get("Content-Disposition")
    if content_disposition:
        dispositions = content_disposition.strip().split(";")
        if dispositions[0].lower() == "attachment":
            name = part.get_filename()
            data = part.get_payload(decode=True)
            if name and data:
                return Attachment(name=name, data=data)
    return None


def parse(content: str) -> dict:
    """Parses the email content and extracts plain text, HTML, and attachments."""
    body = bytearray()
    html = bytearray()
    attachments = []

    message = EmailParser().parsestr(content)
    for part in message.walk():
        attachment = parse_attachment(part)
        if attachment:
            attachments.append(attachment)
        elif part.get_content_type() == "text/plain":
            body.extend(part.get_payload(decode=True) or b"")
        elif part.get_content_type() == "text/html":
            html.extend(part.get_payload(decode=True) or b"")

    return {
        "body": body.decode("utf-8") if body else None,
        "html": html.decode("utf-8") if html else None,
        "attachments": attachments,
    }
