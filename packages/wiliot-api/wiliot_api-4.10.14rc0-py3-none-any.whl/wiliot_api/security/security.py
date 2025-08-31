"""
Copyright (c) 2016- 2025, Wiliot Ltd. All rights reserved.

Redistribution and use of the Software in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

  2. Redistributions in binary form, except as used in conjunction with
  Wiliot's Pixel in a product or a Software update for such product, must reproduce
  the above copyright notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the distribution.

  3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
  may be used to endorse or promote products or services derived from this Software,
  without specific prior written permission.

  4. This Software, with or without modification, must only be used in conjunction
  with Wiliot's Pixel or with Wiliot's cloud service.

  5. If any Software is provided in binary form under this license, you must not
  do any of the following:
  (a) modify, adapt, translate, or create a derivative work of the Software; or
  (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
  discover the source code or non-literal aspects (such as the underlying structure,
  sequence, organization, ideas, or algorithms) of the Software.

  6. If you create a derivative work and/or improvement of any Software, you hereby
  irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
  royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
  right and license to reproduce, use, make, have made, import, distribute, sell,
  offer for sale, create derivative works of, modify, translate, publicly perform
  and display, and otherwise commercially exploit such derivative works and improvements
  (as applicable) in conjunction with Wiliot's products and services.

  7. You represent and warrant that you are not a resident of (and will not use the
  Software in) a country that the U.S. government has embargoed for use of the Software,
  nor are you named on the U.S. Treasury Department’s list of Specially Designated
  Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
  You must not transfer, export, re-export, import, re-import or divert the Software
  in violation of any export or re-export control laws and regulations (such as the
  United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
  and use restrictions, all as then in effect

THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
(SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
(A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
(B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
(C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
import requests
import pickle
import urllib.parse
from datetime import datetime, timedelta
import threading
import base64


class WiliotTokenError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class BadRequestError(Exception):
    pass


class WiliotAuthentication:
    def __init__(self, base_path, oauth_username=None, oauth_password=None, api_key=None):
        # Caller must provide either a username+password or an api key
        if not (all([oauth_username, oauth_password]) or api_key):
            raise Exception('Caller must provide either oauth_username and oath password or an api_key')
        self.base_path = base_path
        self.username = oauth_username
        self.password = oauth_password
        self.api_key = api_key
        self.min_token_duration = 0
        self.token = None
    
    def _get_token_from_server_with_username_password(self):
        url = self.base_path + "auth/token?" + urllib.parse.urlencode(
            {"username": self.username, "password": self.password})
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise BadRequestError
        elif response.status_code == 401:
            raise UnauthorizedError
        else:
            print(f"Failed to generate token with an unexpected error: {response.status_code}, {response.text}")
    
    def _get_token_from_server_with_api_key(self):
        url = self.base_path + "auth/token/api"
        headers = {
            'Authorization': self.api_key
        }
        try:
            response = requests.post(url, headers=headers)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(e.args)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise BadRequestError
        elif response.status_code == 401:
            raise UnauthorizedError
        else:
            print(f"Failed to generate token with an unexpected error: {response.status_code}, {response.text}")
    
    def _get_token_from_server(self):
        # Try authenticating with a username and password first
        if all([self.username, self.password]):
            try:
                auth_res = self._get_token_from_server_with_username_password()
            except BadRequestError as e:
                print("Bad request")
                # A bad request most likely means that the token needs to be obtained with an API key
                # Try authenticating with an API key if one has been provided
                if self.api_key is not None:
                    auth_res = self._get_token_from_server_with_api_key()
                else:
                    raise e
        elif self.api_key is not None:
            auth_res = self._get_token_from_server_with_api_key()
        return auth_res
    
    def get_token(self):
        self.token = self._get_token_from_server()
        # Add an "expires_on" field to reflect the date and this token will expire
        self.token["expires_on"] = datetime.now() + timedelta(seconds=self.token["expires_in"])
        
        return self.token["access_token"]
    
    def token_expired(self):
        return self.token is None or self.token["expires_on"] < datetime.now() + timedelta(minutes=1)
    
    def set_min_token_duration(self, min_token_duration):
        self.min_token_duration = min_token_duration
