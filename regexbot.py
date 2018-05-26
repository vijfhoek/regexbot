from aiotg import Bot, Chat
import asyncio
import os
import regex as re
from collections import defaultdict, deque
from pprint import pprint
from datetime import datetime, timedelta

bot = Bot(api_token=os.environ['API_KEY'])
last_msgs = defaultdict(lambda: deque(maxlen=10))


def find_original(message):
    if 'text' in message:
        return message['text']
    elif 'caption' in message:
        return message['caption']

    return None


async def doit(chat, match):
    date = datetime.fromtimestamp(chat.message['date'])
    if date < datetime.now() - timedelta(minutes=5):
        print('ignoring old message from', date)
        return

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

    # Build Python regex flags
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

    async def substitute(original, msg):
        try:
            s, i = re.subn(fr, to, original, count=count, flags=flags)
            if i > 0:
                return (await Chat.from_message(bot, msg).reply(s))['result']
        except Exception as e:
            await chat.reply('u dun goofed m8: ' + str(e))

    # Handle replies
    if 'reply_to_message' in chat.message:
        # Try to find the original message text
        message = chat.message['reply_to_message']
        original = find_original(message)
        if not original:
            return

        return await substitute(original, message)

    else:
        # Try matching the last few messages
        for msg in reversed(last_msgs[chat.id]):
            original = find_original(msg)
            if not original:
                continue

            result = await substitute(original, msg)
            if result is not None:
                return result


@bot.command(r'^s/((?:\\/|[^/])+)/((?:\\/|[^/])*)(/.*)?')
async def test(chat, match):
    msg = await doit(chat, match)
    if msg:
        last_msgs[chat.id].append(msg)
    pprint(last_msgs[chat.id])


@bot.command(r'(.*)')
@bot.handle('photo')
async def msg(chat, match):
    last_msgs[chat.id].append(chat.message)


async def main():
    await bot.loop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        bot.stop()
