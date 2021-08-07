# vaccine-dispenser
잔여백신 예약 디스코드 봇
## 봇 호스팅
공개적인 서비스는 트래픽 문제때문에 제공하지 않고 있습니다.

[Harmony - Making a Basic Bot](https://harmony.mod.land/guide/beginner/basic_bot.html#create-application)을 참고해서 봇을 만드시고, 환경 변수 `VACCINEBOT_TOKEN`을 토큰값으로 설정해 주세요.

## 봇 실행
### 도커 사용 (권장)
```docker-compose up -d```

### 로컬 파이썬 사용

의존성을 설치합니다.

```pip install -r requirements.txt```

봇을 실행합니다.

```python src/main.py```

## LICENSE
[SJang1](https://github.com/SJang1)님의 [레포](https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro)를 포크했음을 밝히며, MIT 라이센스로 동일하게 유지됩니다.
