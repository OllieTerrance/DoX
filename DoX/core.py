# task instance class
from DoX.task import *

# other useful imports
import copy, os, random, re

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
        # return the task object matching that ID
        return next((x for x in tasks if x.id == id), None)
    def getNthTask(self, pos, isTasks=True):
        tasks = self.tasks if isTasks else self.done
        # return the task object at that position
        return tasks[pos - 1] if 0 < pos <= len(tasks) else None
    def getAllTasks(self, isTasks=True):
        # return all tasks in the list
        return self.tasks if isTasks else self.done
    def getCount(self, isTasks=True):
        # return number of tasks in list
        return len(self.tasks) if isTasks else len(self.done)
    def idToPos(self, id, isTasks=True):
        tasks = self.tasks if isTasks else self.done
        # return the position of the task with that ID
        ids = [x.id for x in tasks]
        try:
            return ids.index(id) + 1
        except:
            pass
    def posToId(self, pos, isTasks=True):
        tasks = self.tasks if isTasks else self.done
        # return the ID of the task at that position
        return tasks[pos - 1].id if 0 < pos <= len(tasks) else None
    def addTask(self, title="", desc="", pri=0, due=None, repeat=None, tags=None):
        # create new task and store in list
        self.tasks.append(task(None, title, desc, pri, due, repeat, tags))
        # set IDs
        self.fixIDs()
        return self
    def editTask(self, id, title="", desc="", pri=0, due=None, repeat=None, tags=None, isTasks=True):
        # fetch existing task
        taskObj = self.getTask(id, isTasks)
        if taskObj:
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
    def moveTask(self, id, newPos, isTasks=True):
        self.moveNthTask(self.idToPos(id, isTasks), newPos, isTasks)
    def moveNthTask(self, pos, newPos, isTasks=True):
        tasks = self.tasks if isTasks else self.done
        # new and old position different, and within range of list
        if pos and not pos == newPos and 0 < pos <= len(tasks) and 0 < newPos <= len(tasks):
            # move task from current position (id) to new position
            tasks.insert(newPos - 1, tasks.pop(pos - 1))
            # replace original list
            if isTasks:
                self.tasks = tasks
            else:
                self.done = tasks
        return self
    def doneTask(self, id):
        self.doneNthTask(self.idToPos(id))
    def doneNthTask(self, pos):
        # position within range of list
        if 0 < pos <= len(self.tasks):
            # fetch task
            taskObj = self.tasks.pop(pos - 1)
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
                # remove original task ID (will receive a new one)
                taskObj.id = None
                # cancel repeat on original task (in case of undo)
                taskObj.repeat = None
            # move task from tasks list to done
            self.done.append(taskObj)
            # set IDs
            self.fixIDs()
        return self
    def undoTask(self, id):
        self.undoNthTask(self.idToPos(id, False))
    def undoNthTask(self, pos):
        # position within range of list
        if 0 < pos <= len(self.done):
            # move task from done list to tasks
            self.tasks.append(self.done.pop(pos - 1))
        return self
    def deleteTask(self, id, isTasks):
        self.deleteNthTask(self.idToPos(id, isTasks), isTasks)
    def deleteNthTask(self, pos, isTasks=True):
        tasks = self.tasks if isTasks else self.done
        # position within range of list
        if 0 < pos <= len(tasks):
            # remove task from list
            tasks.pop(pos - 1)
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
            taskObj = task().parse(line)
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
            taskObj = task().parse(line)
            # add to list
            if taskObj:
                self.done.append(taskObj)
                count += 1
        doneFile.close()
        # set IDs
        self.fixIDs()
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
    def newID(self):
        # generate a random ID
        return hex(random.randint(0, 1048575))[2:].zfill(5)
    def fixIDs(self):
        # list of IDs in use
        used = []
        # list of task objects to generate IDs for
        toGen = []
        for taskObj in self.tasks + self.done:
            if taskObj.id and taskObj.id not in used:
                used.append(taskObj.id)
            else:
                toGen.append(taskObj)
        for taskObj in toGen:
            # generate a new ID
            taskObj.id = self.newID()
            while id in used:
                taskObj.id = self.newID()
            used.append(taskObj.id)
    def tasksFileLastMod(self, path=os.path.join(os.path.expanduser("~"), "DoX")):
        # return time of either file's last edit
        return datetime.datetime.fromtimestamp(max(os.path.getmtime(os.path.join(path, "tasks.txt")), os.path.getmtime(os.path.join(path, "done.txt"))))

if __name__ == "__main__":
    print("You can't run this directly.  See README.md.")
