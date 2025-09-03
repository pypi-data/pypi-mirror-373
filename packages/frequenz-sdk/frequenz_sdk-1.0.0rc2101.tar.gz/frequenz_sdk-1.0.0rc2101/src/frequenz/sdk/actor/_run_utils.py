# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Utility functions to run and synchronize the execution of actors."""


import asyncio
import logging

from ._actor import Actor

_logger = logging.getLogger(__name__)


async def run(*actors: Actor) -> None:
    """Await the completion of all actors.

    !!! info

        Please read the [`actor` module documentation][frequenz.sdk.actor] for more
        comprehensive guide on how to use and implement actors properly.

    Args:
        *actors: the actors to be awaited.
    """
    _logger.info("Starting %s actor(s)...", len(actors))

    for actor in actors:
        if actor.is_running:
            _logger.info("Actor %s: Already running, skipping start.", actor)
        else:
            _logger.info("Actor %s: Starting...", actor)
            actor.start()

    # Wait until all actors are done
    pending_tasks = {asyncio.create_task(a.wait(), name=str(a)) for a in actors}
    while pending_tasks:
        done_tasks, pending_tasks = await asyncio.wait(
            pending_tasks, return_when=asyncio.FIRST_COMPLETED
        )
        # This should always be only one task, but we handle many for extra safety
        for task in done_tasks:
            # BackgroundService returns a BaseExceptionGroup containing multiple
            # exceptions. The 'task.result()' statement raises these exceptions,
            # and 'except*' is used to handle them as a group. If the task raises
            # multiple different exceptions, 'except*' will be invoked multiple times,
            # once for each exception group.
            try:
                task.result()
            except* asyncio.CancelledError:
                _logger.info("Actor %s: Cancelled while running.", task.get_name())
            except* Exception:  # pylint: disable=broad-exception-caught
                _logger.exception(
                    "Actor %s: Raised an exception while running.",
                    task.get_name(),
                )
            else:
                _logger.info("Actor %s: Finished normally.", task.get_name())

    _logger.info("All %s actor(s) finished.", len(actors))
