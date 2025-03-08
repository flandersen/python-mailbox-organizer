from datetime import date, timedelta

from imap_tools import A, MailBox

from mysecrets import EMAIL_ADDRESS, PASSWORD, SERVER


# Load sender lists from files
def load_senders_from_file(filename):
    try:
        with open(filename, "r") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()


delete_seen = load_senders_from_file("delete-seen-after-two-days.list")
delete_unseen = load_senders_from_file("delete-unseen-after-2-weeks.list")

senders = {}
start_date = date.today() - timedelta(days=180)

# Get date, subject, and body length of all emails from INBOX folder
with MailBox(SERVER).login(EMAIL_ADDRESS, PASSWORD) as mailbox:
    for msg in mailbox.fetch(A(date_gte=start_date), headers_only=True):
        sender = msg.from_
        senders[sender] = senders.get(sender, 0) + 1

# Print only senders with exactly 1 email, excluding senders in delete lists
for sender, count in senders.items():
    if count == 1 and sender not in delete_seen and sender not in delete_unseen:
        print(f"{sender}: {count}")
