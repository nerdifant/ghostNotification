#!/usr/bin/env python

import urllib
from urllib2 import Request, urlopen, URLError
import datetime
import json
import ssl

class Post:
    def __init__(self):
        self.id = ""
        self.title = ""
        self.url = ""
        self.author = ""

class GhostClient:
    def __init__(self, config):
        self.url = config['url']
        self.context = ssl._create_unverified_context()
        self.config = self._getConfiguration()
        self.token,self.tokenType = self._getToken(config['auth'])
        self.blogPassword = self._getBlogPassword()

    def getPosts(self, fields=None, filters=None):
        posts = []
        opts = {"fields":"id,title,published_at,published_by,url"}
        if filters: opts["filter"]=filters
        data = self._openUrl("posts/?" + urllib.urlencode(opts))["posts"]
        for d in data:
            p = Post()
            p.id = d['id']
            p.title = d['title']
            p.url = self.url + d['url']
            p.author = self._getUserNameById(d['published_by'])
            posts.append(p)
        return posts

    def getSubscribers(self, limit=None, filters=None):
        subscribers = []
        opts = {"fields":"email"}
        if limit: opts["limit"]=limit
        if filters: opts["filter"]=filters
        data = self._openUrl("subscribers/?" + urllib.urlencode(opts))["subscribers"]
        for d in data:
            subscribers.append(d["email"])
        return subscribers

    def setPostUnfeatured(self, post):
        date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        data = self._openUrl("posts/" + post.id)
        data["posts"][0]["featured"] = False
        resp = self._openUrl("posts/" + post.id + "/", json.dumps(data), reqType = 'PUT', contentType = 'application/json')
        if data["posts"][0]["featured"] == resp["posts"][0]["featured"]:
            return True
        return False

    def _getConfiguration(self):
        return self._openUrl("configuration/")["configuration"]

    def _getBlogPassword(self):
        conf = self._openUrl("settings/?type=private")["settings"]
        for config in conf:
            if config["key"] == "password":
                return config["value"]
        return False

    def _getUserNameById(self, id):
        return self._openUrl("users/"+ id)["users"][0]["name"]

    def _getToken(self, auth):
        # Post ghost email/password to obtain auth token.
        # curl -i \
        #   -H "Accept: application/json" \
        #   -H "Content-Type: application/x-www-form-urlencoded" \
        #   -X POST -d "grant_type=password&username=<user-email>&password=<user-password>&client_id=<client-id>&client_secret=<client-secret>" \
        #   https://<subdomain>.ghost.io/ghost/api/v0.1/authentication/token
        auth["grant_type"] = "password"
        auth["client_id"] = "ghost-admin"
        auth["client_secret"] = "c9bb0cce2d61"
        resp = self._openUrl("authentication/token/", urllib.urlencode(auth))
        return resp["access_token"], resp ["token_type"]

    def _openUrl(self, path, data = None, reqType = False, contentType = 'application/x-www-form-urlencoded'):
        req = Request(self.url + "/ghost/api/v0.1/" + path, data)
        req.add_header('Accept', 'application/json')
        req.add_header('Content-Type', contentType)
        if hasattr(self, 'token'): req.add_header('Authorization', self.tokenType + ' ' + self.token)
        if reqType: req.get_method = lambda: reqType
        try:
            resp = urlopen(req, context = self.context)
        except URLError as e:
            if hasattr(e, 'reason'):
                print("Failed to get data from " + self.url + ": " + e.reason)
            elif hasattr(e, 'code'):
                print ("Error code: " + e.code)
            return
        return json.loads(resp.read())

def main():
    with open('../config.json', 'r') as f:
        config = json.load(f)
    if config:
        ghostClient = GhostClient(config["ghost"])
        subscribers = ghostClient.getSubscribers(limit="all")
        posts = ghostClient.getPosts(filters="featured:true+page:false+status:published")

        print(ghostClient.blogPassword)
        print(subscribers)
        for p in posts:
            print(p.title)
            print(p.url)
            print(p.author)
        return 0
    else:
        print("Error: Read config failed!")
        return 1

if __name__ == "__main__":
    exit(main())
