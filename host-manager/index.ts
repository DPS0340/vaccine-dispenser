import axios from "https://cdn.skypack.dev/axios";
import * as hostile from "./hostile.js";

hostile.set('13.125.8.153', 'vaccinebot.kakao.com')
console.log('vaccinebot.kakao.com -> 봇 서버 IP DNS 등록 추가!')


const res = await fetch('https://checkip.amazonaws.com', {
  method: "GET"
})
console.log(`IP 주소는 ${(await res.text()).trim()} 입니다. 봇에 입력해 주세요!`)

prompt('Enter를 눌러서 종료해 주세요!')