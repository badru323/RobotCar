import requests
import time
import json

class VPFSClient:
    # MUST adjust these values dependent on the keys/ip etc.
    def __init__(self, server_ip, team, auth_key):                  
        self.server_ip = server_ip
        self.team = team
        self.auth_key = auth_key
        self.base_url = f"http://{self.server_ip}:5000"

    # GET /match?auth=<auth>
    def check_match(self):
        url = f"{self.base_url}/match?auth={self.auth_key}"
        try:
            res = requests.get(url)
            if res.status_code == 200:
                return res.json()
            else:
                print("check_match() HTTP error:", res.status_code)
                return None
        except Exception as e:
            print("check_match() exception:", e)
            return None

    # GET /fares?all=[True|False]
    def get_fares(self, include_all=False):
        url = f"{self.base_url}/fares"
        if include_all:
            url += "?all=True"
        try:
            res = requests.get(url)
            if res.status_code == 200:
                return res.json()
            else:
                print("get_fares() HTTP error:", res.status_code)
                return []
        except Exception as e:
            print("get_fares() exception:", e)
            return []

    # POST /fares/claim/<fare_id>?auth=<auth>
    def claim_fare(self, fare_id):
        url = f"{self.base_url}/fares/claim/{fare_id}?auth={self.auth_key}"
        try:
            res = requests.get(url)  # Using GET or POST depends on server design; the doc says GET
            if res.status_code == 200:
                data = res.json()
                return data.get("success", False), data.get("message", "")
            else:
                print("claim_fare() HTTP error:", res.status_code)
                return False, "HTTP Error"
        except Exception as e:
            print("claim_fare() exception:", e)
            return False, str(e)

    # GET /fares/current/<team>
    def get_current_fare(self):
        url = f"{self.base_url}/fares/current/{self.team}"
        try:
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                # data[0] expected as per the docs
                if data and len(data) > 0:
                    return data[0]
            else:
                print("get_current_fare() HTTP error:", res.status_code)
                return None
        except Exception as e:
            print("get_current_fare() exception:", e)
            return None

    # GET /WhereAmI/<team>
    def get_position(self):
        url = f"{self.base_url}/WhereAmI/{self.team}"
        try:
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                if data and len(data) > 0:
                    return data[0]
            else:
                print("get_position() HTTP error:", res.status_code)
                return None
        except Exception as e:
            print("get_position() exception:", e)
            return None
