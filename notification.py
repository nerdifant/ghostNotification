#!/usr/bin/env python

from lib.ghostclient import GhostClient
from lib.mailclient import MailClient
import json
import sys

def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')

    with open('config.json', 'r') as f:
        config = json.load(f)
    if config:
        ghostClient = GhostClient(config["ghost"])
        subscribers = ghostClient.getSubscribers(limit="all")
        posts = ghostClient.getPosts(filters="featured:true+page:false+status:published")

        mailClient = MailClient(config["mail"])
        for p in posts:
            print("> Sending notifications for " + p.title)
            if ghostClient.setPostUnfeatured(p):
                subject = "Neuer Blogeintrag: " + p.title
                content = "Hallo zusammen,\n\nes gibt einen neuen Eintrag in unserem Blog:\n"
                content += p.url
                content += "\n\n Das Passwort lautet: "
                content += ghostClient.blogPassword
                content += config["mail"]["signature"]
                for toMail in subscribers:
                    print("  > Sending mail to: " + toMail)
                    mailClient.sendMail(toMail, subject, content)
            else:
                print("  > Unfeatureing failed.")

        mailClient.teardown()
        return 0
    else:
        print("Error: Read config failed!")
        return 1

if __name__ == "__main__":
    exit(main())
