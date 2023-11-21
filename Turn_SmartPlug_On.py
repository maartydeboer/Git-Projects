import requests
import uuid
import json

def get_tplink_token(username, password):
    url = "https://eu-wap.tplinkcloud.com"
    terminal_uuid = str(uuid.uuid4())
    payload = {
        "method": "login",
        "params": {
            "appType": "Kasa_Android",
            "cloudUserName": username,
            "cloudPassword": password,
            "terminalUUID": terminal_uuid
        }
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['result']['token']
    except Exception as e:
        print(f"Error getting token: {e}")

def get_device_list(token):
    url = f"https://eu-wap.tplinkcloud.com/?token={token}"
    payload = {
        "method": "getDeviceList"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['result']['deviceList']
    except Exception as e:
        print(f"Error retrieving devices: {e}")

def get_timer_info(token, device_id):
    url = f"https://eu-wap.tplinkcloud.com/?token={token}"
    headers = {"Content-Type": "application/json"}

    payload = {
        "method": "passthrough",
        "params": {
            "deviceId": device_id,
            "requestData": "{\"count_down\":{\"get_rules\":null}}"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        responseData = json.loads(data['result']['responseData'])
        rule_list = responseData['count_down']['get_rules']['rule_list']
        if rule_list:
            for rule in rule_list:
                print(f"Timer-ID: {rule['id']}, Timer-Name: {rule['name']}")
            return rule_list[0]['id']  # Takes first timer id
        else:
            print("No timer found.")
            return None
    except Exception as e:
        print(f"Error requesting timer information: {e}")

def set_timer(token, device_id, delay, timer_id):
    url = f"https://eu-wap.tplinkcloud.com/?token={token}"
    headers = {"Content-Type": "application/json"}

    payload_set_timer = {
        "method": "passthrough",
        "params": {
            "deviceId": device_id,
            "requestData": json.dumps({
                "count_down": {
                    "edit_rule": {                  #add_Rule/addRule instead of edit_rule also possible withoud "id" -> didnt work for me
                        "enable": 1,
                        "delay": delay,
                        "act": 1,  # 1 for on, 0 for off
                        "name": "timer",
                        "id": timer_id
                    }
                }
            })
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload_set_timer)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error building Timer: {e}")

#Change this to your Credentials
cloud_username = "Username"
cloud_password = "Password"
delay_seconds = 1  

#Start of Program
token = get_tplink_token(cloud_username, cloud_password)
if token:
    device_list = get_device_list(token)
    if device_list:
        device_id = device_list[1]['deviceId']
        print(f"Device-ID: {device_id}")
        timer_id = get_timer_info(token, device_id)
        if timer_id:
            timer_response = set_timer(token, device_id, delay_seconds, timer_id)
            formatted_timer = json.dumps(timer_response, indent=4)
            print("Timer-Response:", formatted_timer)
else:
    print("Token couldnt be retrieved.")
