import requests
import json
import uuid
import time
import random
import SignerPy
import secrets

class Genertore_Devices:
    def __init__(self):
       self.brands_by_manufacturer = {
    "Samsung": ["Galaxy S21", "Galaxy S22", "Galaxy Note20"],
    "OnePlus": ["NE2211", "OnePlus 9", "OnePlus 10"],
    "Xiaomi": ["Mi 11", "Redmi Note 12", "Poco X4"],
    "Huawei": ["P50", "Mate 40", "Nova 9"],
    "Motorola": ["Moto G100", "Moto Edge", "Moto X"],
    "Nokia": ["Nokia 8.3", "Nokia 5.4", "Nokia 3.4"],
    "Sony": ["Xperia 1", "Xperia 5", "Xperia 10"],
    "LG": ["LG Velvet", "LG Wing", "LG G8"],
    "Google": ["Pixel 6", "Pixel 7", "Pixel 7a"],
    "Oppo": ["Reno 7", "Find X5", "A74"]
}
       self.device_manufacturer = random.choice(list(self.brands_by_manufacturer.keys()))
       self.device_brand = random.choice(self.brands_by_manufacturer[self.device_manufacturer])
       self.current_time_ms = int(time.time() * 1000)
       self.current_time_s = int(time.time())
       self.region = "US"
    def GetVar(self):
      payload = {
        "header": {
          "os": "Android",
          "os_version": str(random.choice([9, 10, 11, 12])),
          "os_api": random.choice([28, 29, 30, 31]),
          "device_model": f"SM-{random.randint(1000,9999)}",
          "device_brand": self.device_brand,
          "device_manufacturer":self.device_manufacturer,
          "cpu_abi": "arm64-v8a",
          "density_dpi": 240,
          "display_density": "hdpi",
          "resolution": "900x1600",
          "display_density_v2": "hdpi",
          "resolution_v2": "1600x900",
          "access": "wifi",
          "rom": f"S.c{random.randint(100000,999999)}-{random.randint(1,99)}_{random.randint(10,99)}f",
          "rom_version": f"NE2211_{random.randint(10,99)}_C.{random.randint(10,99)}",
          "language": random.choice(["en", "ar", "fr", "es"]),
          "timezone": 3,
          "tz_name": "Asia/Baghdad",
          "tz_offset": 10800,
          "sim_region": self.region.lower(),
          "carrier": random.choice(["AT&T", "Verizon", "T-Mobile"]),
          "mcc_mnc": "310410",
          "clientudid": str(uuid.uuid4()),
          "openudid": str(uuid.uuid4().hex),
          "channel": "googleplay",
          "not_request_sender": 1,
          "aid": 1233,
          "release_build": f"d8db25e_{random.randint(20250000,20259999)}",
          "ab_version": "40.7.3",
          "gaid_limited": 0,
          "custom": {
            "ram_size": random.choice(["2GB","3GB","4GB"]),
            "dark_mode_setting_value": 1,
            "is_foldable": 0,
            "screen_height_dp": 1067,
            "apk_last_update_time": self.current_time_ms,
            "filter_warn": 0,
            "priority_region": self.region,
            "user_period": 0,
            "is_kids_mode": 0,
            "web_ua": f"Dalvik/2.1.0 (Linux; U; Android 9; SM-NE2211 Build/SKQ1.220617.001)",
            "screen_width_dp": 648,
            "user_mode": -1
          },
          "package": "com.zhiliaoapp.musically",
          "app_version": "40.7.3",
          "app_version_minor": "",
          "version_code": 400703,
          "update_version_code": 2024007030,
          "manifest_version_code": 2024007030,
          "app_name": "musical_ly",
          "tweaked_channel": "googleplay",
          "display_name": "TikTok",
          "sig_hash": uuid.uuid4().hex,
          "cdid": str(uuid.uuid4()),
          "device_platform": "android",
          "git_hash": uuid.uuid4().hex[:7],
          "sdk_version_code": 2050990,
          "sdk_target_version": 30,
          "req_id": str(uuid.uuid4()),
          "sdk_version": "2.5.9",
          "guest_mode": 0,
          "sdk_flavor": "i18nInner",
          "apk_first_install_time": self.current_time_ms,
          "is_system_app": 0
        },
        "magic_tag": "ss_app_log",
        "_gen_time": self.current_time_ms
      }
      paramss = {
          "req_id": payload["header"]["req_id"],
          "device_platform": payload["header"]["device_platform"],
          "os": payload["header"]["os"].lower(),
          "ssmix": "a",
          "_rticket": str(self.current_time_ms),
          "cdid": payload["header"]["cdid"],
          "channel": payload["header"]["channel"],
          "aid": str(payload["header"]["aid"]),
          "app_name": payload["header"]["app_name"],
          "version_code": str(payload["header"]["version_code"]),
          "version_name": payload["header"]["app_version"],
          "manifest_version_code": str(payload["header"]["manifest_version_code"]),
          "update_version_code": str(payload["header"]["update_version_code"]),
          "ab_version": payload["header"]["ab_version"],
          "resolution": payload["header"]["resolution_v2"].replace("x","*"),
          "dpi": str(payload["header"]["density_dpi"]),
          "device_type": payload["header"]["device_model"],
          "device_brand": payload["header"]["device_brand"],
          "language": payload["header"]["language"],
          "os_api": str(payload["header"]["os_api"]),
          "os_version": payload["header"]["os_version"],
          "ac": payload["header"]["access"],
          "is_pad": "0",
          "app_type": "normal",
          "sys_region": self.region,
          "last_install_time": str(self.current_time_s),
          "mcc_mnc": payload["header"]["mcc_mnc"],
          "timezone_name": payload["header"]["tz_name"],
          "carrier_region_v2": payload["header"]["mcc_mnc"][:3],
          "app_language": payload["header"]["language"],
          "carrier_region": self.region,
          "timezone_offset": str(payload["header"]["tz_offset"]),
          "host_abi": payload["header"]["cpu_abi"],
          "locale": payload["header"]["language"],
          "ac2": "unknown",
          "uoo": "1",
          "op_region": self.region,
          "build_number": payload["header"]["app_version"],
          "region": self.region,
          "ts": str(self.current_time_s),
          "openudid": payload["header"]["openudid"],
          "okhttp_version": "4.2.228.19-tiktok",
          "use_store_region_cookie": "1",
      }

      headers = {
        'User-Agent': f"com.zhiliaoapp.musically/2024007030 (Linux; U; Android {payload['header']['os_version']}; {payload['header']['language']}; {payload['header']['device_model']}; Build/SKQ1.220617.001;tt-ok/3.12.13.20)",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
        'x-tt-app-init-region': f"carrierregion={self.region};mccmnc=310410;sysregion={self.region};appregion={self.region}",
        'x-tt-request-tag': "t=0;n=1",
        'x-tt-dm-status': "login=0;ct=0;rt=7",
        'sdk-version': "2",
        'passport-sdk-version': "-1",
        'x-vc-bdturing-sdk-version': "2.3.13.i18n",
        'content-type': "application/json; charset=utf-8"
      }

      url = "https://log-boot.tiktokv.com/service/2/device_register/"
      response = requests.post(url, data=json.dumps(payload), headers=headers, params=paramss)
      try:
        device_id = response.json()["device_id_str"]
        iid = response.json()["install_id_str"]
        # print(response.text)


        url = "https://api16-normal-useast5.tiktokv.us/consent/api/record/create/sync/v2"
        params = {
            "device_platform": payload["header"]["device_platform"],
            "os": payload["header"]["os"].lower(),
            "ssmix": "a",
            "_rticket": str(int(time.time() * 1000)),
            "channel": payload["header"]["channel"],
            "aid": str(payload["header"]["aid"]),
            "app_name": payload["header"]["app_name"],
            "version_code": str(payload["header"]["version_code"]),
            "version_name": payload["header"]["app_version"],
            "manifest_version_code": str(payload["header"]["manifest_version_code"]),
            "update_version_code": str(payload["header"]["update_version_code"]),
            "ab_version": payload["header"]["ab_version"],
            "resolution": payload["header"]["resolution_v2"].replace("x","*"),
            "dpi": str(payload["header"]["density_dpi"]),
            "device_type": payload["header"]["device_model"],
            "device_brand": payload["header"]["device_brand"],
            "language": payload["header"]["language"],
            "os_api": str(payload["header"]["os_api"]),
            "os_version": payload["header"]["os_version"],
            "ac": payload["header"]["access"],
            "language":  payload["header"]["language"],
            "is_pad": "0",
            "app_type": "normal",
            "sys_region": self.region,
            "last_install_time": str(self.current_time_s),
            "mcc_mnc": payload["header"]["mcc_mnc"],
            "timezone_name": "Asia/Baghdad",
            "carrier_region_v2": payload["header"]["mcc_mnc"][:3],
            "app_language": payload["header"]["language"],
            "carrier_region_v2": self.region,
            "app_language": payload["header"]["language"],
            "carrier_region": self.region,
            "timezone_offset": str(payload["header"]["tz_offset"]),
            "host_abi": payload["header"]["cpu_abi"],
            "locale": payload["header"]["language"],
            "ac2": payload["header"]["access"],
            "uoo": "0",
            "op_region": self.region,
            "build_number": payload["header"]["app_version"],
            "region": self.region,
            "ts": int(time.time()),
            "iid":iid,
            "device_id": device_id,
            "app_version":"40.7.3"
        }
        tokens = secrets.token_hex(16)
        cookies = {
            "passport_csrf_token":tokens,
            "passport_csrf_token_default": tokens
        }

        payload = {
          'consent_records': "[{\"flow\":\"consent_box\",\"entity_key\":\"conditions-policy-device-consent\",\"status\":1}]",
          'sdk_version': "2.7.4.4",
          'sdk_name': "pns_consent_sdk"
        }
        m=SignerPy.sign(params=params,cookie=cookies,payload=payload)
        headers = {
          'User-Agent': headers["User-Agent"],
          'Accept-Encoding': "gzip",
          'rpc-persist-pyxis-policy-v-tnc': "1",
          'x-ss-stub': m['x-ss-stub'],
          'x-tt-pba-enable': "1",
          'sdk-version': "2",
          'x-tt-dm-status': "login=0;ct=1;rt=6",
          'x-ss-req-ticket': m['x-ss-req-ticket'],
          'passport-sdk-version': "-1",
          'rpc-persist-pns-region-1': "US|6252001",
          'rpc-persist-pns-region-2': "US|6252001",
          'rpc-persist-pns-region-3': "US|6252001",
          'x-vc-bdturing-sdk-version': "2.3.13.i18n",
          'oec-vc-sdk-version': "3.0.12.i18n",
          'x-tt-store-region': "us",
          'x-tt-store-region-src': "did",
          'x-ladon':m['x-ladon'],
          'x-khronos':m['x-khronos'],
          'x-argus':m['x-argus'],
          'x-gorgon':m['x-gorgon']

        }

        response = requests.post(url, data=payload, headers=headers,cookies=cookies,params=params)
        if "device_id" in  response.text:
          with open("devices.txt","a",encoding="utf-8") as f:
              f.write("{}:{}:{}:{}:{}:{}:{}\n".format(device_id,iid,paramss["device_type"],paramss["device_brand"],paramss["cdid"],paramss["openudid"],cookies["passport_csrf_token"]))
          return {"data":{"message":"success","devices":{"device_id":device_id,"install_id":iid,"did":device_id,"iid":iid,"openudid":paramss["openudid"],"device_type":params["device_type"],"device_brand":paramss["device_brand"],"cdid":paramss["cdid"],"secrets":cookies["passport_csrf_token"]},"statuc":"ok"},"message":"success"}
        else:
           return {"data":{"message":"error coldnot verify devices","status":"ok"},"message":"error"}
      except:
         return {"data":{"message":"device_id and install_id get error","status":"ok"},"message":"error"}

class Tik:
    def GetVar():
        return Genertore_Devices().GetVar()

