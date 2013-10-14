# utility functions
from DoX.util import *

# some more useful imports
import datetime, re

# task: a thing to do on the to-do list
#     id: assigned dynamically based on list position
#     title: name of the task
#     desc: additional description
#     pri: task priority, 0-3
#     due: date/time when task is due, (date/time, has time?)
#     repeat: when the task should repeat, (time delta, 
#     tags: categories assigned to task, [tag 1, tag 2, ...]
class task:
    def __init__(self, id=None, title="", desc="", pri=0, due=None, repeat=None, tags=None):
        # set values if given
        self.id = id
        self.title = title
        self.desc = desc
        self.pri = pri
        self.due = due
        self.repeat = repeat
        if not tags:
            tags = []
        self.tags = tags
        pass
    def parse(self, line):
        # split by space, keep quoted params intact
        args = shlexSplit(line)
        # empty line, return null
        if not len(args):
            return None
        # set fields
        self.id, self.title, self.desc, self.pri, self.due, self.repeat, self.tags = parseArgs(args)
        # return new task
        return self
    # prints in DoX string format
    def __str__(self):
        return formatArgs(self.id, self.title, self.desc, self.pri, self.due, self.repeat, self.tags)
    # prints developer view of object
    def __repr__(self):
        return "task(id=\"{}\", title=\"{}\", desc=\"{}\", pri={}, due={}, repeat={}, tags={})".format(self.id, self.title, self.desc, self.pri, self.due, self.repeat, self.tags)
    # comparison method for APIs to check all fields
    def __eq__(self, other, checkId=True):
        equal = True
        fields = ["title", "desc", "pri", "due", "repeat", "tags"]
        if checkId:
            fields.append("id")
        for field in fields:
            equal &= (getattr(self, field) == getattr(other, field))
        return equal

if __name__ == "__main__":
    print("You can't run this directly.  See README.md.")
