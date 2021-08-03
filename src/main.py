from log import logger as logging
from discord import Embed
from core import login_request, reservation
from discord.ext import commands
from vaccinebot_token import get_token
from core import fill_str_with_space
from constants import vaccine_candidates

prefix = "vac "
bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix))
token = get_token()

user_infos = {}
locks = {}

@bot.command()
async def login(ctx: commands.Context, id, pw, top_x, top_y, bottom_x, bottom_y, only_left=True):
    message = ctx.message
    user_infos[ctx.author.id] = {'id': id, 'pw': pw, 'top_x': top_x, 'top_y': top_y, 'bottom_x': bottom_x, 'bottom_y': bottom_y, 'only_left': only_left}
    await message.channel.send("로그인이 완료되었습니다!")

@bot.command()
async def reserv(ctx: commands.Context, vac_type):
    message = ctx.message
    if locks.get(ctx.author.id) == True:
        await message.channel.send("이미 예약중입니다!")
    vac_code = [ x['code'] for x in vaccine_candidates if x['name'] == vac_type]
    if not vac_code:
        await message.channel.send("잘못된 백신 인자값입니다.")
        return
    vac_type = vac_code[0]
    user_info = user_infos[ctx.author.id]
    locks[ctx.author.id] = True
    try:
        await reservation(message, vac_type, *user_info.values())
    except Exception as err:
        logging.critical(err, exc_info=True)
    locks[ctx.author.id] = False

@bot.command()
async def list(ctx: commands.Context):
    message = ctx.message
    embed = Embed(title="백신 목록", color=0x95e4fe)
    for vaccine in vaccine_candidates:
        if vaccine["name"] == "(미사용)":
            continue
        embed.add_field(name=vaccine['name'], value=vaccine['name'], inline=False)
    await message.channel.send(embed=embed)

async def help(message):
    embed = Embed(title="백신봇 도움말", color=0x95e4fe)
    embed.add_field(name=f"{prefix}list", value="백신 목록", inline=False)
    embed.add_field(name=f"{prefix}login id pw top_x top_y bottom_x bottom_y only_left", value="카카오 로그인, 좌표값은 https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro/discussions/2 참고", inline=False)
    embed.add_field(name=f"{prefix}reserv vac_type", value="백신 예약", inline=False)
    embed.add_field(
        name=f"License", value="MIT License, Forked from https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro", inline=False)
    embed.add_field(
        name=f"Github", value="https://github.com/DPS0340/korea-covid-19-remaining-vaccine-macro", inline=False)
    await message.channel.send(embed=embed)

@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    mention = f"<@!{bot.user.id}>"
    if mention in message.content:
        await help(message)
        return
    if not message.content.startswith(prefix):
        return
    if message.guild:
        await message.channel.send("개인정보 유출을 방지하기 위해 DM으로 해주세요!")
        await message.channel.send(f"헬프는 {mention} 멘션")
        return
    await bot.process_commands(message)

if __name__ == '__main__':
    bot.run(token)