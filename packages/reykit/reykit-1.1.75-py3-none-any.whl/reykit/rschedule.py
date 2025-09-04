# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-01-09 21:44:48
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Schedule methods.
"""


from typing import Any, Literal, TypedDict, NotRequired
from functools import wraps as functools_wraps
from collections.abc import Callable
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.job import Job
from reydb.rdb import Database

from .rbase import Base, throw


__all__ = (
    'Schedule',
)


class Schedule(Base):
    """
    Schedule type.
    Can create database used `self.build_db` method.
    """


    def __init__(
        self,
        max_workers: int = 10,
        max_instances: int = 1,
        coalesce: bool = True,
        block: bool = False,
        database: Database | None = None
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        max_workers : Maximum number of synchronized executions.
        max_instances : Maximum number of synchronized executions of tasks with the same ID.
        coalesce : Whether to coalesce tasks with the same ID.
        block : Whether to block.
        database : `Database` instance.
            - `None`: Not use database.
            - `Database`: Automatic record to database.
        """

        # Build.

        ## Scheduler.
        executor = ThreadPoolExecutor(max_workers)
        executors = {'default': executor}
        job_defaults = {
            'coalesce': coalesce,
            'max_instances': max_instances
        }
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
        self.scheduler = scheduler

        ### Start.
        self.scheduler.start()

        ## Database.
        self.database = database

        ### Database path name.
        self.db_names = {
            'base': 'base',
            'base.schedule': 'schedule',
            'base.stats_schedule': 'stats_schedule'
        }


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


    def wrap_record_db(
        self,
        task: Callable,
        note: str | None
    ) -> None:
        """
        Decorator, record to database.

        Parameters
        ----------
        task : Task.
        note : Task note.
        """


        # Define.
        @functools_wraps(task)
        def _task(*args, **kwargs) -> None:
            """
            Decorated function.

            Parameters
            ----------
            args : Position arguments of function.
            kwargs : Keyword arguments of function.
            """

            # Handle parameter.
            nonlocal task, note

            # Status executing.
            data = {
                'status': 0,
                'task': task.__name__,
                'note': note
            }
            conn = self.database.connect()
            conn.execute_insert(
                (self.db_names['base'], self.db_names['base.schedule']),
                data
            )
            id_ = conn.variables['identity']
            conn.commit()

            # Try execute.

            ## Record error.
            task = self.database.error.wrap(task, note=note)

            try:
                task(*args, **kwargs)

            # Status occurred error.
            except BaseException:
                data = {
                    'id': id_,
                    'status': 2
                }
                self.database.execute_update(
                    (self.db_names['base'], self.db_names['base.schedule']),
                    data
                )
                raise

            # Status completed.
            else:
                data = {
                    'id': id_,
                    'status': 1
                }
                self.database.execute_update(
                    (self.db_names['base'], self.db_names['base.schedule']),
                    data
                )

        return _task


    def add_task(
        self,
        task: Callable,
        plan: dict[str, Any],
        args: Any | None = None,
        kwargs: Any | None = None,
        note: str | None = None
    ) -> Job:
        """
        Add task.

        Parameters
        ----------
        task : Task function.
        plan : Plan trigger keyword arguments.
        args : Task position arguments.
        kwargs : Task keyword arguments.
        note : Task note.

        Returns
        -------
        Task instance.
        """

        # Handle parameter.
        if plan is None:
            plan = {}
        trigger = plan.get('trigger')
        trigger_args = {
            key: value
            for key, value in plan.items()
            if key != 'trigger'
        }

        # Add.

        ## Database.
        if self.database is not None:
            task = self.wrap_record_db(task, note)

        job = self.scheduler.add_job(
            task,
            trigger,
            args,
            kwargs,
            **trigger_args
        )

        return job


    def modify_task(
        self,
        task: Job | str,
        plan: dict[str, Any],
        args: Any | None = None,
        kwargs: Any | None = None,
        note: str | None = None
    ) -> None:
        """
        Modify task.

        Parameters
        ----------
        task : Task instance or ID.
        plan : Plan trigger keyword arguments.
        args : Task position arguments.
        kwargs : Task keyword arguments.
        note : Task note.
        """

        # Handle parameter.
        if type(task) == Job:
            task = task.id
        if plan is None:
            plan = {}
        trigger = plan.get('trigger')
        trigger_args = {
            key: value
            for key, value in plan.items()
            if key != 'trigger'
        }

        # Modify plan.
        if plan != {}:
            self.scheduler.reschedule_job(
                task,
                trigger=trigger,
                **trigger_args
            )

        # Modify arguments.
        if (
            args != ()
            or kwargs != {}
        ):
            self.scheduler.modify_job(
                task,
                args=args,
                kwargs=kwargs
            )

        # Modify note.
        self.notes[task] = note


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


    def build_db(self) -> None:
        """
        Check and build all standard databases and tables, by `self.db_names`.
        """

        # Check.
        if self.database is None:
            throw(ValueError, self.database)

        # Set parameter.

        ## Database.
        databases = [
            {
                'name': self.db_names['base']
            }
        ]

        ## Table.
        tables = [

            ### 'schedule'.
            {
                'path': (self.db_names['base'], self.db_names['base.schedule']),
                'fields': [
                    {
                        'name': 'create_time',
                        'type': 'datetime',
                        'constraint': 'NOT NULL DEFAULT CURRENT_TIMESTAMP',
                        'comment': 'Record create time.'
                    },
                    {
                        'name': 'update_time',
                        'type': 'datetime',
                        'constraint': 'DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP',
                        'comment': 'Record update time.'
                    },
                    {
                        'name': 'id',
                        'type': 'int unsigned',
                        'constraint': 'NOT NULL AUTO_INCREMENT',
                        'comment': 'ID.'
                    },
                    {
                        'name': 'status',
                        'type': 'tinyint',
                        'constraint': 'NOT NULL',
                        'comment': 'Schedule status, 0 is executing, 1 is completed, 2 is occurred error.'
                    },
                    {
                        'name': 'task',
                        'type': 'varchar(100)',
                        'constraint': 'NOT NULL',
                        'comment': 'Schedule task function name.'
                    },
                    {
                        'name': 'note',
                        'type': 'varchar(500)',
                        'comment': 'Schedule note.'
                    }
                ],
                'primary': 'id',
                'indexes': [
                    {
                        'name': 'n_create_time',
                        'fields': 'create_time',
                        'type': 'noraml',
                        'comment': 'Record create time normal index.'
                    },
                    {
                        'name': 'n_update_time',
                        'fields': 'update_time',
                        'type': 'noraml',
                        'comment': 'Record update time normal index.'
                    },
                    {
                        'name': 'n_task',
                        'fields': 'task',
                        'type': 'noraml',
                        'comment': 'Schedule task function name normal index.'
                    }
                ],
                'comment': 'Schedule execute record table.'
            }

        ]

        ## View stats.
        views_stats = [

            ### 'stats_schedule'.
            {
                'path': (self.db_names['base'], self.db_names['base.stats_schedule']),
                'items': [
                    {
                        'name': 'count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{self.db_names['base']}`.`{self.db_names['base.schedule']}`'
                        ),
                        'comment': 'Schedule count.'
                    },
                    {
                        'name': 'past_day_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{self.db_names['base']}`.`{self.db_names['base.schedule']}`\n'
                            'WHERE TIMESTAMPDIFF(DAY, `create_time`, NOW()) = 0'
                        ),
                        'comment': 'Schedule count in the past day.'
                    },
                    {
                        'name': 'past_week_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{self.db_names['base']}`.`{self.db_names['base.schedule']}`\n'
                            'WHERE TIMESTAMPDIFF(DAY, `create_time`, NOW()) <= 6'
                        ),
                        'comment': 'Schedule count in the past week.'
                    },
                    {
                        'name': 'past_month_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{self.db_names['base']}`.`{self.db_names['base.schedule']}`\n'
                            'WHERE TIMESTAMPDIFF(DAY, `create_time`, NOW()) <= 29'
                        ),
                        'comment': 'Schedule count in the past month.'
                    },
                    {
                        'name': 'task_count',
                        'select': (
                            'SELECT COUNT(DISTINCT `task`)\n'
                            f'FROM `{self.db_names['base']}`.`{self.db_names['base.schedule']}`'
                        ),
                        'comment': 'Task count.'
                    },
                    {
                        'name': 'last_time',
                        'select': (
                            'SELECT IFNULL(MAX(`update_time`), MAX(`create_time`))\n'
                            f'FROM `{self.db_names['base']}`.`{self.db_names['base.schedule']}`'
                        ),
                        'comment': 'Schedule last record time.'
                    }
                ]

            }

        ]

        # Build.
        self.database.build.build(databases, tables, views_stats=views_stats)

        ## Error.
        self.database.error.build_db()


    __iter__ = tasks
