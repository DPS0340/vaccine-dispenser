const hostile = require('hostile')
const axios = require('axios')

hostile.set('127.0.0.1', 'vaccinebot.kakao.com', function (err) {
  if (err) {
    console.error(err)
  } else {
    console.log('vaccinebot.kakao.com -> 127.0.0.1 DNS 등록 추가!')
  }
});


(async () => {
    const res = await axios.get('https://checkip.amazonaws.com')
    console.log(`IP 주소는 ${res.data.trim()} 입니다. 봇에 입력해 주세요!`)
})()