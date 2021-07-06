import requests
import json
import urllib3
import os
import time
urllib3.disable_warnings()

APIURL = 'https://vaccine-map.kakao.com/api/v2/vaccine/left_count_by_coords'
APIdata = '{"bottomRight":{"x":127.40752397814762,"y":36.35252722021185},"onlyLeft":false,"order":"latitude","topLeft":{"x":127.482570304122,"y":36.317732943866424}}'
headers = {
    "Host": "vaccine-map.kakao.com",
    "Connection": "keep-alive",
    "Origin": "https://vaccine-map.kakao.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Referer": "https://vaccine-map.kakao.com/",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Accept-Language": "fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3"
}

done = False
while done == False:
    time.sleep(1)
    response = requests.post(APIURL, data=APIdata, headers=headers, verify=False)

    received_API_status_code = response.status_code
    received_API_data = response.text

    print(received_API_data)

    jsonloaded = json.loads(received_API_data)
    jsonData = jsonloaded["organizations"]
    found = False
    for x in jsonData:
        if x.get('status') == "AVAILABLE" or x.get('leftCounts') != 0:
            found = x
            done = True
            break
        # keys = x.keys()
        # print(keys)
        # values = x.values()
        # print(values)


print("--- found")
print("name: " + found.get('orgName'))
print("leftCounts: " + found.get('leftCounts'))
orgCdCode = x.get('orgCode')

os.system('/usr/bin/open -a "/Applications/Google Chrome.app" "https://v-search.nid.naver.com/reservation/standby?orgCd=' + orgCdCode + '"')