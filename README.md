# vaccine-dispenser
잔여백신 비동기 예약 매크로 디스코드 봇

## 봇 호스팅
공개적인 서비스는 트래픽 문제때문에 제공하지 않고 있습니다.

[Harmony - Making a Basic Bot](https://harmony.mod.land/guide/beginner/basic_bot.html#create-application)을 참고해서 봇을 만드시고, 환경 변수 `VACCINEBOT_TOKEN`을 토큰값으로 설정해 주세요.

## 봇 실행
### Docker 사용 (권장)
먼저 [Docker](https://docs.docker.com/engine/install/ubuntu/)랑 [Docker Compose](https://docs.docker.com/compose/install/)가 설치되었는지 확인해 주세요.

```docker-compose up -d```

### 로컬 파이썬 사용

의존성을 설치합니다.

```pip install -r requirements.txt```

봇을 실행합니다.

```python src/main.py```

## 커맨드 목록
모든 커맨드는 DM 전용입니다.

![image](https://user-images.githubusercontent.com/32592965/128608773-77b6d05f-1801-4827-8654-40de4ea3df42.png)

## AS-IS / TO-BE

- [X] 디스코드 봇 미그레이션
- [X] aiohttp를 사용한 비동기 처리
- [X] pyppeteer를 사용한 로그인 자동화
- [X] 로그인중 캡챠 발생시 hosts를 이용하여 cookie hijacking
- [X] 주소 기반 좌표 체크 자동화
- [X] 예약시 동시에 여러 병원 요청
- [X] 로깅, 메시지  예약시 lazy하게 작동


## LICENSE
[SJang1](https://github.com/SJang1)님의 [레포](https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro)를 포크했음을 밝히며, MIT 라이센스로 동일하게 유지됩니다.
