import unittest
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from velocity.misc.mail import (
    Attachment,
    get_full_emails,
    get_address_only,
    parse_attachment,
    parse,
)
import hashlib


class TestEmailProcessing(unittest.TestCase):

    def test_get_full_emails(self):
        """Test that email addresses with names are formatted correctly."""
        mock_address = [
            type(
                "Address",
                (),
                {"mailbox": b"john", "host": b"example.com", "name": b"John Doe"},
            ),
            type(
                "Address",
                (),
                {"mailbox": b"jane", "host": b"example.com", "name": None},
            ),
        ]
        result = get_full_emails(mock_address)
        self.assertEqual(result, ["John Doe <john@example.com>", "jane@example.com"])

    def test_get_address_only(self):
        """Test that only email addresses without names are returned."""
        mock_address = [
            type("Address", (), {"mailbox": b"john", "host": b"example.com"}),
            type("Address", (), {"mailbox": b"jane", "host": b"example.com"}),
        ]
        result = get_address_only(mock_address)
        self.assertEqual(result, ["john@example.com", "jane@example.com"])

    def test_attachment_initialization(self):
        """Test the initialization of the Attachment class."""
        data = b"file data"
        attachment = Attachment(name="file.txt", data=data)
        self.assertEqual(attachment.name, "file.txt")
        self.assertEqual(attachment.data, data)
        self.assertEqual(attachment.size, len(data))
        self.assertEqual(attachment.ctype, "text/plain")
        self.assertEqual(attachment.hash, hashlib.sha1(data).hexdigest())

    def test_parse_attachment(self):
        """Test parsing a valid attachment from a message part."""
        part = MIMEApplication(b"Test file data", Name="test.txt")
        part["Content-Disposition"] = 'attachment; filename="test.txt"'
        attachment = parse_attachment(part)
        self.assertIsInstance(attachment, Attachment)
        self.assertEqual(attachment.name, "test.txt")
        self.assertEqual(attachment.ctype, "text/plain")
        self.assertEqual(attachment.data, b"Test file data")

    def test_parse_attachment_none(self):
        """Test that parse_attachment returns None if there's no attachment."""
        part = MIMEText("This is a plain text email part")
        self.assertIsNone(parse_attachment(part))

    def test_parse_plain_text_email(self):
        """Test parsing a plain text email."""
        msg = MIMEText("This is a plain text email")
        msg["Content-Type"] = "text/plain"
        result = parse(msg.as_string())
        self.assertEqual(result["body"], "This is a plain text email")
        self.assertIsNone(result["html"])
        self.assertEqual(result["attachments"], [])

    def test_parse_html_email(self):
        """Test parsing an HTML email."""
        msg = MIMEText("<p>This is an HTML email</p>", "html")
        msg["Content-Type"] = "text/html"
        result = parse(msg.as_string())
        self.assertEqual(result["html"], "<p>This is an HTML email</p>")
        self.assertIsNone(result["body"])
        self.assertEqual(result["attachments"], [])

    def test_parse_multipart_email_with_attachments(self):
        """Test parsing a multipart email with attachments."""
        msg = MIMEMultipart()
        msg.attach(MIMEText("This is a plain text part", "plain"))
        msg.attach(MIMEText("<p>This is an HTML part</p>", "html"))

        attachment_part = MIMEApplication(b"Attachment data", Name="attachment.txt")
        attachment_part["Content-Disposition"] = 'attachment; filename="attachment.txt"'
        msg.attach(attachment_part)

        result = parse(msg.as_string())
        self.assertEqual(result["body"], "This is a plain text part")
        self.assertEqual(result["html"], "<p>This is an HTML part</p>")
        self.assertEqual(len(result["attachments"]), 1)
        self.assertEqual(result["attachments"][0].name, "attachment.txt")
        self.assertEqual(result["attachments"][0].data, b"Attachment data")

    def test_parse_empty_email(self):
        """Test parsing an empty email string."""
        result = parse("")
        self.assertIsNone(result["body"])
        self.assertIsNone(result["html"])
        self.assertEqual(result["attachments"], [])


if __name__ == "__main__":
    unittest.main()
