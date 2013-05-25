import datetime, re

def parseArgs(args, title="", desc="", pri=0, due=None, tags=None):
    # hack to stop default tags accumulating on successive calls
    if tags is None:
        tags = []
    # first generic parameter regarded as task title
    needTitle = True
    for arg in args:
        # ~ description
        if arg[0] == "~":
            desc = arg[1:]
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
            try:
                due = datetime.datetime.strptime(arg[1:], "%d/%m/%Y|%H:%M:%S")
            except ValueError:
                pass
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
    # return parsed values
    return title, desc, pri, due, tags

def trunc(string, max):
    # truncate and add ellipse (of length 3) to long strings
    if len(string) > max - 3:
        string = string[:max - 3] + "..."
    return string

if __name__ == "__main__":
    print("You can't run this directly.  See README.md.")
