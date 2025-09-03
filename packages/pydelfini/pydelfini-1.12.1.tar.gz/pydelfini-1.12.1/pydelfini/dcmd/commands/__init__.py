from .accounts import AccountsCommands
from .admin import AdminCommands
from .auth import AuthCommands
from .base_commands import BaseCommands
from .cde import CdeCommands
from .collection import CollectionCommands
from .groups import GroupsCommands
from .pdd import PddCommands
from .tasks import TasksCommands
from .users import UsersCommands


class Commands(BaseCommands):
    accounts = AccountsCommands
    admin = AdminCommands
    auth = AuthCommands
    cdeset = CdeCommands
    collection = CollectionCommands
    groups = GroupsCommands
    pdd = PddCommands
    tasks = TasksCommands
    users = UsersCommands
