#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    An asynchronous task scheduler, with cron syntax, intervals, limits,
#    dynamic configuration, and optional vault integration.
#    Copyright (C) 2025  PyAsyncScheduler

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
An asynchronous task scheduler, with cron syntax, intervals, limits,
dynamic configuration, and optional vault integration.
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
An asynchronous task scheduler, with cron syntax, intervals, limits,
dynamic configuration, and optional vault integration.
"""
__url__ = "https://github.com/mauricelambert/PyAsyncScheduler"

# __all__ = []

__license__ = "GPL-3.0 License"
__copyright__ = """
PyAsyncScheduler  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
copyright = __copyright__
license = __license__

print(copyright)


from typing import (
    Any,
    Awaitable,
    Callable,
    Deque,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    Set,
    Coroutine,
    TypeVar,
)
from asyncio import (
    Queue,
    create_task,
    gather,
    get_event_loop,
    run,
    sleep,
    start_server,
    StreamReader,
    StreamWriter,
)
from types import SimpleNamespace, FunctionType
from collections import defaultdict, deque
from datetime import datetime, timedelta
from sys import exit, argv, stderr
from collections import namedtuple
from dataclasses import dataclass
from functools import partial
from itertools import product
from threading import Thread
from getpass import getpass
from string import Template
from csv import DictReader
from warnings import warn
from pathlib import Path
from json import loads

try:
    from PySimpleVault import PasswordVault
except ImportError:
    warn(
        "Vault is not loaded. Secrets decryption is unavailable.",
        category=UserWarning,
        stacklevel=2,
    )
    PasswordVault = TypeVar("PasswordVault")
    vault_imported = False
else:
    vault_imported = True


NoneType = type(None)
Json = TypeVar("Json", Dict, List, str, int, float, NoneType)


class TaskLimiter:
    """
    Per-instance execution limiter using a sliding time window.

    This limiter *delays* executions instead of dropping them so that
    "every instance runs" as required. Use :meth:`await_permit` to
    asynchronously wait until the next execution is allowed.

    Args:
        limit: Maximum number of executions allowed within ``period_seconds``.
        period_seconds: Sliding window size, in seconds.
    """

    def __init__(self, limit: int, period_seconds: int):
        self.limit: int = int(limit)
        self.period_seconds: int = int(period_seconds)
        self.timestamps: Deque[float] = deque()

    def _prune(self) -> None:
        """
        This method prune timestamps that are outside the sliding window.
        """

        now = datetime.now().timestamp()
        while (
            self.timestamps and self.timestamps[0] <= now - self.period_seconds
        ):
            self.timestamps.popleft()

    async def await_permit(self) -> None:
        """
        This method wait until an execution slot is available, then record the run.
        """

        while True:
            self._prune()
            if len(self.timestamps) < self.limit:
                self.timestamps.append(datetime.now().timestamp())
                return None

            now = datetime.now().timestamp()
            wait_for = max(
                (self.timestamps[0] + self.period_seconds) - now, 0.1
            )
            await sleep(wait_for)


