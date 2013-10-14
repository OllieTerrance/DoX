# some useful imports
import datetime, os, re, shlex, sys, time

# wrapper for shlex.split to support Unicode strings in Python 2.x
def shlexSplit(string):
    if sys.version_info >= (3,):
        # Python 3.x natively support Unicode, just use that
        return shlex.split(string)
    else:
        # encode string, split, then decode parts
        return map(lambda s: s.decode("UTF8"), shlex.split(string.encode("utf-8")))

# takes a string of arguments and parses the details out (optional default values for updating)
def parseArgs(args, id=None, title="", desc="", pri=0, due=None, repeat=None, tags=None):
    # hack to stop default tags accumulating on successive calls
    if tags is None:
        tags = []
    # first generic parameter regarded as task title
    needTitle = True
    for arg in args:
        # $ identifier (hex)
        if re.match("^\$[0-9a-f]{5}$", arg) and not id == False:
            id = arg[1:]
        # ~ description
        elif arg[0] == "~" and len(arg) > 1:
            desc = arg[1:].replace("|", "\n")
        # ! priority (numerical)
        elif re.match("^![0-3]$", arg):
            pri = int(arg[1])
        # ! priority (bang)
        elif re.match("^!{1,3}$", arg):
            pri = len(arg)
        # 0 (zero) priority
        elif arg == "0":
            pri = 0
        # @ due date
        elif arg[0] == "@" and len(arg) > 1:
            keywords = arg[1:].split("|")
            if len(keywords) == 1:
                keywords.append("")
            # attempt to parse
            due = parseDateTime(keywords[0], keywords[1])
        # & repeat
        elif arg[0] == "&" and len(arg) > 1:
            repeat = arg[1:]
            fromToday = False
            # repeat from today instead of from due date
            if repeat[-1] == "*":
                repeat = repeat[:-1]
                fromToday = True
            # aliases
            if repeat in ["daily", "day", "every day"]:
                repeat = 1
            elif repeat in ["weekly", "week"]:
                repeat = 7
            elif repeat in ["fortnightly", "fortnight", "2 weeks"]:
                repeat = 14
            else:
                # no matches, treat as integer
                try:
                    repeat = int(repeat)
                except ValueError:
                    repeat = None
            if repeat:
                repeat = (repeat, fromToday)
        # # tags
        elif arg[0] == "#" and len(arg) > 1:
            tag = arg[1:]
            if tag.lower() in [x.lower() for x in tags]:
                tags = [x for x in tags if not x.lower() == tag.lower()]
            else:
                tags.append(tag)
        # generic
        elif needTitle:
            title = arg
            needTitle = False
    # can't repeat without due date
    if repeat and not due:
        # make it due today
        due = (datetime.datetime.combine(datetime.datetime.today().date(), datetime.time()), False)
    # return parsed values
    return id, title, desc, pri, due, repeat, tags

# take a set of values and format them back into a string
def formatArgs(id=None, title="", desc="", pri=0, due=None, repeat=None, tags=None):
    args = []
    if title:
        # just print title
        args.append(quote(title))
    if desc:
        # description with line breaks converted
        args.append("~{}".format(quote(desc.replace("\n", "|"))))
    if pri:
        # basic priority if not 0
        args.append("!{}".format(pri))
    if due:
        # due date in standard format
        dueStr = due[0].strftime("@%d/%m/%Y")
        if due[1]:
            dueStr = due[0].strftime("@%d/%m/%Y|%H:%M:%S")
        args.append(dueStr)
    if repeat:
        # repeat as a number
        repeatStr = "&{}".format(repeat[0])
        if repeat[1]:
            repeatStr += "*"
        args.append(repeatStr)
    if len(tags):
        # individual tags
        for tag in tags:
            args.append("#{}".format(quote(tag)))
    if id:
        args.append("${}".format(id))
    # return formatted string
    return " ".join(args)

def parseDateTime(date, time):
    date = date.lower()
    time = time.lower()
    # aliases for days
    days = {
        "monday": 0,
        "mon": 0,
        "tuesday": 1,
        "tues": 1,
        "tue": 1,
        "wednesday": 2,
        "wed": 2,
        "thursday": 3,
        "thurs": 3,
        "thur": 3,
        "thu": 3,
        "friday": 4,
        "fri": 4,
        "saturday": 5,
        "sat": 5,
        "sunday": 6,
        "sun": 6
    }
    today = datetime.datetime.combine(datetime.datetime.today().date(), datetime.time())
    thisDate = None
    # basic string understanding
    if date == "today":
        thisDate = today
    elif date == "tomorrow":
        thisDate = today + datetime.timedelta(days=1)
    elif date == "yesterday":
        thisDate = today + datetime.timedelta(days=-1)
    elif date in ["week", "next week"]:
        thisDate = today + datetime.timedelta(days=7)
    elif date in days:
        # compare given day with today
        day = days[date]
        thisDay = today.weekday()
        delta = day - thisDay
        # shift by a week if already passed
        if delta <= 0:
            delta += 7
        thisDate = today + datetime.timedelta(days=delta)
    else:
        # no matches, try standard parse
        try:
            thisDate = datetime.datetime.strptime(date, "%d/%m/%Y")
        except ValueError:
            try:
                thisDate = datetime.datetime.strptime(date, "%d/%m").replace(year=today.year)
            except ValueError:
                try:
                    thisDate = datetime.datetime.strptime(date, "%d").replace(year=today.year, month=today.month)
                except ValueError:
                    pass
    # match found, now try to find a time
    if thisDate:
        due = (thisDate, False)
        # if a time is specified
        if time:
            thisTime = None
            if time == "now":
                thisTime = datetime.datetime.today()
            else:
                # no matches, try standard parse
                try:
                    thisTime = datetime.datetime.strptime(time, "%H:%M:%S")
                except ValueError:
                    try:
                        thisTime = datetime.datetime.strptime(time, "%H:%M")
                    except ValueError:
                        try:
                            thisTime = datetime.datetime.strptime(time, "%H")
                        except ValueError:
                            pass
            if thisTime:
                due = (datetime.datetime.combine(thisDate.date(), thisTime.time()), True)
    # no date specified
    else:
        due = None
    return due

# trim and ellipse a string of long length
def trunc(string, max):
    if len(string) > max - 3:
        string = string[:max - 3] + "..."
    return string

# wrap multi-word strings in quotes
def quote(string):
    if re.search(" ", string):
        return "\"{}\"".format(string.replace("\"", "\\\""))
    return string

# print the due date relatively if possible
def prettyDue(due):
    date = due[0].date()
    time = due[0].time()
    string = date.strftime("%d/%m/%Y")
    today = datetime.datetime.today().date()
    if date == today:
        string = "Today"
    elif date == today + datetime.timedelta(days=1):
        string = "Tomorrow"
    elif date == today + datetime.timedelta(days=-1):
        string = "Yesterday"
    elif today < date < today + datetime.timedelta(days=7):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        string = days[date.weekday()]
    if due[1]:
        string += " " + time.strftime("%H:%M:%S" if time.second else "%H:%M")
    return string

# print the repeat timeout nicely if possible
def prettyRepeat(repeat):
    days = repeat[0]
    string = "Every {} days".format(days)
    if days == 1:
        string = "Daily"
    elif days == 7:
        string = "Weekly"
    elif days == 14:
        string = "Fortnightly"
    if repeat[1]:
        string += " *"
    return string

if __name__ == "__main__":
    print("You can't run this directly.  See README.md.")
