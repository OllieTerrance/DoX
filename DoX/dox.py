# task instance class
from task import *
# utility functions
from util import *

# other useful imports
import copy, os, re

# dox: API backbone - can be used by other applications
class dox:
    # task list
    tasks = []
    # completed tasks
    done = []
    # load tasks text file
    def __init__(self):
        self.loadTasks()
    def getTask(self, id):
        # id within range of list
        if id > 0 and id <= len(self.tasks):
            # return the task object
            return self.tasks[id - 1]
    def getDone(self, id):
        # id within range of list
        if id > 0 and id <= len(self.done):
            # return the task object
            return self.done[id - 1]
    def addTask(self, title="", desc="", pri=0, due=None, repeat=None, tags=None):
        # create new task and store in list
        self.tasks.append(task(len(self.tasks) + 1, title, desc, pri, due, repeat, tags))
    def editTask(self, id, title="", desc="", pri=0, due=None, repeat=None, tags=None):
        # fetch existing task
        taskObj = self.getTask(id)
        # update values
        taskObj.title = title
        taskObj.desc = desc
        taskObj.pri = pri
        taskObj.due = due
        taskObj.repeat = repeat
        if not tags:
            tags = []
        taskObj.tags = tags
    def addTaskFromStr(self, line):
        # use task class parser instead
        tasks.append(task().parse(line))
    def moveTask(self, id, pos):
        # new and old position different, and within range of list
        if not id == pos and id > 0 and id <= len(self.tasks) and pos > 0 and pos <= len(self.tasks):
            # move task from current position (id) to new position
            self.tasks.insert(pos - 1, self.tasks.pop(id - 1))
            # fix ids to close gap
            self.renumberTasks()
    def doneTask(self, id):
        # id within range of list
        if id > 0 and id <= len(self.tasks):
            # fetch task
            taskObj = self.tasks.pop(id - 1)
            # schedule a repeat
            if taskObj.repeat:
                taskCopy = copy.deepcopy(taskObj)
                delta = datetime.timedelta(days=taskCopy.repeat[0])
                # default to repeat from due date
                due = taskCopy.due[0] + delta
                if taskCopy.repeat[1]:
                    # repeat from today instead
                    due = datetime.datetime.combine(datetime.datetime.today().date() + delta, due.time())
                taskCopy.due = (due, taskCopy.due[1])
                self.tasks.append(taskCopy)
            # move task from tasks list to done
            self.done.append(taskObj)
            # fix ids to close gap
            self.renumberTasks()
    def undoTask(self, id):
        # id within range of list
        if id > 0 and id <= len(self.done):
            # move task from done list to tasks
            self.tasks.append(self.done.pop(id - 1))
            # fix ids to close gap
            self.renumberTasks()
    def deleteTask(self, id):
        # id within range of list
        if id > 0 and id <= len(self.tasks):
            # remove task from list
            self.tasks.pop(id - 1)
            # fix ids to close gap
            self.renumberTasks()
    def renumberTasks(self):
        count = 1
        for taskObj in self.tasks:
            # reset the id to the position in the list
            taskObj.id = count
            count += 1
        count = 1
        for taskObj in self.done:
            # reset the id to the position in the list
            taskObj.id = count
            count += 1
    def loadTasks(self, path=os.path.join(os.path.expanduser("~"), "DoX")):
        # empty/reset task lists (if previously loaded)
        self.tasks = []
        self.done = []
        # no DoX folder, create it
        if not os.path.exists(path):
            os.makedirs(path)
        tasksPath = os.path.join(path, "tasks.txt")
        # no tasks file, create it
        if not os.path.exists(tasksPath):
            open(tasksPath, "w").close()
        donePath = os.path.join(path, "done.txt")
        # no completed tasks file, create it
        if not os.path.exists(donePath):
            open(donePath, "w").close()
        configPath = os.path.join(path, "config.txt")
        # open tasks file
        tasksFile = open(tasksPath, "r")
        count = 1
        # loop through file
        for line in tasksFile:
            # parse line into task object
            taskObj = task().parse(count, line)
            # add to list
            if taskObj:
                self.tasks.append(taskObj)
                count += 1
        tasksFile.close()
        # open completed tasks file
        doneFile = open(donePath, "r")
        count = 1
        # loop through file
        for line in doneFile:
            # parse line into task object
            taskObj = task().parse(count, line)
            # add to list
            if taskObj:
                self.done.append(taskObj)
                count += 1
        doneFile.close()
    def saveTasks(self, path=os.path.join(os.path.expanduser("~"), "DoX")):
        # open tasks file for writing
        tasksPath = os.path.join(path, "tasks.txt")
        tasksFile = open(tasksPath, "w")
        for taskObj in self.tasks:
            # create DoX string format for task and add to file
            tasksFile.write(str(taskObj) + "\r\n")
        tasksFile.close()
        # open done file for writing
        tasksPath = os.path.join(path, "done.txt")
        tasksFile = open(tasksPath, "w")
        for taskObj in self.done:
            # create DoX string format for task and add to file
            tasksFile.write(str(taskObj) + "\r\n")
        tasksFile.close()
    def tasksFileLastMod(self, path=os.path.join(os.path.expanduser("~"), "DoX")):
        # return time of either file's last edit
        return datetime.datetime.fromtimestamp(max(os.path.getmtime(os.path.join(path, "tasks.txt")), os.path.getmtime(os.path.join(path, "done.txt"))))

if __name__ == "__main__":
    print("You can't run this directly.  See README.md.")
