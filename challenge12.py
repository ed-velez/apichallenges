#!/usr/bin/env python
import os
import sys
import requests
from werkzeug.datastructures import MultiDict
import json

def main():

    url = "https://api.mailgun.net/v2/routes"

    with open(os.path.expanduser("~/.mailgun")) as f:
            key = f.read()
    payload=MultiDict([("priority", 1),
                    ("description", "Challenge 12"),
                    ("expression", "match_recipient('ed.velez@apichallenges.mailgun.org')"),
                    ("action", "forward(' http://cldsrvr.com/challenge1')"),
                    ("action", "stop()")])

    r = requests.post(url, auth=('api', key.rstrip()), data=payload)

    print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == '__main__':
    main()
