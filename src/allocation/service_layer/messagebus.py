import logging
from typing import TYPE_CHECKING, Callable, Type

from tenacity import RetryError, Retrying, stop_after_attempt, wait_exponential

from src.allocation.domain import commands, events

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from src.allocation.service_layer import unit_of_work

Message = commands.Command | events.Event


class MessageBus:
    def __init__(
        self,
        uow: "unit_of_work.AbstractUnitOfWork",
        event_handlers: dict[Type[events.Event], list[Callable]],
        command_handlers: dict[Type[commands.Command], Callable],
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    def handle(self, message: Message):
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, events.Event):
                self.handle_event(message)
            elif isinstance(message, commands.Command):
                self.handle_command(message)
            else:
                raise Exception(f"{message} was not an Event or Command")

    def handle_event(
        self,
        event: events.Event,
    ):
        for handler in self.event_handlers[type(event)]:
            try:
                for attempt in Retrying(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(),
                ):
                    with attempt:
                        logger.debug(
                            "handling event %s with handler %s",
                            event,
                            handler,
                        )
                        handler(event)
                        self.queue.extend(self.uow.collect_new_events())
            except RetryError as retry_failure:
                logger.error(
                    "Не получилось обработать событие %s раз, отказ!",
                    retry_failure.last_attempt.attempt_number,
                )
                continue

    def handle_command(
        self,
        command: commands.Command,
    ):
        logger.debug("handling command %s", command)
        try:
            handler = self.command_handlers[type(command)]
            handler(command)
            self.queue.extend(self.uow.collect_new_events())
        except Exception:
            logger.exception("Error handling command %s", command)
            raise
