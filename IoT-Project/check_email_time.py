import email.utils
from datetime import datetime, timedelta
import smtplib, ssl
import imaplib
import easyimap as imap
from email.header import decode_header
import email
import traceback
from bluepy.btle import Scanner
import mysql.connector
from mysql.connector import Error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

def checkFanReply():
    global emailReceived
    sender_email = '2003igorok@gmail.com'
    sender_password = 'vukx tyxh ytnf kbzr'
    # Connect to the Gmail server
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(sender_email, sender_password)
    
    # Select the mailbox (inbox in this case)
    mail.select("inbox")

    # Search for all emails and get the latest one
    status, messages = mail.search(None, 'ALL')
    if status == 'OK':
        email_ids = messages[0].split()
        if email_ids:
            latest_email_id = email_ids[-1]
            print(latest_email_id)
            # Fetch the latest email
            status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
            if status == 'OK':
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Get the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")

                # Get the email date
                email_date = email.utils.parsedate(msg.get("Date"))
                if email_date:
                    email_datetime = datetime(*email_date[:6])
                    print(email_datetime)
                    current_datetime = datetime.now()
                    print(current_datetime)

                    # Check if the email is received within the last 30 seconds
                    if (current_datetime - email_datetime).total_seconds() <= 60:
                        # Get the email body
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')

                        # Check if the subject is "It is getting hot" and the body contains "YES"
                        if "It is getting hot" in subject and "YES" in body.upper():
                            print("there is a yes in the email")
                            emailReceived = True
                            return True

    # Close the connection
    mail.close()
    mail.logout()
    emailReceived = False
    return False

print(checkFanReply())