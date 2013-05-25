# some more useful imports
import datetime, re, shlex, util

class task:
    def __init__(self):
        # empty task
        self.id = 0
        self.title = ""
        self.desc = ""
        self.pri = 0
        self.due = None
        self.tags = []
        pass
    def parse(self, id, line):
        # split by space, keep quoted params intact
        args = shlex.split(line)
        # empty line, return null
        if not len(args):
            return None
        # set new id
        self.id = id
        self.title, self.desc, self.pri, self.due, self.tags = util.parseArgs(args)
        # return new task
        return self
    def __str__(self):
        args = []
        if self.title:
            args.append(self.quote(self.title))
        if self.desc:
            args.append("~{}".format(self.quote(self.desc)))
        if self.pri:
            args.append("!{}".format(self.pri))
        if self.due:
            args.append(self.due.strftime("@%d/%m/%Y|%H:%M:%S"))
        if len(self.tags):
            for tag in self.tags:
                args.append("#{}".format(self.quote(tag)))
        return " ".join(args)
    def quote(self, arg):
        if re.search(" ", arg):
            return "\"{}\"".format(arg)
        return arg
    def __repr__(self):
        return "task(id={}, title=\"{}\", desc=\"{}\", pri={}, tags={})".format(self.id, self.title, self.desc, self.pri, self.tags)

if __name__ == "__main__":
    print("You can't run this directly.  See README.md.")
