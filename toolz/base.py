#!/usr/bin/env python3

import re

__description__ = "common functions module"
__author__ = "Choops <choopsbd@gmail.com>"

c0 = "\33[0m"
ce = "\33[31m"
cok = "\33[32m"
cw = "\33[33m"
ci = "\33[36m"

error = f"{ce}E{c0}:"
done = f"{cok}OK{c0}:"
warning = f"{cw}W{c0}:"


def yesno(question, default="n"):
    """
    Ask a '"yes or no' question with a default choice defined as 'n'
    Return True/False for 'Yes'/'No'
    """

    def_indic = "[y/N]"

    if default.lower() == "y":
        def_indic = "[Y/n]"

    answer = input(f"{question} {def_indic} ? ").lower()

    if answer == "":
        answer = default.lower()
    elif not re.match('^(y|yes|n|no)$', answer):
        print(f"{error} Invalid answer '{answer}'")
        return yesno(question, default)

    return answer.startswith("y")
