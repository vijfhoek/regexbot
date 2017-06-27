from aiotg import Bot, Chat
import asyncio
import json
import os
import regex as re
from collections import defaultdict
from pprint import pprint

bot = Bot(api_token=os.environ['API_KEY'])

last_msgs = defaultdict(list)

async def doit(chat, match):
    fr = match.group(1)
    to = match.group(2)
    to = to.replace('\\/', '/')
    try:
        fl = match.group(3)
        if fl == None:
            fl = ''
        fl = fl[1:]
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

    if 'reply_to_message' in chat.message and 'text' in chat.message['reply_to_message']:
        try:
            s, i = re.subn(fr, to, chat.message['reply_to_message']['text'])
            if i > 0:
                return (await Chat.from_message(bot, chat.message['reply_to_message']).reply(s))['result']
        except Exception as e:
            await chat.reply('u dun goofed m8: ' + str(e))
            return
    else:
        global last_msgs
        if chat.id not in last_msgs:
            return

        for msg in reversed(last_msgs[chat.id]):
            try:
                if 'text' in msg:
                    original = msg['text']
                elif 'caption' in msg:
                    original = msg['caption']
                else:
                    continue

                s, i = re.subn(fr, to, original, count=count, flags=flags)
                if i > 0:
                    return (await Chat.from_message(bot, msg).reply(s))['result']
            except Exception as e:
                await chat.reply('u dun goofed m8: ' + str(e))
                return


@bot.command(r'^s/((?:\\/|[^/])+)/((?:\\/|[^/])*)(/.*)?')
async def test(chat, match):
    global last_msgs

    msg = await doit(chat, match)  
    if msg:
        last_msgs[chat.id].append(msg)
    pprint(last_msgs[chat.id])


@bot.command(r'(.*)')
async def msg(chat, match):
    global last_msgs

    if chat.id not in last_msgs:
        last_msgs[chat.id] = []

    last_msgs[chat.id].append(chat.message)
    if len(last_msgs[chat.id]) > 10:
        last_msgs[chat.id] = last_msgs[chat.id][-10:]


@bot.handle('photo')
async def msg_photo(chat, match):
    global last_msgs

    if chat.id not in last_msgs:
        last_msgs[chat.id] = []

    last_msgs[chat.id].append(chat.message)
    if len(last_msgs[chat.id]) > 10:
        last_msgs[chat.id] = last_msgs[chat.id][-10:]



async def main():
    await bot.loop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        bot.stop()

        
