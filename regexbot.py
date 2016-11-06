from aiotg import Bot, Chat
import logging
import asyncio
import aiohttp
import os
import json
import regex as re

bot = Bot(api_token=os.environ['API_KEY'])

last_msgs = {}

async def doit(chat, match):
    global last_msgs

    if chat.id not in last_msgs:
        return

    fr = match.group(1)
    to = match.group(2)
    try:
        fl = match.group(3)
    except IndexError:
        fl = ''

    count = 1
    flags = 0
    for f in fl:
        if f == 'i':
            flags |= re.IGNORECASE
        elif f == 'g':
            count = 0
        else:
            await chat.reply('unknown flag: {}'.format(f))
            return

    for msg in reversed(last_msgs[chat.id]):
        try:
            s, i = re.subn(fr, to, msg['text'], count=count, flags=flags)
            if i > 0:
                await Chat.from_message(bot, msg).reply(s)
                return
        except Exception as e:
            await chat.reply('u dun goofed m8: ' + str(e))
            return


@bot.command(r'^s/(.*)/(.*)/(.*)$')
async def test(chat, match):
    await doit(chat, match)

@bot.command(r'^s/(.*)/(.*)$')
async def test(chat, match):
    await doit(chat, match)  


@bot.command(r'(.*)')
async def msg(chat, match):
    global last_msgs

    if chat.id not in last_msgs:
        last_msgs[chat.id] = []

    last_msgs[chat.id].append(chat.message)
    if len(last_msgs[chat.id]) > 10:
        last_msgs[chat.id] = last_msgs[chat.id][-10:]

async def main():
    await bot.loop()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        bot.stop()

        
