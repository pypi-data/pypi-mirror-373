# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-01-09 21:44:48
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Schedule methods.
"""


from typing import Any, Literal, TypedDict, NotRequired
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
        self.database = database
 
        ## Database path name.
        self.db_names = {
            'base': 'base',
            'base.schedule': 'schedule',
            'base.schedule_stats': 'schedule_stats'
        }


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
        plan: dict[str, Any],
        *args: Any,
        **kwargs: Any
    ) -> Job:
        """
        Add task.

        Parameters
        ----------
        task : Task function.
        plan : Plan trigger keyword arguments.
        args : Task position arguments.
        kwargs : Task keyword arguments.

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
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Modify task.

        Parameters
        ----------
        task : Task instance or ID.
        plan : Plan trigger keyword arguments.
        args : Task position arguments.
        kwargs : Task keyword arguments.
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

        # Modify trigger.
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
                task.id,
                args=args,
                kwargs=kwargs
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
                'name': self.db_names['worm']
            }
        ]

        ## Table.
        tables = [

            ### 'douban_media'.
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
                        'constraint': 'NOT NULL',
                        'comment': 'Douban media ID.'
                    },
                    {
                        'name': 'imdb',
                        'type': 'char(10)',
                        'comment': 'IMDb ID.'
                    },
                    {
                        'name': 'type',
                        'type': 'varchar(5)',
                        'constraint': 'NOT NULL',
                        'comment': 'Media type.'
                    },
                    {
                        'name': 'name',
                        'type': 'varchar(50)',
                        'constraint': 'NOT NULL',
                        'comment': 'Media name.'
                    },
                    {
                        'name': 'year',
                        'type': 'year',
                        'constraint': 'NOT NULL',
                        'comment': 'Release year.'
                    },
                    {
                        'name': 'desc',
                        'type': 'varchar(1000)',
                        'comment': 'Media content description.'
                    },
                    {
                        'name': 'score',
                        'type': 'float',
                        'comment': 'Media score, [0,10].'
                    },
                    {
                        'name': 'score_count',
                        'type': 'int',
                        'comment': 'Media score count.'
                    },
                    {
                        'name': 'minute',
                        'type': 'smallint',
                        'comment': 'Movie or TV drama episode minute.'
                    },
                    {
                        'name': 'episode',
                        'type': 'smallint',
                        'comment': 'TV drama total episode number.'
                    },
                    {
                        'name': 'episode_now',
                        'type': 'smallint',
                        'comment': 'TV drama current episode number.'
                    },
                    {
                        'name': 'premiere',
                        'type': 'json',
                        'comment': 'Premiere region and date dictionary.'
                    },
                    {
                        'name': 'country',
                        'type': 'json',
                        'comment': 'Release country list.'
                    },
                    {
                        'name': 'class',
                        'type': 'json',
                        'comment': 'Class list.'
                    },
                    {
                        'name': 'director',
                        'type': 'json',
                        'comment': 'Director list.'
                    },
                    {
                        'name': 'star',
                        'type': 'json',
                        'comment': 'Star list.'
                    },
                    {
                        'name': 'scriptwriter',
                        'type': 'json',
                        'comment': 'Scriptwriter list.'
                    },
                    {
                        'name': 'language',
                        'type': 'json',
                        'comment': 'Language list.'
                    },
                    {
                        'name': 'alias',
                        'type': 'json',
                        'comment': 'Alias list.'
                    },
                    {
                        'name': 'comment',
                        'type': 'json',
                        'comment': 'Comment list.'
                    },
                    {
                        'name': 'image',
                        'type': 'varchar(150)',
                        'constraint': 'NOT NULL',
                        'comment': 'Picture image URL.'
                    },
                    {
                        'name': 'image_low',
                        'type': 'varchar(150)',
                        'constraint': 'NOT NULL',
                        'comment': 'Picture image low resolution URL.'
                    },
                    {
                        'name': 'video',
                        'type': 'varchar(150)',
                        'comment': 'Preview video Douban page URL.'
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
                        'name': 'u_imdb',
                        'fields': 'imdb',
                        'type': 'unique',
                        'comment': 'IMDb number unique index.'
                    },
                    {
                        'name': 'n_name',
                        'fields': 'name',
                        'type': 'noraml',
                        'comment': 'Media name normal index.'
                    }
                ],
                'comment': 'Douban media information table.'
            }

        ]

        ## View stats.
        views_stats = [

            ### 'schedule_stats'.
            {
                'path': (self.db_names['base'], self.db_names['base.schedule_stats']),
                'items': [
                    {
                        'name': 'count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`'
                        ),
                        'comment': 'Media count.'
                    },
                    {
                        'name': 'past_day_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`\n'
                            'WHERE TIMESTAMPDIFF(DAY, `create_time`, NOW()) = 0'
                        ),
                        'comment': 'Media count in the past day.'
                    },
                    {
                        'name': 'past_week_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`\n'
                            'WHERE TIMESTAMPDIFF(DAY, `create_time`, NOW()) <= 6'
                        ),
                        'comment': 'Media count in the past week.'
                    },
                    {
                        'name': 'past_month_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`\n'
                            'WHERE TIMESTAMPDIFF(DAY, `create_time`, NOW()) <= 29'
                        ),
                        'comment': 'Media count in the past month.'
                    },
                    {
                        'name': 'avg_score',
                        'select': (
                            'SELECT ROUND(AVG(`score`), 1)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`'
                        ),
                        'comment': 'Media average score.'
                    },
                    {
                        'name': 'score_count',
                        'select': (
                            'SELECT FORMAT(SUM(`score_count`), 0)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`'
                        ),
                        'comment': 'Media score count.'
                    },
                    {
                        'name': 'last_create_time',
                        'select': (
                            'SELECT MAX(`create_time`)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`'
                        ),
                        'comment': 'Media last record create time.'
                    },
                    {
                        'name': 'last_update_time',
                        'select': (
                            'SELECT IFNULL(MAX(`update_time`), MAX(`create_time`))\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`'
                        ),
                        'comment': 'Media last record update time.'
                    }
                ]

            }

        ]

        # Build.
        self.database.build.build(databases, tables, views_stats=views_stats)


    __iter__ = tasks
