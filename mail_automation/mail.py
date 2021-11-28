import os
import smtplib
import ssl
import config
from dotenv import load_dotenv


class SendMail:

    def __init__(self, message, receiver_email):
        """

        :param sender_email: email of the sender
        :param sender_password: password of the sender
        :param receiver_email: email of the receiver
        :param message: message to be sent
        """
        try:
            self.port = 465
            self.smtp_server = "smtp.gmail.com"
            load_dotenv('env/email_credentials.env')
            self.sender_email = os.getenv("EMAIL")
            self.sender_password = os.getenv("PASSWORD")
            self.receiver_email = receiver_email
            self.message = message
        except Exception as e:
            config.logger.log("ERROR", str(e))

    def send(self):
        """

        :return: True, if message was sent successfully
                 False, if some error occurred.
        """
        try:
            config.logger.log("INFO", "Sending confirmation mail to user...")
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.receiver_email, self.message)
            server.close()
            config.logger.log("INFO", "Mail sent")
            return True
        except smtplib.SMTPRecipientsRefused:
            config.logger.log("ERROR", "Invalid mail provided")
            return False
        except Exception as e:
            config.logger.log("ERROR", str(e))
            return False
