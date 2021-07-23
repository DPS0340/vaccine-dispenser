# korea-covid-19-remaining-vaccine-macro
잔여백신 지도 API로 남은 백신 수를 확인하고, 잔여백신이 있는 경우 잔여백신 예약 페이지로 이동합니다.

## 카카오 잔여백신 예약
### 이용방법
1. [https://accounts.kakao.com/login](https://accounts.kakao.com/login?continue=https%3A%2F%2Faccounts.kakao.com%2Fweblogin%2Faccount%2Finfo) 에 접근하여 카카오 로그인을 합니다.
2. https://vaccine.kakao.com/api/v1/user 에 접근하여 본인의 정보가 정상적으로 표시되는지 확인합니다.  
정상적으로 표시되지 않는 경우 카카오톡에서 잔여백신 알림 신청을 해줍니다.
3. https://vaccine-map.kakao.com/map2?v=1 에서 지도를 움직여서 잔여백신을 검색할 지역을 설정하고, 개발자도구를 열어 해당 위치의 x, y값을 기록해둡니다.
4. 터미널에서 `pip3 install requests` 로 필요한 `requests` 라이브러리를 설치합니다.
5. 터미널에서 `python3 ./vaccine-run-kakao.py` 로 백신을 검색합니다
6. 백신이 발생하면 해당 병원 잔여백신 예약 페이지로 이동되며, 바로 당일예약이 됩니다.

### 주의사항
- 잔여백신 예약 성공의 타이밍이 매번 다릅니다. 어떤 경우는 잔여백신이 발생한 직후에는 예약이 실패하기도 합니다. 따라서, 타이밍이 다르게 `time.sleep(시간)`을 다르게 설정 후, 두 개 이상의 프로세스를 실행하기를 권장합니다.

## 네이버 잔여백신 예약
### 주의사항
- 네이버 서버의 문제로, 잔여백신이 발생할 때마다 잔여백신 지도 API가 작동을 하지 않습니다.
