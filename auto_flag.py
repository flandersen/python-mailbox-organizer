import re
from datetime import date, timedelta

from imap_tools import A, MailBox, consts

from mysecrets import EMAIL_ADDRESS, PASSWORD, SERVER


class AutoFlag:
    def __init__(self, sender: str, subject_pattern: str = "") -> None:
        self.sender = sender
        self.subject_pattern = subject_pattern

    @property
    def subject_pattern(self) -> str:
        return self._subject_pattern

    @subject_pattern.setter
    def subject_pattern(self, value: str) -> None:
        self._subject_pattern = value or ""


def load_auto_flags(file_path: str) -> dict:
    """Load auto-flag rules from a file."""
    auto_flags = {}
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            sender, title_regex = (line.split("|") + [""])[:2]
            auto_flags[sender] = AutoFlag(sender, title_regex)
    return auto_flags


def get_mails_to_flag(mailbox: MailBox, auto_flags: dict, start_date: date) -> list:
    """Fetch emails to be flagged based on sender and subject pattern."""
    to_auto_flag = []
    for msg in mailbox.fetch(A(date_gte=start_date), headers_only=True):
        if msg.from_ in auto_flags:
            auto_flag = auto_flags[msg.from_]
            subject_pattern = auto_flag.subject_pattern

            if consts.MailMessageFlags.FLAGGED not in msg.flags:
                if not subject_pattern or re.match(subject_pattern, msg.subject):
                    to_auto_flag.append(msg.uid)
    return to_auto_flag


def main():
    start_date = date.today() - timedelta(days=180)
    auto_flags = load_auto_flags("auto-flag-mails.list")

    with MailBox(SERVER).login(EMAIL_ADDRESS, PASSWORD) as mailbox:
        mails_to_flag = get_mails_to_flag(mailbox, auto_flags, start_date)

        if mails_to_flag:
            print(f"Flagging {len(mails_to_flag)} mails.")
            mailbox.flag(
                mails_to_flag, flag_set=consts.MailMessageFlags.FLAGGED, value=True
            )
        else:
            print("Nothing to flag.")


if __name__ == "__main__":
    main()
