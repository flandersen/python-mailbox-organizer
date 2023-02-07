from datetime import datetime, timedelta

from imap_tools import MailBox

from mysecrets import EMAIL_ADDRESS, PASSWORD, SERVER

# EMAIL_ADDRESS = '<from mysecret.py>'
# PASSWORD = '<from mysecret.py>'
# SERVER = '<from mysecret.py>'

date_two_days_ago = datetime.utcnow().date() - timedelta(days=2)
date_two_weeks_ago = datetime.utcnow().date() - timedelta(days=14)

delete_unseen_after_2_weeks = {}

with open('delete-unseen-after-2-weeks.list', 'r') as reader:
    for line in reader:
        line = line.strip()
        if line != '':
            delete_unseen_after_2_weeks[line] = 'dummy'

delete_seen_after_2_days = {}

with open('delete-seen-after-two-days.list', 'r') as reader:
    for line in reader:
        line = line.strip()
        if line != '':
            delete_seen_after_2_days[line] = 'dummy'

uids_to_delete = list()

# Get date, subject and body len of all emails from INBOX folder
with MailBox(SERVER).login(EMAIL_ADDRESS, PASSWORD) as mailbox:
    for msg in mailbox.fetch(headers_only=True):
        if msg.from_ in delete_unseen_after_2_weeks\
            and msg.date.date() <= date_two_weeks_ago\
            and '\\Flagged' not in msg.flags:

            uids_to_delete.append(msg.uid)

        elif msg.from_ in delete_seen_after_2_days\
            and msg.date.date() <= date_two_days_ago\
            and '\\Flagged' not in msg.flags\
            and '\\Seen' in msg.flags:

            uids_to_delete.append(msg.uid)
    
    print("Deleting {} mails.".format(len(uids_to_delete)))
    mailbox.delete(uids_to_delete)
