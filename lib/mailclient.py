#!/usr/bin/env python

import json
import smtplib
import datetime
from email.mime.text import MIMEText

class MailClient:
    def __init__(self, config):
        self.server = smtplib.SMTP(config["host"], config["port"])
        self.server.starttls()
        self.server.login(config["user"], config["password"])
        self.fromEmail = config["from-email"]

    def sendMail(self, toMail, subject, content):
        date = datetime.datetime.now().strftime( "%d/%m/%Y %H:%M" )
        msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" \
            % ( self.fromEmail, toMail, subject, date, content )
        self.server.sendmail(self.fromEmail, toMail, msg)

    def teardown(self):
        self.server.quit()

def main():
    with open('../config.json', 'r') as f:
        config = json.load(f)
    if config:
        mailClient = MailClient(config["mail"])
        mailClient.sendMail(config["mail"]["from-email"], "Test Content", "Test Subject")
        mailClient.teardown()
        return 0
    else:
        print("Error: Read config failed!")
        return 1

if __name__ == "__main__":
    exit(main())
