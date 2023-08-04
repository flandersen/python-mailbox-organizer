import re
from datetime import date

from imap_tools import A, MailBox, consts

from mysecrets import EMAIL_ADDRESS, PASSWORD, SERVER

# EMAIL_ADDRESS = '<from mysecret.py>'
# PASSWORD = '<from mysecret.py>'
# SERVER = '<from mysecret.py>'

class AutoFlag:
    _sender:str = ""
    _subject_pattern:str = ""

    @property
    def subject_pattern(self)->str:
        return self._subject_pattern

    def __init__(self, sender:str, subject_pattern:str) -> None:
        self._sender = sender
        self._subject_pattern = subject_pattern


auto_flags = {}

with open('auto-flag-mails.list', 'r') as reader:
    for line in reader:
        line = line.strip()       
        parts = line.split('|')

        if len(parts) == 1:
            sender = line
            title_regex = ""
        else:
            sender = parts[0]
            title_regex = parts[1]
        
        auto_flags[sender] = AutoFlag(sender, title_regex)


to_auto_flag = list()

# Get date, subject and body len of all emails from INBOX folder
with MailBox(SERVER).login(EMAIL_ADDRESS, PASSWORD) as mailbox:
    for msg in mailbox.fetch(A(date_gte=date(2023, 5, 1)), headers_only=True):
        if msg.from_ in auto_flags:
            auto_flag:AutoFlag = auto_flags[msg.from_]
            subject_pattern = auto_flag.subject_pattern

            if consts.MailMessageFlags.FLAGGED not in msg.flags:
                if subject_pattern == "":
                    to_auto_flag.append(msg.uid)
                else:
                    match = re.match(subject_pattern, msg.subject)
                    if match:
                        to_auto_flag.append(msg.uid)                

    if len(to_auto_flag) > 0:
        print("Flagging {} mails.".format(len(to_auto_flag)))
        mailbox.flag(to_auto_flag, flag_set=consts.MailMessageFlags.FLAGGED, value=True)
    else:
        print("Noting to flag.")
