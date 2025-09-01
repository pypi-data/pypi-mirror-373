import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch, ANY, call
from pathlib import Path

# Try to import the module directly first
try:
    from src.reporting.email_sender import EmailSender
except ImportError:
    # If that fails, add the project root to the Python path and try again
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.reporting.email_sender import EmailSender


class TestEmailSender(unittest.TestCase):
    """Test cases for the EmailSender class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.smtp_server = "test.smtp.com"
        self.smtp_port = 587
        self.username = "test@example.com"
        self.password = "testpass"
        self.recipient = "recipient@example.com"
        
        # Create a test report file for attachment testing
        self.test_report_path = Path("test_report.html")
        with open(self.test_report_path, "w") as f:
            f.write("<h1>Test Report</h1>")
            
        # Create a mock SMTP server
        self.mock_smtp = MagicMock()
        
        # Mock SMTP server responses
        self.mock_smtp.login.return_value = (235, b'2.7.0 Authentication successful')
        self.mock_smtp.send_message.return_value = {}
        self.mock_smtp.noop.return_value = (250, b'OK')
        
        # Initialize EmailSender with test credentials and mock SMTP connection
        self.sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=self.username,
            password=self.password,
            smtp_connection=self.mock_smtp
        )
        
    def tearDown(self) -> None:
        """Clean up after tests."""
        # Clean up the test report file
        if self.test_report_path.exists():
            self.test_report_path.unlink()

    def test_send_email_success(self) -> None:
        """Test sending a basic email successfully."""
        # Test data
        subject = "Test Email"
        html_content = "<h1>Test Email</h1><p>This is a test email.</p>"

        # Call the method
        result = self.sender.send_email(
            to_email=self.recipient, 
            subject=subject, 
            html_content=html_content
        )

        # Assertions
        assert result is True
        self.mock_smtp.login.assert_called_once_with(self.username, self.password)
        self.mock_smtp.send_message.assert_called_once()
        
        # Verify the message was constructed correctly
        msg = self.mock_smtp.send_message.call_args[0][0]
        assert msg['Subject'] == subject
        # The email header format adds quotes around display names with spaces
        assert msg['From'] == f'"Stock Analysis Pro" <{self.username}>'
        assert msg['To'] == self.recipient

    def test_send_report_success(self):
        """Test sending a report successfully."""
        # Create a test report file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            report_path = f.name
            f.write("<h1>Test Report</h1><p>This is a test report.</p>")

        try:
            # Call the method with current signature
            result = self.sender.send_report(
                to_email=self.recipient,
                report_path=report_path,
                subject="Test Report",
                charts=[]
            )

            # Assertions
            assert result is True
            self.mock_smtp.login.assert_called_once_with(self.username, self.password)
            self.mock_smtp.send_message.assert_called_once()

            # Verify the message was constructed correctly
            msg = self.mock_smtp.send_message.call_args[0][0]
            assert msg['Subject'] == "Test Report"
            # The email header format adds quotes around display names with spaces
            assert msg['From'] == f'"Stock Analysis Pro" <{self.username}>'
            assert msg['To'] == self.recipient

        finally:
            # Clean up the test report file
            if os.path.exists(report_path):
                os.unlink(report_path)

    def test_send_email_with_attachments(self) -> None:
        """Test sending an email with attachments."""
        # Configure mock SMTP server
        self.mock_smtp.login.return_value = (235, b'2.7.0 Authentication successful')
        self.mock_smtp.send_message.return_value = {}

        # Test data
        subject = "Test Email with Attachment"
        html_content = "<h1>Test Email</h1><p>This email has an attachment.</p>"

        # Call the method
        result = self.sender.send_email(
            to_email=self.recipient,
            subject=subject,
            html_content=html_content,
            attachments=[str(self.test_report_path)]
        )

        # Assertions
        assert result is True
        self.mock_smtp.login.assert_called_once_with(self.username, self.password)
        self.mock_smtp.send_message.assert_called_once()

        # Verify the message was constructed correctly
        msg = self.mock_smtp.send_message.call_args[0][0]
        assert msg['Subject'] == subject
        # The email header format adds quotes around display names with spaces
        assert msg['From'] == f'"Stock Analysis Pro" <{self.username}>'
        assert msg['To'] == self.recipient

    def test_send_email_template_success(self):
        """Test sending an email with a template successfully."""
        # Create a test template in the project's templates directory
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        os.makedirs(template_dir, exist_ok=True)
        test_template = os.path.join(template_dir, "test_template.html")

        try:
            # Create test template
            with open(test_template, "w") as f:
                f.write("<h1>{{ title }}</h1><p>{{ message }}</p>")

            # Test data
            subject = "Test Template Email"
            context = {"title": "Test", "message": "This is a test email with template."}

            # Call the method
            result = self.sender.send_email(
                to_email=self.recipient,
                subject=subject,
                template_name="test_template.html",
                context=context
            )

            # Assertions
            assert result is True
            self.mock_smtp.login.assert_called_once_with(self.username, self.password)
            self.mock_smtp.send_message.assert_called_once()

            # Verify the message was constructed correctly
            msg = self.mock_smtp.send_message.call_args[0][0]
            assert msg['Subject'] == subject
            # The email header format adds quotes around display names with spaces
            assert msg['From'] == f'"Stock Analysis Pro" <{self.username}>'
            assert msg['To'] == self.recipient

        finally:
            # Clean up test template
            if os.path.exists(test_template):
                os.unlink(test_template)
            # Remove the templates directory if it's empty
            if os.path.exists(template_dir) and not os.listdir(template_dir):
                os.rmdir(template_dir)

    def test_send_email_failure(self) -> None:
        """Test handling of email sending failure."""
        # Configure mock SMTP server to raise an exception on login
        self.mock_smtp.login.side_effect = Exception("SMTP Connection Error")

        # Call the method
        result = self.sender.send_email(
            to_email=self.recipient,
            subject="Test Email",
            html_content="<p>This should fail</p>"
        )

        # Assertions
        assert result is False
        self.mock_smtp.login.assert_called_once_with(self.username, self.password)
        self.mock_smtp.quit.assert_not_called()  # Should not call quit if login fails


if __name__ == "__main__":
    unittest.main()
