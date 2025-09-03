# Simple library to build stuff
# (c) zboxjpg

from datetime import datetime
from enum import Enum, auto
import sys
import time

class Platform(Enum):
    LINUX    = auto()
    WIN32    = auto()
    CYGWIN   = auto()
    MSYS     = auto()
    MACOSX   = auto()
    OS2      = auto()
    OS2EMX   = auto()
    RISCOS   = auto()
    ATHEOS   = auto()
    FREEBSD6 = auto()
    FREEBSD7 = auto()
    FREEBSD8 = auto()
    FREEBSDN = auto()

def GetPlatform():
    match sys.platform:
        case "linux" | "linux2": return Platform.LINUX
        case "win32": return Platform.WIN32
        case "cygwin": return Platform.CYGWIN
        case "msys": return Platform.MSYS
        case "darwin": return Platform.MACOSX
        case "os2": return Platform.OS2
        case "os2emx": return Platform.OS2EMX
        case "riscos": return Platform.RISCOS
        case "atheos": return Platform.ATHEOS
        case "freebsd6": return Platform.FREEBSD6
        case "freebsd7": return Platform.FREEBSD7
        case "freebsd8": return Platform.FREEBSD8
        case "freebsdN": return Platform.FREEBSDN
        case _: raise Exception("Undefined platform `%s`(???)" % (sys.platform))

class Status(Enum):
    OK      = auto()
    ERROR   = auto()

class Task():
    """Task class, that contains task itself and args
    
    cmd -> command

    com -> comment (def. None)"""
    def __init__(self, cmd, com = None):
        self.args = []
        self.cmd = cmd
        self.com = com

    def AddFlag(self, flag = ""):
        """
        Add flag to task
        
        e.g. .AddArg("-v")
        """
        self.args.append(flag)

        return self
    
    def AddArg(self, arg = "", flag = ""):
        """
        Add argument to task

        e.g. .AddArg("main.cpp") OR .AddArg("app", "-o")
        """
        if flag: self.args.extend([flag, arg])
        else: self.args.append(arg)

        return self

    def GetFullTask(self):
        """
        Return task as list

        e.g. ['g++', 'main.cpp', '-o', 'app']
        """
        full_task = [self.cmd]
        full_task.extend(self.args)
        return full_task
    
class Builder():
    "Builder class that contains tasks and used to run tasks sync & async"
    def __init__(self):
        self.tasks : list[Task] = []

    def ClearTasks(self):
        self.tasks = []
        return self

    def AddTask(self, task : Task):
        """
        Add task to builder

        e.g. .AddTask(Task("g++").AddArg("main.cpp").AddArg("app", "-o"))
        """
        self.tasks.append(task)
        return self

    def CMDRun(self):
        "Run tasks"
        start_time = time.time()
        import subprocess as sp
        for task in self.tasks:
            ft = task.GetFullTask()
            if task.com: print(task.com)
            else: 
                print("[SB-CMD]", datetime.now().strftime("%H.%M.%S"), "RUNNING > ", " ".join(ft))
            proc = sp.run(ft)
            res_time = time.time() - start_time
            if proc.returncode:
                print("\n[SB-CMD]", datetime.now().strftime("%H.%M.%S"), "EXITCODE > ", proc.returncode)
                print(f"[SB-CMD] Build finished in just {res_time:.3f}s")
                return Status.ERROR
            print(f"[SB-CMD] Build finished in just {res_time:.3f}s")
        return Status.OK
