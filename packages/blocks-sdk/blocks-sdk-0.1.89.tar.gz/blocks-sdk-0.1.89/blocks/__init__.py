from .repo import Repo
from .on import OnClass
from .task import TaskClass
from .state import BlocksState
from .utils import bash, experimental_bash
from .git import Git
from .config import Config

config = Config()
git = Git(config)
repo = Repo(config)
state = BlocksState()
task = TaskClass.get_decorator(state)
on = OnClass.get_decorator(state)