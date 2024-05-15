from datetime import date, datetime, timedelta, UTC

from imap_tools import MailBox, consts, A

from mysecrets import EMAIL_ADDRESS, PASSWORD, SERVER

# EMAIL_ADDRESS = '<from mysecret.py>'
# PASSWORD = '<from mysecret.py>'
# SERVER = '<from mysecret.py>'

date_two_days_ago = datetime.now(UTC).date() - timedelta(days=2)
date_two_weeks_ago = datetime.now(UTC).date() - timedelta(days=14)

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
start_date = date.today() - timedelta(days=180)

# Get date, subject and body len of all emails from INBOX folder
with MailBox(SERVER).login(EMAIL_ADDRESS, PASSWORD) as mailbox:
    for msg in mailbox.fetch(A(date_gte=start_date), headers_only=True):
        if msg.from_ in delete_unseen_after_2_weeks\
            and msg.date.date() <= date_two_weeks_ago\
            and consts.MailMessageFlags.FLAGGED  not in msg.flags:

            uids_to_delete.append(msg.uid)

        elif msg.from_ in delete_seen_after_2_days\
            and msg.date.date() <= date_two_days_ago\
            and consts.MailMessageFlags.FLAGGED not in msg.flags\
            and consts.MailMessageFlags.SEEN in msg.flags:

            uids_to_delete.append(msg.uid)
    
    print("Moving {} mails to Trash.".format(len(uids_to_delete)))
    mailbox.move(uids_to_delete, 'Trash')
