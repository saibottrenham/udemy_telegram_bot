import datetime


class ReminderData:

    def __init__(self, row):
        self.reminder_id = row[0]
        self.chat_id = row[1]
        self.message = row[2]
        self.time = row[3]
        self.fired = row[4]

    def __repr__(self):
        return "Message: {0}; At Time: {1}".format(self.message, self.time.strftime("%d/%m/%Y %H:%M"))

    def fire(self):
        self.fired = True

    def should_be_fired(self):
        return self.time < datetime.datetime.now() and not self.fired
