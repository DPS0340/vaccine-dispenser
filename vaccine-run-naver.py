import requests
import json
import urllib3
import os
import time
import datetime
urllib3.disable_warnings()


APIURL = 'https://api.place.naver.com/graphql'
APIdata = '[{"operationName":"vaccineList","variables":{"input":{"keyword":"코로나백신위탁의료기관","x":"126.9421195","y":"37.4913207"},"businessesInput":{"start":0,"display":100,"deviceType":"mobile","x":"126.9421195","y":"37.4913207","bounds":"126.9060707;37.477069;126.9781684;37.5055696","sortingOrder":"distance"},"isNmap":false,"isBounds":false},"query":"query vaccineList($input: RestsInput, $businessesInput: RestsBusinessesInput, $isBounds: Boolean!) {  rests(input: $input) {    businesses(input: $businessesInput) {      total      vaccineLastSave      isUpdateDelayed      items {        id        name        description        distance        commonAddress        roadAddress        address        imageUrl        imageCount        tags        distance        category        businessHours        vaccineOpeningHour {          isDayOff          standardTime          __typename        }        vaccineQuantity {          totalQuantity          totalQuantityStatus          startTime          endTime          vaccineOrganizationCode          list {            quantity            quantityStatus            vaccineType            __typename          }          __typename        }        __typename      }      optionsForMap @include(if: $isBounds) {        maxZoom        minZoom        includeMyLocation        maxIncludePoiCount        center        __typename      }      __typename    }    queryResult {      keyword      vaccineFilter      categories      region      isBrandList      filterBooking      hasNearQuery      isPublicMask      __typename    }    __typename  }}"}]'

done = False
while done == False:
    time.sleep(0.4)
    headers = {
        "Origin": "https://m.place.naver.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        "Content-Type": "application/json",
        "Referer": "https://m.place.naver.com/rest/vaccine",
    }

    response = requests.post(APIURL, APIdata.encode('utf-8'), headers=headers)
    if response.status_code != 200:
      print(response.text)
      exit()

    received_API_status_code = response.status_code
    received_API_data = response.text

    print(received_API_data)
    print(datetime.datetime.now())

    jsonloaded = json.loads(received_API_data)
    # print(jsonloaded[0]["data"]["rests"]["businesses"]["items"])
    jsonData = jsonloaded[0]["data"]["rests"]["businesses"]["items"]
    found = False
    for x in jsonData:
      # print(x)
      if x['vaccineQuantity'] and int(x['vaccineQuantity']['totalQuantity']) > 0:
        # 화이자 있는지 체크
        for y in x["vaccineQuantity"]["list"]:
            if y.get('vaccineType') == "화이자" and y.get("quantity") > 0:
                found = x
                done = True
                break
        if done:
          break
        # keys = x.keys()
        # print(keys)
        # values = x.values()
        # print(values)

print("--- found")
print(found.keys())
print(found.values())
orgCdCode = x.get('vaccineQuantity').get('vaccineOrganizationCode')
sid = x.get('id')
# "status":"AVAILABLE" 또는 "leftCounts":0이 아닌 것의 병원코드를 한번 가져온 후에 크롬을 열고 이 프로세스 멈추기

os.system('/usr/bin/open -a "/Applications/Google Chrome.app" "https://v-search.nid.naver.com/reservation/standby?orgCd=' + orgCdCode + '&sid=' + sid + '"')