class CronSchedule:
    """
    Lightweight 5-field cron expression evaluator (no external libraries).

    Supports lists ",", ranges "-", steps "/", and wildcard "*".

    Fields: minute hour day month weekday (0=Monday per datetime.weekday()).
    Note: Many crons use 0=Sunday, 6=Saturday; here we map 0-6 to Python's
    Monday(0)..Sunday(6). If you need Sunday-based 0..6, set
    ``use_sunday_zero=True``.
    """

    def __init__(self, cron_expression: str, use_sunday_zero: bool = False):
        parts = cron_expression.strip().split()
        if len(parts) != 5:
            raise ValueError("Cron expression must have exactly 5 fields")

        self.minutes = self._parse_field(parts[0], 0, 59)
        self.hours = self._parse_field(parts[1], 0, 23)
        self.days = self._parse_field(parts[2], 1, 31)
        self.months = self._parse_field(parts[3], 1, 12)
        self.weekdays = self._parse_field(parts[4], 0, 6)
        self.use_sunday_zero = use_sunday_zero

    def _parse_field(
        self, field: str, min_value: int, max_value: int
    ) -> Set[int]:
        """
        This method parses a single cron field into a set of integers.
        """

        out: Set[int] = set()

        for part in field.split(","):
            part = part.strip()
            if not part:
                continue

            if part == "*":
                out.update(range(min_value, max_value + 1))
                continue

            step = 1
            if "/" in part:
                base, step_str = part.split("/", 1)
                step = max(1, int(step_str))
            else:
                base = part

            if base == "*":
                rng = range(min_value, max_value + 1)
            elif "-" in base:
                a, b = base.split("-", 1)
                start, end = int(a), int(b)
                rng = range(start, end + 1)
            else:
                rng = [int(base)]

            for v in rng:
                if min_value <= v <= max_value and (v - min_value) % step == 0:
                    out.add(v)

        return out

    def matches(self, match_datetime: datetime) -> bool:
        """
        Return True if ``match_datetime`` matches the cron expression at minute-level granularity.
        """

        weekday = match_datetime.weekday()
        if self.use_sunday_zero:
            weekday = (weekday + 1) % 7

        return (
            match_datetime.minute in self.minutes
            and match_datetime.hour in self.hours
            and match_datetime.day in self.days
            and match_datetime.month in self.months
            and weekday in self.weekdays
        )


