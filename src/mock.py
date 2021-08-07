import json


async def mock_check_user_info_loaded(message, cookies, val=True):
    return val

async def mock_find_vaccine(*args, **kwargs):
    return json.dumps({'organizations': [
        {'orgCode': '21318221', 'orgName': '천마의원', 'address': '부산 사하구 옥천로 73-1', 'x': 129.009095060001, 'y': 35.0932200126732, 'status': 'AVAILABLE', 'leftCounts': 6},
        {'orgCode': '21355941', 'orgName': '남포신용훈내과의원', 'address': '부산 중구 구덕로 40', 'x': 129.03157940536863, 'y': 35.09846045080925, 'status': 'AVAILABLE', 'leftCounts': 2},
        {'orgCode': '21352607', 'orgName': '김도현이비인후과의원', 'address': '부산 서구 구덕로 312', 'x': 129.0171033252261, 'y': 35.111723353705884, 'status': 'AVAILABLE', 'leftCounts': 1}
        ]})

async def mock_try_reservation(*args, **kwargs):
    return json.dumps({'code': 'NO_VACANCY', 'desc': '잔여백신 접종 신청이\n선착순 마감되었습니다.', 'organization': {'orgCode': '21345538', 'orgName': '전윤숙 소아청소년과의원', 'confirmId': '537137397', 'phoneNumber': '051-522-8886', 'address': '부산 서구 대영로 54', 'x': 129.017298692113, 'y': 35.1096834428386, 'openHour': {'date': '2021-08-07', 'dayOfWeek': '토요일', 'dayOff': False, 'openHour': {'start': '10:00', 'end': '14:00'}, 'lunch': {'start': '13:00', 'end': '14:00'}}, 'disabled': False}})

class MockResponse:
    def __init__(self) -> None:
        self.status = 200
        self.read = mock_find_vaccine