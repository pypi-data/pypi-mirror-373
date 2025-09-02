from abc import abstractmethod
from asyncio import CancelledError
from dataclasses import dataclass
from datetime import timedelta
from random import SystemRandom

from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import models
from django.db import transaction
from django.db.models import F
from django.db.models import Q

from ..timezones import utcnow
from . import logger
from .engine import AbstractConsumer
from .engine import AbstractProducer
from .job import Job


def get_random_float(system_random=SystemRandom()):  # noqa: B008
    return system_random.random()


class QueueState(models.IntegerChoices):
    __empty__ = "NOT QUEUED"

    PENDING = 1, "PENDING"
    SCHEDULED = 2, "SCHEDULED"
    COMPLETED = 3, "COMPLETED"
    ERRORED = 4, "ERRORED"
    CANCELED = 5, "CANCELED"


class ResultType(models.IntegerChoices):
    __empty__ = "UNSET"

    PENDING = 6, "PENDING"
    SUCCESS = 7, "SUCCESS"
    ABSENT = 8, "ABSENT"
    ERROR = 9, "ERROR"


class TaskQuerySet(models.QuerySet):
    @transaction.atomic
    def upsert(self, key, /, **fields):
        now = utcnow()
        if "request_count" in fields:
            fields.setdefault("request_updated_at", now)
        if "queue_state" in fields:
            fields.setdefault("queue_updated_at", now)
        if "result_type" in fields:
            fields.setdefault("result_updated_at", now)
        task, _ = self.update_or_create(**key, defaults=fields)
        return task

    @transaction.atomic
    def inc_request_count(self, key, **kwargs):
        task: AbstractTask
        task, _ = self.select_for_update().get_or_create(**key)
        self.select_for_update().filter(id=task.id).update(request_count=F("request_count") + 1, request_updated_at=utcnow(), **kwargs)
        task.refresh_from_db()
        return task

    @transaction.atomic
    def get_first_and_mark_scheduled(self, **kwargs):
        task: AbstractTask = (
            self.filter(queue_state=QueueState.PENDING).order_by("queue_priority").select_for_update(skip_locked=True).first()
        )
        if task:
            logger.info("Marking as scheduled: %s", task)
            now = utcnow()
            task.queue_state = QueueState.SCHEDULED
            task.queue_updated_at = now
            for field, value in kwargs.items():
                setattr(task, field, value)
            task.save(
                update_fields=[
                    "queue_state",
                    "queue_updated_at",
                    *kwargs,
                ]
            )
        return task


class AbstractTask(models.Model):
    class Meta:
        abstract = True
        verbose_name = "worker task"
        verbose_name_plural = "worker tasks"
        indexes = [
            models.Index(
                fields=["queue_priority"],
                condition=Q(queue_state=QueueState.PENDING),
                name="%(app_label)s_%(class)s_queue",
            ),
            models.Index(
                fields=["result_updated_at", "queue_updated_at", "request_updated_at", "id"],
                name="%(app_label)s_%(class)s_admin",
            ),
            models.Index(
                F("result_updated_at").desc(nulls_last=True),
                F("queue_updated_at").desc(nulls_last=True),
                F("request_updated_at").desc(nulls_last=True),
                F("id"),
                name="%(app_label)s_%(class)s_sort",
            ),
        ]

    objects = TaskQuerySet.as_manager()

    request_count = models.PositiveIntegerField(default=0)
    request_updated_at = models.DateTimeField(null=True, blank=True)
    queue_priority = models.FloatField(default=get_random_float)
    queue_state = models.PositiveSmallIntegerField(choices=QueueState.choices, null=True, blank=True)
    queue_updated_at = models.DateTimeField(null=True, blank=True)
    result_details = models.TextField(null=True, blank=True)
    result_type = models.PositiveSmallIntegerField(choices=ResultType.choices, null=True, blank=True)
    result_updated_at = models.DateTimeField(null=True, blank=True)

    @property
    @abstractmethod
    def result_provider(self) -> models.Field:
        pass

    @property
    def job_kwargs(self):
        raise NotImplementedError

    def is_fresh(self):
        now = utcnow()
        if self.result_updated_at and self.result_updated_at > now - timedelta(seconds=settings.WORKER_TASK_REFRESH_SECONDS):
            return True

    async def done_watchdog(self, job: Job):
        try:
            result = await job.done
        except Exception as exc:
            logger.exception("%s.done_watchdog(%s) .done failed: %r", self, job, exc)
            self.queue_state = QueueState.ERRORED
        except CancelledError:
            logger.info("%s.done_watchdog(%s) .done got canceled.", self, job)
            self.queue_state = QueueState.CANCELED
        else:
            logger.info("%s.done_watchdog(%s) .done got completed with result: %s", self, job, result)
            self.queue_state = QueueState.COMPLETED
        self.queue_updated_at = utcnow()
        await self.asave(update_fields=["queue_state", "updated_at"])


@dataclass(repr=False)
class ModelProducer(AbstractProducer):
    @property
    @abstractmethod
    def task_model(self) -> type[AbstractTask]:
        pass

    async def fetch_task(self):
        return await sync_to_async(self.task_model.objects.get_first_and_mark_scheduled, thread_sensitive=False)()


@dataclass(repr=False)
class ModelConsumer(AbstractConsumer):
    @property
    @abstractmethod
    def task_model(self) -> type[AbstractTask]:
        pass

    async def save_result(self, job: Job, /, **kwargs):
        logger.info("%s.save_result(%s, **%s)", self, job, kwargs)
        return await sync_to_async(self.task_model.objects.upsert)(job.task_natural_key, **kwargs)
