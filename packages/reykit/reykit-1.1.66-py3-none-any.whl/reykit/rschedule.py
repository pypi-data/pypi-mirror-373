# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-01-09 21:44:48
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Schedule methods.
"""


from typing import Any, Literal
from collections.abc import Callable
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.job import Job

from .rbase import Base


__all__ = (
    'Schedule',
)


class Schedule(Base):
    """
    Schedule type.
    """


    def __init__(
        self,
        max_workers: int = 10,
        max_instances: int = 1,
        coalesce: bool = True,
        block: bool = False
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        max_workers : Maximum number of synchronized executions.
        max_instances : Maximum number of synchronized executions of tasks with the same ID.
        coalesce : Whether to coalesce tasks with the same ID.
        block : Whether to block.
        """

        # Set parameter.
        executor = ThreadPoolExecutor(max_workers)
        executors = {'default': executor}
        job_defaults = {
            'coalesce': coalesce,
            'max_instances': max_instances
        }

        # Instance.
        if block:
            scheduler = BlockingScheduler(
                executors=executors,
                job_defaults=job_defaults
            )
        else:
            scheduler = BackgroundScheduler(
                executors=executors,
                job_defaults=job_defaults
            )

        # Set attribute.
        self.scheduler = scheduler


    def start(self) -> None:
        """
        Start scheduler.
        """

        # Start.
        self.scheduler.start()


    def pause(self) -> None:
        """
        Pause scheduler.

        Parameters
        ----------
        task : Task instance.
        """

        # Pause.
        self.scheduler.pause()


    def resume(self) -> None:
        """
        Resume scheduler.

        Parameters
        ----------
        task : Task instance.
        """

        # Resume.
        self.scheduler.resume()


    def tasks(self) -> list[Job]:
        """
        Return to task list.

        Returns
        -------
        Task list.
        """

        # Get.
        jobs = self.scheduler.get_jobs()

        return jobs


    def add_task(
        self,
        task: Callable,
        trigger: Literal['date', 'interval', 'cron'] = 'date',
        args: tuple | None = None,
        kwargs: dict | None = None,
        **trigger_kwargs: Any
    ) -> Job:
        """
        Add task.

        Parameters
        ----------
        task : Task function.
        trigger : Trigger type.
        args : Task position arguments.
        kwargs : Task keyword arguments.
        trigger_kwargs : Trigger keyword arguments.

        Returns
        -------
        Task instance.
        """

        # Add.
        job = self.scheduler.add_job(
            task,
            trigger,
            args,
            kwargs,
            **trigger_kwargs
        )

        return job


    def modify_task(
        self,
        task: Job | str,
        trigger: Literal['date', 'interval', 'cron'] | None = None,
        args: tuple | None = None,
        kwargs: dict | None = None,
        **trigger_kwargs: Any
    ) -> None:
        """
        Modify task.

        Parameters
        ----------
        task : Task instance or ID.
        trigger : Trigger type.
        args : Task position arguments.
        kwargs : Task keyword arguments.
        trigger_kwargs : Trigger keyword arguments.
        """

        # Arguments.
        params_arg = {}
        if args is not None:
            params_arg['args'] = args
        if kwargs is not None:
            params_arg['kwargs'] = kwargs

        ## Modify.
        if params_arg != {}:
            self.scheduler.modify_job(
                task.id,
                **params_arg
            )

        # Trigger.
        if (
            trigger is not None
            or trigger_kwargs != {}
        ):
            self.scheduler.reschedule_job(
                task.id,
                trigger=trigger,
                **trigger_kwargs
            )


    def remove_task(
        self,
        task: Job | str
    ) -> None:
        """
        Remove task.

        Parameters
        ----------
        task : Task instance or ID.
        """

        # Handle parameter.
        if type(task) == Job:
            id_ = task.id
        else:
            id_ = task

        # Remove.
        self.scheduler.remove_job(id_)


    def pause_task(
        self,
        task: Job | str   
    ) -> None:
        """
        Pause task.

        Parameters
        ----------
        task : Task instance or ID.
        """

        # Handle parameter.
        if type(task) == Job:
            id_ = task.id
        else:
            id_ = task

        # Pause.
        self.scheduler.pause_job(id_)


    def resume_task(
        self,
        task: Job | str
    ) -> None:
        """
        Resume task.

        Parameters
        ----------
        task : Task instance or ID.
        """

        # Handle parameter.
        if type(task) == Job:
            id_ = task.id
        else:
            id_ = task

        # Resume.
        self.scheduler.resume_job(id_)


    __iter__ = tasks
