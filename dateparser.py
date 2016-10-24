from datetime import datetime


def parse_epoch(epoch):
    date = datetime.fromtimestamp(epoch / 1000)
    return date.strftime("%d/%m/%Y")


def format_age(created_at):
    now = datetime.utcnow()
    then = datetime.fromtimestamp(created_at/1000)
    age = int((now - then).total_seconds()) // 60

    if age == 0:
        return 'just now'

    if age < 60:
        value = age
        precision = 'minute'
    elif age < 60 * 24:
        value = age // 60
        precision = 'hour'
    else:
        value = age // (60 * 24)
        precision = 'day'

    return '{value} {precision}{suffix}'.format(value=value, precision=precision, suffix=('s' if value > 1 else ''))
