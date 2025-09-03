# Proofpoint Secure Email Relay Mail API Python Library

[![PyPI Downloads](https://static.pepy.tech/badge/ser-mail-api)](https://pepy.tech/projects/ser-mail-api)  
This library implements all the functions of the SER Email Relay API via Python.

## Requirements

- Python 3.9+
- `requests`
- `requests-oauth2client`
- `pysocks`
- Active Proofpoint SER API credentials

### Installing the Package

You can install the tool using the following command directly from GitHub:

```bash
pip install git+https://github.com/pfptcommunity/ser-mail-api-python.git
```

Alternatively, you can install the tool using pip:

```bash
# Note: This may not work on Ubuntu 24.04:
pip install ser-mail-api
```

If you encounter an error similar to the following:

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.

    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.

    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
```

You should install `pipx` or configure your own virtual environment and use the command referenced above:

```bash
pipx install ser-mail-api
```

## Features

- **Send Emails**: Easily compose and send emails with minimal code.
- **Support for Attachments**:
    - Attach files from disk
    - Encode attachments as Base64
    - Send byte[] attachments
- **Support for Inline HTML Content**:
    - Using the syntax `<img src="cid:logo">`
    - Content-ID can be set manually or auto-generated
- **HTML & Plain Text Content**: Supports both plain text and HTML email bodies.
- **Recipient Management**: Add `To`, `CC`, and `BCC` recipients with ease.
- **Reply Management**: Add `Reply-To` addresses to redirect replies.

## Quick Start

```python
import json
from ser_mail_api.v1 import *

if __name__ == "__main__":
    # Default region when not specified is Region.US
    client = Client("<client_id>", "<client_secret>", Region.US)

    # Create a new Message object
    message = Message("This is a test email", MailUser("sender@example.com", "Joe Sender"))

    # Add text content body
    message.add_content(Content("This is a test message", ContentType.Text))

    # Add HTML content body, with embedded image
    message.add_content(Content("<b>This is a test message</b><br><img src=\"cid:logo\">", ContentType.Html))

    # Create an inline attachment from disk and set the cid
    message.add_attachment(Attachment.from_file("C:/temp/logo.png", Disposition.Inline, "logo"))

    # Add recipients
    message.add_to(MailUser("recipient1@example.com", "Recipient 1"))
    message.add_to(MailUser("recipient2@example.com", "Recipient 2"))

    # Add CC
    message.add_cc(MailUser("cc1@example.com", "CC Recipient 1"))
    message.add_cc(MailUser("cc2@example.com", "CC Recipient 2"))

    # Add BCC
    message.add_bcc(MailUser("bcc1@example.com", "BCC Recipient 1"))
    message.add_bcc(MailUser("bcc2@example.com", "BCC Recipient 2"))

    # Add attachments
    message.add_attachment(Attachment.from_base64("VGhpcyBpcyBhIHRlc3Qh", "test.txt"))
    message.add_attachment(Attachment.from_file("C:/temp/file.csv"))
    message.add_attachment(Attachment.from_bytes(b"Sample bytes", "bytes.txt", "text/plain"))

    # Set one or more Reply-To addresses
    message.add_reply_to(MailUser("noreply@proofpoint.com", "No Reply"))

    # Send the email
    result = client.send(message)

    print("HTTP Response: {}/{}".format(result.get_status(), result.get_reason()))
    print("Reason:", result.reason)
    print("Message ID:", result.message_id)
    print("Request ID:", result.request_id)
```

## Attachment MIME Type Deduction Behavior

When creating attachments, the library automatically attempts to determine the MIME type. This detection is based on:

- The `filename` argument when using `Attachment.from_bytes` or `Attachment.from_base64`.
- The `filepath` when using `Attachment.from_file`.

If the MIME type cannot be determined, an exception will be raised.

```python
from ser_mail_api.v1 import *

if __name__ == "__main__":
    # Create an attachment from disk; the MIME type will be "application/vnd.ms-excel", and disposition will be "Disposition.Attachment"
    Attachment.from_file("C:/temp/file.csv")
    # This will throw an error, as the MIME type is unknown
    Attachment.from_file("C:/temp/file.unknown")
    # Create an attachment and specify the type information. The disposition will be "Disposition.Attachment", filename will be unknown.txt, and MIME type "text/plain"
    Attachment.from_file("C:/temp/file.unknown", filename="unknown.txt")
    # Create an attachment and specify the type information. The disposition will be "Disposition.Attachment", filename will be file.unknown, and MIME type "text/plain"
    Attachment.from_file("C:/temp/file.unknown", mime_type="text/plain")
```

## Inline Attachments and Content-IDs

When creating attachments, they are `Disposition.Attachment` by default. To properly reference a **Content-ID** (e.g.,
`<img src="cid:logo">`), you must explicitly set the attachment disposition to `Disposition.Inline`.
If the attachment type is set to `Disposition.Inline`, a default unique **Content-ID** will be generated.

### Using Dynamically Generated Content-ID

The example below demonstrates how to create inline content with a dynamically generated Content-ID inside an HTML
message body.

```python
from ser_mail_api.v1 import *

if __name__ == "__main__":
    # Default region when not specified is Region.US
    client = Client("<client_id>", "<client_secret>", Region.US)

    # Create a new Message object
    message = Message("This is a test email", MailUser("sender@example.com", "Joe Sender"))

    # Create an inline attachment with dynamically generated Content-ID
    logo = Attachment.from_file("C:/temp/logo.png", Disposition.Inline)

    # Add HTML content body, with embedded image
    message.add_content(Content(f"<b>This is a test message</b><br><img src=\"cid:{logo.cid}\">", ContentType.Html))

    # Add the attachment to the message
    message.add_attachment(logo)

    # Add recipients
    message.add_to(MailUser("recipient1@example.com", "Recipient 1"))

    # Send the email
    result = client.send(message)

    print("HTTP Response: {}/{}".format(result.get_status(), result.get_reason()))
    print("Reason:", result.reason)
    print("Message ID:", result.message_id)
    print("Request ID:", result.request_id)
```

### Setting a Custom Content-ID

The example below demonstrates how to create inline content with a custom Content-ID inside an HTML message body.

```python
from ser_mail_api.v1 import *

if __name__ == "__main__":
    # Default region when not specified is Region.US
    client = Client("<client_id>", "<client_secret>", Region.US)

    # Create a new Message object
    message = Message("This is a test email", MailUser("sender@example.com", "Joe Sender"))

    # Add an inline attachment with a custom Content-ID
    message.add_attachment(Attachment.from_file("C:/temp/logo.png", Disposition.Inline, "logo"))

    # Add HTML content body, with embedded image
    message.add_content(Content(f"<b>This is a test message</b><br><img src=\"cid:logo\">", ContentType.Html))

    # Add recipients
    message.add_to(MailUser("recipient1@example.com", "Recipient 1"))

    # Send the email
    result = client.send(message)

    print("HTTP Response: {}/{}".format(result.get_status(), result.get_reason()))
    print("Reason:", result.reason)
    print("Message ID:", result.message_id)
    print("Request ID:", result.request_id)
```

### Proxy Support

Socks5 Proxy Example:

```python
from ser_mail_api.v1 import *

if __name__ == '__main__':
    # Default region when not specified is Region.US
    client = Client("<client_id>", "<client_secret>", Region.US)
    credentials = "{}:{}@".format("proxyuser", "proxypass")
    client._session.proxies = {'https': "{}://{}{}:{}".format('socks5', credentials, '<your_proxy>', '8128')}
```

HTTP Proxy Example (Squid):

```python
from ser_mail_api.v1 import *

if __name__ == '__main__':
    # Default region when not specified is Region.US
    client = Client("<client_id>", "<client_secret>", Region.US)
    credentials = "{}:{}@".format("proxyuser", "proxypass")
    client._session.proxies = {'https': "{}://{}{}:{}".format('http', credentials, '<your_proxy>', '3128')}

```

### HTTP Timeout Settings

```python
from ser_mail_api.v1 import *

if __name__ == '__main__':
    # Default region when not specified is Region.US
    client = Client("<client_id>", "<client_secret>", Region.US)
    # Timeout in seconds, connect timeout
    client.timeout = 600
    # Timeout advanced, connect / read timeout
    client.timeout = (3.05, 27)
```

## Known Issues

There is a known issue where **empty file content** results in a **400 Bad Request** error.

```json
{
  "content": "",
  "disposition": "attachment",
  "filename": "empty.txt",
  "id": "1ed38149-70b2-4476-84a1-83e73913d43c",
  "type": "text/plain"
}
```

🔹 **API Response:**

```
Status Code: 400/BadRequest
Message ID:
Reason: attachments[0].content is required
Request ID: fe9a1acf60a20c9d90bed843f6530156
Raw JSON: {"request_id":"fe9a1acf60a20c9d90bed843f6530156","reason":"attachments[0].content is required"}
```

This issue has been reported to **Proofpoint Product Management**.

## Limitations
- The Proofpoint API currently does not support **empty file attachments**.
- If an empty file is sent, you will receive a **400 Bad Request** error.

## Additional Resources

For more information, refer to the official **Proofpoint Secure Email Relay API documentation**:  
[**API Documentation**](https://api-docs.ser.proofpoint.com/docs/email-submission)
