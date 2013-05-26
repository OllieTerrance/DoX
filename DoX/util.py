# some useful imports
import datetime, os, re, time

# takes a set of arguments and parses the details out
def parseArgs(args, title="", desc="", pri=0, due=None, repeat=None, tags=None):
    # hack to stop default tags accumulating on successive calls
    if tags is None:
        tags = []
    # first generic parameter regarded as task title
    needTitle = True
    for arg in args:
        # ~ description
        if arg[0] == "~":
            desc = arg[1:].replace("\\", "\n")
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
        elif arg[0] == "@":
            keyword = arg[1:].lower().split("|")
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
            if keyword[0] == "today":
                thisDate = today
            elif keyword[0] == "tomorrow":
                thisDate = today + datetime.timedelta(days=1)
            elif keyword[0] == "yesterday":
                thisDate = today + datetime.timedelta(days=-1)
            elif keyword[0] in ["week", "next week"]:
                thisDate = today + datetime.timedelta(days=7)
            elif keyword[0] in days:
                # compare given day with today
                day = days[keyword[0]]
                thisDay = today.weekday()
                delta = day - thisDay
                # shift by a week if already passed
                if delta <= 0:
                    delta += 7
                thisDate = today + datetime.timedelta(days=delta)
            else:
                # no matches, try standard parse
                try:
                    thisDate = datetime.datetime.strptime(keyword[0], "%d/%m/%Y")
                except ValueError:
                    try:
                        thisDate = datetime.datetime.strptime(keyword[0], "%d/%m").replace(year=today.year)
                    except ValueError:
                        try:
                            thisDate = datetime.datetime.strptime(keyword[0], "%d").replace(year=today.year, month=today.month)
                        except ValueError:
                            pass
            # custom match found, now try to find a time
            if thisDate:
                due = (thisDate, False)
                # if a time is specified
                if len(keyword) > 1:
                    thisTime = None
                    if keyword[1] == "now":
                        thisTime = datetime.datetime.today()
                    else:
                        # no matches, try standard parse
                        try:
                            thisTime = datetime.datetime.strptime(keyword[1], "%H:%M:%S")
                        except ValueError:
                            try:
                                thisTime = datetime.datetime.strptime(keyword[1], "%H:%M")
                            except ValueError:
                                try:
                                    thisTime = datetime.datetime.strptime(keyword[1], "%H")
                                except ValueError:
                                    pass
                    if thisTime:
                        due = (datetime.datetime.combine(thisDate.date(), thisTime.time()), True)
        # & repeat
        elif arg[0] == "&":
            repeat = arg[1:]
            fromToday = False
            if repeat[-1] == "*":
                repeat = repeat[:-1]
                fromToday = True
            if repeat in ["daily", "day", "every day"]:
                repeat = 1
            elif repeat in ["weekly", "week"]:
                repeat = 7
            elif repeat in ["fortnightly", "fortnight", "2 weeks"]:
                repeat = 14
            else:
                try:
                    repeat = int(repeat)
                except ValueError:
                    repeat = None
            if repeat:
                repeat = (repeat, fromToday)
        # # tags
        elif arg[0] == "#":
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
    return title, desc, pri, due, repeat, tags

# trim and ellipse a string of long strings
def trunc(string, max):
    if len(string) > max - 3:
        string = string[:max - 3] + "..."
    return string

# wrap multi-word strings in quotes
def quote(string):
    if re.search(" ", string):
        return "\"{}\"".format(string)
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
