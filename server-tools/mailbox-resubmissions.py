#!/usr/bin/python3
import mailbox
from time import time, gmtime, strftime, timezone
from email.header import decode_header, make_header

md = mailbox.Maildir('/home/pacs/mih12/users/mh/Maildir')
now = time()-timezone
today = now / (24*60*60)
todays_weekday = int(strftime('%w'))
today_ymd = strftime('%Y-%m-%d')
seconds_per_day = 24*60*60

def without_linebreaks(string):
    return string.replace('\n', ' ').replace('\r', '')

def decoded_header(string):
    return str(make_header(decode_header(string)))
    # return ''.join((t[0].decode(t[1] or 'ASCII').encode('utf-8') for t in decode_header(string) )

def print_message(message_key, message):
    print(' - MessageID: ', message_key)
    print(' - Subject:   ', without_linebreaks(decoded_header(message['Subject'])))
    print(' - From:      ', message['From'])
    print()

def resubmit(folder_name, folder, message_key, message):
    print('[', folder_name, '/', message.get_date(), '] resubmitted:')
    message.remove_flag('S')  # mark as unseen
    message.add_flag('F')     # star/flag so it does not get deferred automatically
    message.set_date(time())
    md.add(message)
    folder.discard(message_key)
    print_message(message_key, message)

def error(folder_name, folder, message_key, message, cause):
    message.remove_flag('S')
    message.set_date(time())
    folder.update({message_key: message})
    print('[', folder_name, '] error: ', cause)
    print(' > mailbox-resubmit', message_key.split(',', 2)[0], 'YYYY-mm-dd')
    print_message(message_key, message)

def resubmit_from_folder_after_days(folder_name, days):
    resubmission_date = today-days
    resubmission_folder = md.get_folder(folder_name)
    for message_key in resubmission_folder.iterkeys():
        message = resubmission_folder.get(message_key)
        message_date = message.get_date() / seconds_per_day
        resubmission_due_in_days = message_date-resubmission_date
        if (resubmission_due_in_days <= 0):
            resubmit(folder_name, resubmission_folder, message_key, message)

def resubmit_from_folder_at_time(folder_name, hour):
    if ( gmtime(now).tm_hour == hour ):
        resubmission_folder = md.get_folder(folder_name)
        for message_key in resubmission_folder.iterkeys():
            message = resubmission_folder.get(message_key)
            resubmit(folder_name, resubmission_folder, message_key, message)

def resubmit_from_folder_on_day(folder_name, weekday, hour):
    if ( todays_weekday == weekday and gmtime(now).tm_hour == hour ):
        resubmission_folder = md.get_folder(folder_name)
        for message_key in resubmission_folder.iterkeys():
            message = resubmission_folder.get(message_key)
            resubmit(folder_name, resubmission_folder, message_key, message)

def resubmit_from_folder_by_due_dates(folder_name):
    resubmission_folder = md.get_folder(folder_name)
    for message_key in resubmission_folder.iterkeys():
        message = resubmission_folder.get(message_key)
        x_resubmit = message['X-Resubmit']
        if not x_resubmit:
            error(folder_name, resubmission_folder, message_key, message, '"X-Resubmit: YYYY-MM-DD" header is missing')
        elif x_resubmit.strip() == today_ymd:
            resubmit(folder_name, resubmission_folder, message_key, message)

def move_unstarred_and_unread_messages_from_inbox_to_deferred_at_time(hour):
    "move unstarred Inbox messages to 'Deferred' folder daily at the given hour"
    if gmtime(now).tm_hour != hour:
        return

    # Ensure the "Deferred" folder exists
    try:
        folders = md.list_folders()
    except Exception:
        folders = []
    if 'Deferred' not in folders:
        md.add_folder('Deferred')

    deferred = md.get_folder('Deferred')

    # Iterate over Inbox (root Maildir) messages
    for key in md.iterkeys():
        msg = md.get(key)
        flags = getattr(msg, 'get_flags', lambda: '')()
        # skip starred (flagged) and unread (not seen) messages
        if 'F' in flags or 'S' not in flags:
            continue
        # Move to Deferred
        deferred.add(msg)
        md.discard(key)
        print('[INBOX -> Deferred] moved:')
        print_message(key, msg)

move_unstarred_and_unread_messages_from_inbox_to_deferred_at_time(23)
resubmit_from_folder_at_time('_Resubmit.0: evening', 19)
resubmit_from_folder_at_time('_Resubmit.1: morning', 8)
resubmit_from_folder_on_day('_Resubmit.2: weekend', 6, 8)
resubmit_from_folder_after_days('_Resubmit.3: 3 days', 2)
resubmit_from_folder_after_days('_Resubmit.4: 1 week', 7)
resubmit_from_folder_after_days('_Resubmit.5: 4 weeks', 28)
resubmit_from_folder_after_days('_Resubmit.6: 3 months', 90)
resubmit_from_folder_by_due_dates('_Resubmit.D: due date')

md.flush()
