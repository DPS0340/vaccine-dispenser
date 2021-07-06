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


# TODO : "status":"AVALIABLE" 또는 "leftCounts":0이 아닌 것을 찾아서 해당되는 병원의 orgCode를 가져오기
print("--- found")
print("name: " + found.get('orgName'))
print("leftCounts: " + found.get('leftCounts'))
# 가져온 orgCode를 아래 os.system에 orgCdCode 변수로 지정해서 크롬 열기
orgCdCode = x.get('orgCode')
# "status":"AVALIABLE" 또는 "leftCounts":0이 아닌 것의 병원코드를 한번 가져온 후에 크롬을 열고 이 프로세스 멈추기

os.system('/usr/bin/open -a "/Applications/Google Chrome.app" "https://v-search.nid.naver.com/reservation/standby?orgCd=' + orgCdCode + '"')