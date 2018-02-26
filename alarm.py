import telegram
import auth
import datetime

class Alarm:
    bot = telegram.Bot(token=auth.TELEGRAM_TOKEN)
    id = auth.TELEGRAM_ID
    minutes = 5
    lastMessage = None
    msg = ''

    def __init__(self, minute):
        self.minutes = minute

    def add(self, cur, per):
        if self.lastMessage is None or datetime.datetime.now() > self.lastMessage + datetime.timedelta(minutes=self.minutes):
            self.msg = self.msg + '\n' + cur + ' ' + str(round((per - 1) * 100, 2)) + '% 차이 발생'

    def message(self):
        if self.lastMessage is None or datetime.datetime.now() > self.lastMessage + datetime.timedelta(minutes=self.minutes):
            self.lastMessage = datetime.datetime.now()
            self.bot.sendMessage(chat_id=self.id, text=self.msg)
            self.msg = ''
