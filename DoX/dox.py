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
    def getTask(self, id, isTasks=True):
        tasks = self.tasks if isTasks else self.done
        # id within range of list
        if 0 < id <= len(tasks):
            # return the task object
            return tasks[id - 1]
    def getAllTasks(self, isTasks=True):
        # return all tasks in the list
        return self.tasks if isTasks else self.done
    def getCount(self, isTasks=True):
        # return number of tasks in list
        return len(self.tasks) if isTasks else len(self.done)
    def addTask(self, title="", desc="", pri=0, due=None, repeat=None, tags=None):
        # create new task and store in list
        self.tasks.append(task(len(self.tasks) + 1, title, desc, pri, due, repeat, tags))
        return self
    def editTask(self, id, title="", desc="", pri=0, due=None, repeat=None, tags=None, isTasks=True):
        # fetch existing task
        taskObj = self.getTask(id, isTasks)
        # update values
        taskObj.title = title
        taskObj.desc = desc
        taskObj.pri = pri
        taskObj.due = due
        taskObj.repeat = repeat
        if not tags:
            tags = []
        taskObj.tags = tags
        return self
    def addTaskFromStr(self, line):
        # use task class parser instead
        tasks.append(task().parse(line))
        return self
    def moveTask(self, id, pos, isTasks=True):
        tasks = self.tasks if isTasks else self.done
        # new and old position different, and within range of list
        if not id == pos and 0 < id <= len(tasks) and 0 < pos <= len(tasks):
            # move task from current position (id) to new position
            tasks.insert(pos - 1, tasks.pop(id - 1))
            # replace original list
            if isTasks:
                self.tasks = tasks
            else:
                self.done = tasks
            # fix ids to close gap
            self.renumberTasks()
        return self
    def doneTask(self, id):
        # id within range of list
        if 0 < id <= len(self.tasks):
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
                # cancel repeat on original task (in case of undo)
                taskObj.repeat = None
            # move task from tasks list to done
            self.done.append(taskObj)
            # fix ids to close gap
            self.renumberTasks()
        return self
    def undoTask(self, id):
        # id within range of list
        if 0 < id <= len(self.done):
            # move task from done list to tasks
            self.tasks.append(self.done.pop(id - 1))
            # fix ids to close gap
            self.renumberTasks()
        return self
    def deleteTask(self, id, isTasks=True):
        tasks = self.tasks if isTasks else self.done
        # id within range of list
        if 0 < id <= len(tasks):
            # remove task from list
            tasks.pop(id - 1)
            # fix ids to close gap
            self.renumberTasks()
        return self
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
        return self
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
        return self
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
        return self
    def tasksFileLastMod(self, path=os.path.join(os.path.expanduser("~"), "DoX")):
        # return time of either file's last edit
        return datetime.datetime.fromtimestamp(max(os.path.getmtime(os.path.join(path, "tasks.txt")), os.path.getmtime(os.path.join(path, "done.txt"))))

if __name__ == "__main__":
    print("You can't run this directly.  See README.md.")