def load_csv_rows(csv_path: str) -> List[Dict[str, str]]:
    """
    This function loads a CSV into a list of row dictionaries using the header row as keys.

    Args:
        csv_path: Path to a CSV file.
    Returns:
        List of rows mapping column name -> cell value (all strings).
    """

    rows: List[Dict[str, str]] = []

    with Path(csv_path).open(newline="", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            rows.append(
                {k: (v if v is not None else "") for k, v in row.items()}
            )

    return rows


def expand_from_csvs(
    template: str, csv_paths: Sequence[str], **additional_data
) -> List[Tuple[str, Dict[str, str]]]:
    """
    This function builds the Cartesian product of multiple CSVs and render a Template per combo.

    For each combination of one row from each CSV, merge the row dicts (later
    CSVs overwrite keys on collision), then render the ``template`` with
    ``string.Template.safe_substitute``.

    Args:
        template: A string.Template with placeholders like ``${user}``.
        csv_paths: A list of CSV file paths.

    Returns:
        A list of tuples: (rendered_config_string, merged_mapping_dict).
    """

    template = Template(template)
    row_sets: List[List[Dict[str, str]]] = (
        [load_csv_rows(p) for p in csv_paths] if csv_paths else [[]]
    )

    if not row_sets or not row_sets[0]:
        rendered = template.safe_substitute({})
        return [(rendered, {})]

    rendered_list: List[Tuple[str, Dict[str, str]]] = []
    for combo in product(*row_sets):
        merged: Dict[str, str] = {}
        for row in combo:
            merged.update(row)
        merged.update(additional_data)
        rendered = template.safe_substitute(merged)
        rendered_list.append((rendered, merged))

    return rendered_list


class TaskScheduler:
    """
    Secure, dependency-free task scheduler supporting cron/interval/sleep,
    per-time-window limits, async workers, optional threading, runtime task
    registration, and CSV-based wordlists -> Template expansion.

    Configuration schema per task (JSON):

    {
      "template": "https://${edr_user}:${edr_password}@edr.com/foo?u=${user}&p=${pass}",
      "csv_inputs": ["users.csv", "passes.csv"],
      "credentials": {"edr": {"category": "EDR", "role": "events_reader"}},
      "cron": "*/5 * * * *",
      "limit": {"max_executions": 100, "per_seconds": 60},
      "instance_spacing": 1
    }

    {
      "template": "https://api/foo?u=${user}&p=${pass}",
      "csv_inputs": ["users.csv", "passes.csv"],
      "start_time": "2025-06-22T00:00:00",
      "end_time":   "2025-06-22T06:00:00",
      "occurrences": 12
    }

    {
      "template": "https://api/foo?u=${user}&p=${pass}",
      "csv_inputs": ["users.csv", "passes.csv"],
      "sleep": 3600
    }

    Notes:
    - Each *instance* is one rendered template string from CSV rows.
    - If a limit is set, the limiter *delays* launches to honor the window.
    - If a run cycle takes longer than the nominal schedule period, the next
      cycle will start immediately after the current one completes (i.e., run late).
    - For threading: if the provided ``start_callable`` returns a ``threading.Thread``
      (not started), the scheduler will ``start()`` it and later ``join()`` it.
      To pass back a result from threads, expose a ``.result`` attribute on the
      thread object (optional). Async callables should return an awaitable.
    """

    def __init__(
        self,
        start_callable: Callable[[str], Union[Awaitable[Any], Thread, None]],
        process_result: Optional[Callable[[Any, Dict[str, Any]], None]] = None,
        worker_count: int = 4,
        external_coroutines: List[Coroutine] = [],
        vault: PasswordVault = None,
    ):
        self._results: Dict[str, Json] = {}
        self._start_callable = start_callable
        self._process_result = process_result or partial(
            default_handle_result, self._results
        )
        self._worker_count = max(1, int(worker_count))
        self._vault = vault

        self._tasks: List[Dict[str, Json]] = []
        self._queue: Queue[Tuple[str, Dict[str, Any]]] = Queue()
        self._limiters: Dict[str, TaskLimiter] = {}
        self._running_cycles: Dict[str, bool] = defaultdict(lambda: False)
        self._pending_cycle: Dict[str, bool] = defaultdict(lambda: False)
        self._external_coroutines = external_coroutines

    @staticmethod
    def check_and_build_task(
        task_config: Dict[str, Union[str, int, List[str]]],
        task: Dict[str, Json],
    ) -> None:
        """
        This method checks the task format and attributes.

        Raise ValueError or TypeError if a value is invalid.
        """

        now = datetime.now()

        if "template" not in task_config:
            raise ValueError("url must be present")

        if not isinstance(task_config["template"], str):
            raise TypeError("url must be a string")

        if "limit" in task_config:
            limit = task_config["limit"]

            if not isinstance(limit, dict):
                raise TypeError("limit must be a dict")

            if (
                "max_executions" not in limit
                or "per_seconds" not in limit
                or len(limit) != 2
            ):
                raise ValueError("Invalid limit format")

            if not isinstance(limit["max_executions"], int) or not isinstance(
                limit["per_seconds"], int
            ):
                raise TypeError(
                    "max_executions and per_seconds must be integers"
                )

        if "csv_inputs" in task_config:
            if not isinstance(task_config["csv_inputs"], list):
                raise TypeError("csv_inputs must be a dict")

            for inputs in "csv_inputs":
                if not isinstance(inputs, str):
                    raise ValueError(
                        "csv_inputs each element must be a string"
                    )

        if "instance_spacing" in task_config:
            if not isinstance(task_config["instance_spacing"], (int, float)):
                raise TypeError("instance_spacing must be a number")

            if task_config["instance_spacing"] <= 0:
                raise ValueError("instance_spacing must be greater than 0")

        if "credentials" in task_config:
            credentials = task_config["credentials"]

            if isinstance(credentials, dict):
                raise TypeError("credentials must be a dict")

            for name, credential in credentials.items():
                if not isinstance(name, str):
                    raise TypeError("keys in credentials must be a string")

                if "category" in credentials and "role" in credentials:
                    raise ValueError(
                        "category and role must be defined in all credentials"
                    )

                if not isinstance(
                    credentials["category"], str
                ) or not isinstance(credentials["role"], str):
                    raise TypeError(
                        "credentials.category and credentials.role must be a string"
                    )

        if "sleep" in task_config:
            if "cron" in task_config:
                raise ValueError("sleep and cron can't be set")

            if (
                "occurrences" in task_config
                or "start_time" in task_config
                or "end_time" in task_config
            ):
                raise ValueError(
                    "sleep and (occurrences OR start_time OR end_time) can't be set"
                )

            if not isinstance(task_config["sleep"], int):
                raise TypeError("sleep must be an integer")

            if task_config["sleep"] <= 0:
                raise ValueError("sleep must be greater than 0")

            task["_next_run"] = now

        elif "cron" in task_config:
            if (
                "occurrences" in task_config
                or "start_time" in task_config
                or "end_time" in task_config
            ):
                raise ValueError(
                    "cron and (occurrences OR start_time OR end_time) can't be set"
                )

            if not isinstance(task_config["cron"], str):
                raise TypeError("cron must be a string")

            task["_cron"] = CronSchedule(task_config["cron"])
            task["_last_checked_minute"] = now.replace(
                second=0, microsecond=0
            ) - timedelta(minutes=1)

        elif (
            "occurrences" in task_config
            and "start_time" in task_config
            and "end_time" in task_config
        ):
            if not isinstance(task_config["occurrences"], int):
                raise TypeError("occurrences must be an integer")

            occurences = task_config["occurrences"]
            if occurences <= 0:
                raise ValueError("occurrences must be greater than 0")

            if not isinstance(task_config["start_time"], str):
                raise TypeError("start_time must be a string")

            if not isinstance(task_config["end_time"], str):
                raise TypeError("end_time must be a string")

            start_time = task["_start_time"] = datetime.fromisoformat(
                task_config["start_time"]
            )
            end_time = task["_end_time"] = datetime.fromisoformat(
                task_config["end_time"]
            )

            if end_time <= start_time:
                raise ValueError("start_time should be greater than end_time")

            task["_next_run"] = start_time
            task["_interval"] = (end_time - start_time) / occurences

        else:
            raise ValueError(
                "sleep OR cron OR (occurrences and start_time and end_time) must be present"
            )

    def add_task(
        self,
        task_config: Dict[str, Union[str, int, List[str]]],
        id_: str = None,
        parent_id: str = None,
    ) -> Dict[str, Union[str, int, None]]:
        """
        This method registers a new task at runtime.
        """

        if not self._running_cycles or parent_id in self._running_cycles:
            meta_tasks = {
                "parent_id": parent_id,
                "configuration": task_config,
                "run": 0,
            }
            id_ = meta_tasks["id"] = id_ or hash(str(id(meta_tasks)))
            self.check_and_build_task(task_config, meta_tasks)
            self._tasks.append(meta_tasks)

        return {"code": 0, "output": id_, "error": None}

    if vault_imported:

        def open_vault(
            self, master_password: str, vault: str
        ) -> Dict[str, Union[str, int, None]]:
            """
            This method opens and sets password.
            """

            self._vault = PasswordVault.start(master_password, vault)
            return {"code": 0, "output": "success", "error": None}

    def get_task_result(
        self, id_: str, parent_id: str
    ) -> Dict[str, Union[str, int, None]]:
        """
        This method opens and sets password.
        """

        if id_ in self._results:
            result = self._results[id_]
            if result["parent_id"] == parent_id:
                return self._results.pop(id_)
            return {"code": 3, "output": None, "error": "Permission error."}
        elif id_ in self._running_cycles:
            return {"code": 1, "output": None, "error": "Task running."}
        return {"code": 2, "output": None, "error": "Task not found."}

    async def _worker_loop(self) -> None:
        """
        This method is the async worker: dispatch items from the queue.
        """

        while True:
            rendered_str, meta = await self._queue.get()
            try:
                await self._dispatch_one(rendered_str, meta)
            finally:
                self._queue.task_done()

    async def _dispatch_one(self, rendered: str, meta: Dict[str, Any]) -> None:
        """
        This method dispatchs a single instance using the provided start callable.

        If the start callable returns a Thread, it will be started and joined
        in a background asyncio Task without blocking other dispatches. If it
        returns an awaitable, it will be awaited in an asyncio Task. Any return
        value will be passed to ``process_result`` if provided.
        """

        maybe = self._start_callable(rendered, task_id=meta["id"])

        async def _handle_async(awaitable: Awaitable[Any]) -> None:
            try:
                result = await awaitable
                if self._process_result is not None:
                    self._process_result(result, meta)
            except Exception as error:
                if self._process_result is not None:
                    self._process_result(
                        SimpleNamespace(error=str(error)), meta
                    )

        def _handle_thread(function: FunctionType) -> None:
            try:
                result = function()
                if self._process_result is not None:
                    self._process_result(result, meta)
            except Exception as error:
                if self._process_result is not None:
                    self._process_result(
                        SimpleNamespace(error=str(error)), meta
                    )

        if isinstance(maybe, FunctionType):
            loop = get_event_loop()
            await loop.run_in_executor(None, _handle_thread, maybe)
        elif isinstance(maybe, Coroutine):
            create_task(_handle_async(maybe))
        else:
            if self._process_result is not None:
                self._process_result(None, meta)

    def _should_run_now(
        self, task: Dict[str, Any], now: Optional[datetime] = None
    ) -> bool:
        """
        This method checks whether a task is due to start a *cycle* now.

        A cycle is one full sweep launching all instances (CSV combinations),
        subject to limiter/spacing. If a cycle is already running, we mark a
        pending cycle and return False; it will run after completion.
        """

        now = now or datetime.now()
        task_config = task["configuration"]

        if "cron" in task:
            last = task["_last_checked_minute"]
            current_minute = now.replace(second=0, microsecond=0)
            probe = last
            while probe < current_minute:
                probe += timedelta(minutes=1)
                if task["_cron"].matches(probe):
                    task["_last_checked_minute"] = current_minute
                    return True
            task["_last_checked_minute"] = current_minute
            return False

        elif all(
            k in task_config for k in ("start_time", "end_time", "occurrences")
        ):
            next_run: datetime = task["_next_run"]
            end_time: datetime = task["_end_time"]
            if now >= next_run and now <= end_time:
                task["_next_run"] = next_run + task["_interval"]
                return True
            return False

        elif "sleep" in task:
            next_run = task["_next_run"]
            if now >= next_run:
                task["_next_run"] = now + timedelta(
                    seconds=task_config["sleep"]
                )
                return True
            return False

        return False

    def _get_limiter(
        self, task_id: str, task: Dict[str, Any]
    ) -> Optional[TaskLimiter]:
        """
        This method returns (and cache) a limiter for a task if configured, else None.
        """

        limit_config = task.get("limit")
        if not limit_config:
            return None

        key = task_id
        limiter = self._limiters.get(key)
        if limiter is None:
            limiter = TaskLimiter(
                limit_config["max_executions"], limit_config["per_seconds"]
            )
            self._limiters[key] = limiter

        return limiter

    async def _run_cycle(self, meta: Dict[str, Any]) -> None:
        """
        This method runs a full cycle for a task: render all instances and dispatch them.

        Respects per-instance limiter and ``instance_spacing`` (default 1s).
        """

        task = meta["configuration"]
        task_id = meta["id"]
        url = task["template"]
        csv_paths: List[str] = task.get("csv_inputs", [])
        instance_spacing: float = task.get("instance_spacing", 0)

        credentials = {}
        if vault_imported:
            for name, credential in task["credentials"].items():
                creds = self._vault.get_credentials(
                    credential["category"], credential["role"]
                )
                credentials[name + "_user"] = creds["username"]
                credentials[name + "_password"] = creds["password"]

        rendered_instances = expand_from_csvs(url, csv_paths, **credentials)

        self._running_cycles[task_id] = True
        limiter = self._get_limiter(task_id, task)

        for idx, (rendered, mapping) in enumerate(rendered_instances):
            meta["index"] = idx
            meta["mapping"] = mapping
            if limiter is not None:
                await limiter.await_permit()
            await self._queue.put((rendered, meta))
            await sleep(instance_spacing)

        await self._queue.join()
        self._running_cycles[task_id] = False

    async def _supervisor(self) -> None:
        """
        This method is the supervisor that evaluates schedules and triggers cycles.
        """

        while True:
            now = datetime.now()
            ids = []
            for id, task in enumerate(self._tasks):
                task_id = task["id"]
                due = self._should_run_now(task, now)

                if due is None:
                    ids.append(id)

                if due:
                    if self._running_cycles[task_id]:
                        self._pending_cycle[task_id] = True
                        continue
                    create_task(self._run_cycle(task))
                else:
                    if (
                        self._pending_cycle[task_id]
                        and not self._running_cycles[task_id]
                    ):
                        self._pending_cycle[task_id] = False
                        create_task(self._run_cycle(task))

            for id in ids:
                del task[id]

            await sleep(1.0)

    async def run(self) -> None:
        """
        Start workers and the supervisor. This never returns.
        """

        workers = [
            create_task(self._worker_loop()) for _ in range(self._worker_count)
        ]
        sup = create_task(self._supervisor())
        await gather(*workers, sup, *self._external_coroutines)


def default_handle_result(
    data: Dict[str, Dict[str, Union[int, str, None]]],
    response: Dict[str, Union[int, str, None]],
    task: Dict[str, Json],
) -> None:
    """
    The default handler to add a task result to results storage.
    """

    if response is None:
        data[task["id"]] = {
            "code": 127,
            "output": None,
            "error": "TypeError: Task must be callable",
        }
        return None

    data[task["id"]] = {
        "code": response.code,
        "output": response.body,
        "error": response.error,
    }


Arguments = namedtuple("Arguments", ["vault", "tasks_files"])


@dataclass
class Argument:
    names: List[str]
    value: Any = None


def parse_args(argv: List[str]) -> Arguments:
    """
    This function parses a command line with a single optional argument
    (--vault or -v) followed by the vault name, and collects the remaining
    strings as tasks configuration files.

    Args:
        argv: List of command-line arguments (typically sys.argv[1:]).

    Returns:
        Arguments: A named tuple with 'vault' (str or None)
                    and 'tasks_files' (list of strings).

    Raises:
        ValueError: If the vault flag is provided without a value.
    """

    flags = [Argument(["--vault", "-v"])]
    argv = argv.copy()
    length = len(argv)
    last = length - 1

    for flag in flags:
        for name in flag.names:
            counter = argv.count(name)
            if not counter:
                continue
            if counter > 1:
                raise ValueError(
                    "ArgmentError: " + name + " is defined multiples times"
                )

            position = argv.index(name)
            if position == last:
                raise ValueError("ArgmentError: value is required for " + name)

            if flag.value is not None:
                raise ValueError("ArgmentError: " + name + " is already set")

            del argv[position]
            flag.value = argv[position]
            del argv[position]

    return Arguments(flags[0].value, argv)


def main():
    """
    The main function to start the default scheduler services.

    Requirements are not optional.
    """

    from UrlHandler import get_task
    from JsonRpcExtended import AsyncServer, JsonRpcServer

    arguments = parse_args(argv[1:])
    server = AsyncServer("127.0.0.1", 8520)

    vault = (
        PasswordVault.start(
            master_password=getpass(), root_dir=arguments.vault
        )
        if arguments.vault and vault_imported
        else None
    )
    scheduler = TaskScheduler(
        start_callable=lambda x, **y: get_task(x, **y).code,
        worker_count=8,
        external_coroutines=[server.start()],
        vault=vault,
    )

    JsonRpcServer.register_function(scheduler.add_task, "add_task")
    if vault_imported:
        JsonRpcServer.register_function(scheduler.open_vault, "open_vault")
    JsonRpcServer.register_function(
        scheduler.get_task_result, "get_task_result"
    )

    scheduler._process_result = partial(
        default_handle_result, scheduler._results
    )

    if not arguments.tasks_files:
        print("Fatal error: Nothing to do", file=stderr)
        return 1

    for file in arguments.tasks_files:
        tasks_config = loads(Path(file).read_text())
        for t in tasks_config:
            scheduler.add_task(t)

    run(scheduler.run())
    return 0


if __name__ == "__main__":
    exit(main())
