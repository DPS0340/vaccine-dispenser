import hostile from 'hostile'
import axios from 'axios'
import readline from 'readline'

hostile.set('13.125.8.153', 'vaccinebot.kakao.com', function (err) {
  if (err) {
    console.error(err)
  } else {
    console.log('vaccinebot.kakao.com -> 봇 서버 IP DNS 등록 추가!')
  }
});


function wait_for_enter(query='Enter를 눌러서 종료해 주세요!') {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });

    return new Promise(resolve => rl.question(query, ans => {
        rl.close();
        resolve(ans);
    }))
}


const res = await axios.get('https://checkip.amazonaws.com')
console.log(`IP 주소는 ${res.data.trim()} 입니다. 봇에 입력해 주세요!`)

await wait_for_enter()