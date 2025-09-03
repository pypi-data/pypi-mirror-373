from pydelfini.delfini_core.api.admin import admin_tasks_results
from pydelfini.delfini_core.api.admin import admin_tasks_schedules
from pydelfini.delfini_core.api.admin import admin_tasks_stats

from .base_commands import BaseCommands


class TasksCommands(BaseCommands):
    """Queries against the task backend"""

    def stats(self) -> None:
        """Retrieve task statistics.

        Admin access is required.

        """
        tasks_stats = admin_tasks_stats.sync(client=self.core)

        self._output(tasks_stats.to_dict())

    def schedules(self) -> None:
        """Retrieve scheduled tasks.

        Admin access is required.

        """
        tasks_schedules = admin_tasks_schedules.sync(client=self.core)

        self._output(tasks_schedules.to_dict())

    @BaseCommands._with_arg("--id", help="task UUID")
    @BaseCommands._with_arg("--idemkey", help="task idemkey or schedule name")
    def results(self) -> None:
        """Retrieve results for a provided task ID or idemkey.

        A task schedule name can be provided as an idemkey to retrieve
        results from that scheduled task.

        Admin access is required.

        """
        if self.args.id:
            results = admin_tasks_results.sync(task_id=self.args.id, client=self.core)
        elif self.args.idemkey:
            results = admin_tasks_results.sync(
                task_idemkey=self.args.idemkey, client=self.core
            )
        else:
            raise ValueError("must provide either --id or --idemkey")

        self._output(results.to_dict())
