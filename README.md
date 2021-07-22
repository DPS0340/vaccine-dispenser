# korea-covid-19-remaining-vaccine-macro
잔여백신 지도 API로 남은 백신 수를 확인하고, 잔여백신이 있는 경우 잔여백신 예약 페이지로 이동합니다.

## 카카오 잔여백신 예약
### 이용방법
1. https://accounts.kakao.com/login 에 접근하여 카카오 로그인을 합니다.
2. https://vaccine.kakao.com/api/v1/user 에 접근하여 본인의 정보가 정상적으로 표시되는지 확인합니다.  
정상적으로 표시되지 않는 경우 카카오톡에서 잔여백신 알림 신청을 해줍니다.
3. https://vaccine-map.kakao.com/map2?v=1 에서 지도를 움직여서 잔여백신을 검색할 지역을 설정하고, 개발자도구를 열어 해당 위치의 x, y값을 기록해둡니다.
4. 터미널에서 `pip3 install requests` 로 필요한 `requests` 라이브러리를 설치합니다.
5. 터미널에서 `python3 ./vaccine-run-kakao.py` 로 백신을 검색합니다
6. 백신이 발생하면 해당 병원 잔여백신 예약 페이지로 이동되며, 바로 당일예약이 됩니다.
