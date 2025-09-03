import json

from ser_mail_api.v1 import *

if __name__ == "__main__":
    # Load API key
    with open("../ser.api_key", "r") as api_key_file:
        api_key_data = json.load(api_key_file)

    client = Client(api_key_data.get("client_id"), api_key_data.get("client_secret"))

    # Create a new Message object
    message = Message("This is a test email", MailUser("sender@example.com", "Joe Sender"))

    # Add text content body
    message.add_content(Content("This is a test message", ContentType.Text))

    # Add html content body, with embedded image.
    message.add_content(Content("<b>This is a test message</b><br><img src=\"cid:logo\">", ContentType.Html))

    # Create an inline attachment from disk and set the cid.
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

    # Set or more Reply-To addresses
    message.add_reply_to(MailUser("noreply@proofpoint.com", "No Reply"))

    # Send the email
    result = client.send(message)

    print("HTTP Response: {}/{}".format(result.get_status(), result.get_reason()))
    print("Reason:", result.reason)
    print("Message ID:", result.message_id)
    print("Request ID:", result.request_id)
