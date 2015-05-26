import base64
import hmac
import json
import requests
import time
import datetime
import urllib
import os
import uuid
import re

from hashlib import sha1
from hashlib import md5
import numpy as np

class YakGrabber:
	def __init__(self):
		self.base_url = "https://us-east-api.yikyakapi.net/api/"
		self.user_agent = "Dalvik/1.6.0 (Linux; U; Android 4.3; Samsung Galaxy S4 - 4.3 - API 18 - 1080x1920 Build/JLS36G)"
		self.key = "EF64523D2BD1FA21F18F5BC654DFC41B"
# user_agent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"

	def sign_request(self, page, params):
	    #The salt is just the current time in seconds since epoch
	    salt = str(int(time.time()))

	    #The message to be signed is essentially the request, with parameters sorted
	    msg = "/api/" + page
	    sorted_params = list(params.keys())
	    sorted_params.sort()
	    if len(params) > 0:
	        msg += "?"
	    for param in sorted_params:
	        msg += "%s=%s&" % (param, params[param])
	    #Chop off last "&"
	    if len(params) > 0:
	        msg = msg[:-1]

	    #the salt is just appended directly
	    msg += salt

	    #Calculate the signature
	    h = hmac.new(self.key.encode(), msg.encode(), sha1)
	    hash = base64.b64encode(h.digest())

	    return hash, salt

	def get(self, page, params):
	    url = self.base_url + page

	    hash, salt = self.sign_request(page, params)
	    params['hash'] = hash
	    params['salt'] = salt

	    headers = {
	        "User-Agent": self.user_agent,
	        "Accept-Encoding": "gzip",
	        #"Cookie": "lat=" + self.location.latitude + "; long=" + self.location.longitude + "; pending=deleted; expires=Thu,01-Jan-1970 00:00:01 GMT;Max-Age=0",
	    }
	    
	    # print("===============", url, params, headers)
	    return requests.get(url, params=params, headers=headers)

	def fetch_yaks(self):
		params = {
		    "userID": "00000000-0000-0000-0000-000000000000", #self.id
		    "userLat": "37.4274745", #self.location.latitude,
		    "userLong": "-122.169719" #self.location.longitude,
		}
		response = self.get("getMessages", params)
		return np.array(json.loads(response.text)["messages"])
