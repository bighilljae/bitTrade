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
        if per is None:
            self.msg = cur
            return
        if self.lastMessage is None or datetime.datetime.now() > self.lastMessage + datetime.timedelta(minutes=self.minutes):
            self.msg = self.msg + '\n' + cur + ' ' + str(round((per - 1) * 100, 2)) + '% 차이 발생'

    def message(self, force=False):
        if self.lastMessage is None or datetime.datetime.now() > self.lastMessage + datetime.timedelta(minutes=self.minutes) and self.msg != '':
            if len(self.msg) <= 0:
                return
            self.lastMessage = datetime.datetime.now()
            print('message %s' % self.msg)
            self.bot.sendMessage(chat_id=self.id, text=self.msg)
            self.msg = ''
