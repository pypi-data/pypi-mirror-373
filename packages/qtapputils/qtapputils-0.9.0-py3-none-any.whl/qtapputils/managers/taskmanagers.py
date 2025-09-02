# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from uuid import UUID

# ---- Standard imports
from collections import OrderedDict
import uuid

# ---- Third party imports
from qtpy.QtCore import QObject, QThread, Signal

# ---- Local imports
from qtapputils.qthelpers import qtwait


class WorkerBase(QObject):
    """
    A worker to execute tasks without blocking the GUI.
    """
    sig_task_completed = Signal(object, object)

    def __init__(self):
        super().__init__()
        self._tasks: OrderedDict[Any, tuple[str, tuple, dict]] = OrderedDict()

    def _get_method(self, task: str):
        # Try direct, then fallback to underscore-prefixed (for backward
        # compatibility with older version of qtapputils).
        try:
            method = getattr(self, task)
        except AttributeError:
            method = getattr(self, '_' + task)
        return method

    def add_task(self, task_uuid4: Any, task: str, *args, **kargs):
        """
        Add a task to the stack.
        Parameters
        ----------
        task_uuid4 : UUID or any hashable
            Unique ID for the task.
        task : str
            The name of the method to execute.
        *args, **kargs :
            Arguments for the task.
        """
        self._tasks[task_uuid4] = (task, args, kargs)

    def run_tasks(self):
        """Execute the tasks that were added to the stack."""
        for task_uuid4, (task, args, kargs) in self._tasks.items():
            if task is not None:
                method_to_exec = self._get_method(task)
                returned_values = method_to_exec(*args, **kargs)
            else:
                returned_values = args
            self.sig_task_completed.emit(task_uuid4, returned_values)

        self._tasks.clear()
        self.thread().quit()


class TaskManagerBase(QObject):
    """
    A basic FIFO (First-In, First-Out) task manager.
    """
    sig_run_tasks_started = Signal()
    sig_run_tasks_finished = Signal()

    def __init__(self, verbose: bool = False):
        super().__init__()
        self.verbose = verbose

        self._worker = None

        self._task_callbacks: dict[uuid.UUID, Callable] = {}
        self._task_data: dict[uuid.UUID, tuple[str, tuple, dict]] = {}

        self._running_tasks = []
        self._queued_tasks = []
        self._pending_tasks = []
        # Queued tasks are tasks whose execution has not been requested yet.
        # This happens when we want the Worker to execute a list of tasks
        # in a single run. All queued tasks are dumped in the list of pending
        # tasks when `run_task` is called.
        #
        # Pending tasks are tasks whose execution was postponed due to
        # the fact that the worker was busy. These tasks are run as soon
        # as the worker becomes available.
        #
        # Running tasks are tasks that are being executed by the worker.

    @property
    def is_running(self):
        return not (len(self._running_tasks) == 0 and
                    len(self._pending_tasks) == 0 and
                    not self._thread.isRunning())

    def run_tasks(
            self, callback: Callable = None, returned_values: tuple = None):
        """
        Execute all the tasks that were added to the stack.

        Parameters
        ----------
        callback : Callable, optional
            A callback that will be called with the provided returned_values
            after the current queued tasks have been all executed.
        returned_values : tuple, optional
            A list of values that will be passed to the callback function when
            it is called.
        """
        if callback is not None:
            self.add_task(None, callback, returned_values)
        self._run_tasks()

    def add_task(self, task: str, callback: Callable, *args, **kargs):
        """Add a new task at the end of the queued tasks stack."""
        self._add_task(task, callback, *args, **kargs)

    def worker(self) -> WorkerBase:
        """Return the worker that is installed on this manager."""
        return self._worker

    def set_worker(self, worker: WorkerBase):
        """"Install the provided worker on this manager"""
        self._worker = worker
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run_tasks)

        # Connect the worker signals to handlers.
        self._worker.sig_task_completed.connect(self._handle_task_completed)

    # ---- Private API
    def _handle_task_completed(
            self, task_uuid4: uuid.UUID, returned_values: tuple) -> None:
        """
        Handle when a task has been completed by the worker.

        This is the ONLY slot that should be called after a task is
        completed by the worker.
        """
        # Run the callback associated with the specified task UUID if any.
        if self._task_callbacks[task_uuid4] is not None:
            try:
                self._task_callbacks[task_uuid4](*returned_values)
            except TypeError:
                # This means there is 'returned_values' is None.
                self._task_callbacks[task_uuid4]()

        # Clean up completed task.
        self._cleanup_task(task_uuid4)

        # Execute pending tasks if worker is idle.
        if len(self._running_tasks) == 0:
            if len(self._pending_tasks) > 0:
                self._run_pending_tasks()
            else:
                if self.verbose:
                    print('All pending tasks were executed.')
                self.sig_run_tasks_finished.emit()

    def _cleanup_task(self, task_uuid4: uuid.UUID):
        """Cleanup task associated with the specified UUID."""
        del self._task_callbacks[task_uuid4]
        del self._task_data[task_uuid4]
        if task_uuid4 in self._running_tasks:
            self._running_tasks.remove(task_uuid4)

    def _add_task(self, task: str, callback: Callable, *args, **kargs):
        """Add a new task at the end of the stack of queued tasks."""
        task_uuid4 = uuid.uuid4()
        self._task_callbacks[task_uuid4] = callback
        self._queued_tasks.append(task_uuid4)
        self._task_data[task_uuid4] = (task, args, kargs)

    def _run_tasks(self):
        """
        Execute all the tasks that were added to the stack of queued tasks.
        """
        self._pending_tasks.extend(self._queued_tasks)
        self._queued_tasks = []
        if len(self._running_tasks) == 0:
            self.sig_run_tasks_started.emit()
        self._run_pending_tasks()

    def _run_pending_tasks(self):
        """Execute all pending tasks."""
        if len(self._running_tasks) == 0 and len(self._pending_tasks) > 0:
            if self.verbose:
                print('Executing {} pending tasks...'.format(
                    len(self._pending_tasks)))

            # Even though the worker has executed all its tasks,
            # we may still need to wait a little for it to stop properly.
            try:
                qtwait(lambda: not self._thread.isRunning(), timeout=10)
            except TimeoutError:
                print("Error: unable to stop {}'s working thread.".format(
                    self.__class__.__name__))

            self._running_tasks = self._pending_tasks.copy()
            self._pending_tasks = []
            for task_uuid4 in self._running_tasks:
                task, args, kargs = self._task_data[task_uuid4]
                self._worker.add_task(task_uuid4, task, *args, **kargs)
            self._thread.start()


class LIFOTaskManager(TaskManagerBase):
    """
    A last-in, first out (LIFO) task manager manager, where there's always
    at most one task in the queue, and if a new task is added, it overrides
    or replaces the existing task.
    """

    def _add_task(self, task: Callable, callback, *args, **kargs):
        """
        Override method so that the tasks are managed as a LIFO
        stack (Last-in, First out) instead of FIFO (First-In, First-Out).
        """
        for task_uuid4 in self._pending_tasks:
            self._cleanup_task(task_uuid4)
        self._queued_tasks = []
        self._pending_tasks = []
        super()._add_task(task, callback, *args, **kargs)
