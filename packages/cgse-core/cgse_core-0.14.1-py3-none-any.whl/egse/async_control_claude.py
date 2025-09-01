"""
This module defines the abstract class for any Control Server and some convenience functions.
"""

import abc
import asyncio
import datetime
import logging
import pickle
import textwrap
from functools import partial
from typing import Callable
from typing import Coroutine
from typing import Type
from typing import Union

import zmq
import zmq.asyncio

from egse.decorators import retry
from egse.decorators import retry_with_exponential_backoff
from egse.listener import EVENT_ID
from egse.listener import Event
from egse.listener import Listeners
from egse.system import SignalCatcher

try:
    # This function is only available when the cgse-core package is installed
    from egse.logger import close_all_zmq_handlers
except ImportError:

    def close_all_zmq_handlers():  # noqa
        pass


from egse.process import ProcessStatus
from egse.settings import Settings
from egse.system import get_average_execution_time
from egse.system import get_average_execution_times
from egse.system import get_full_classname
from egse.system import get_host_ip
from egse.system import save_average_execution_time

_LOGGER = logging.getLogger(__name__)

PROCESS_SETTINGS = Settings.load("PROCESS")


async def is_control_server_active(endpoint: str = None, timeout: float = 0.5) -> bool:
    """Checks if the Control Server is running.

    This function sends a *Ping* message to the Control Server and expects a *Pong* answer back within the timeout
    period.

    Args:
        endpoint (str): Endpoint to connect to, i.e. <protocol>://<address>:<port>
        timeout (float): Timeout when waiting for a reply [s, default=0.5]

    Returns: True if the Control Server is running and replied with the expected answer; False otherwise.
    """

    if endpoint is None:
        raise ValueError(
            "endpoint argument not provided, please provide a string with this format: '<protocol>://<address>:<port>'"
        )

    ctx = zmq.asyncio.Context.instance()

    return_code = False

    try:
        socket = ctx.socket(zmq.REQ)
        socket.connect(endpoint)
        data = pickle.dumps("Ping")
        await socket.send(data)

        # Use asyncio.wait_for instead of zmq.select
        try:
            data = await asyncio.wait_for(socket.recv(), timeout=timeout)
            response = pickle.loads(data)
            return_code = response == "Pong"
        except asyncio.TimeoutError:
            pass

        socket.close(linger=0)
    except Exception as exc:
        _LOGGER.warning(f"Caught an exception while pinging a control server at {endpoint}: {exc}.")

    return return_code


# Synchronous version for backward compatibility
def is_control_server_active_sync(endpoint: str = None, timeout: float = 0.5) -> bool:
    """Synchronous version of is_control_server_active for backward compatibility.

    This function runs the async version in a new event loop.
    """
    if endpoint is None:
        raise ValueError(
            "endpoint argument not provided, please provide a string with this format: '<protocol>://<address>:<port>'"
        )

    # Create a new event loop for this function call
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(is_control_server_active(endpoint, timeout))
    finally:
        loop.close()


# Helper function to periodically run a coroutine
async def do_every_async(interval: float, coroutine: Callable[[], Coroutine]) -> None:
    """Run a coroutine every interval seconds"""
    while True:
        await coroutine()
        await asyncio.sleep(interval)


class ControlServer(abc.ABC):
    """Base class for all device control servers and for the Storage Manager and Configuration Manager.

    A Control Server reads commands from a ZeroMQ socket and executes these commands by calling the `execute()` method
    of the commanding protocol class.

    The subclass shall define the following:

    - Define the device protocol class -> `self.device_protocol`
    - Bind the command socket to the device protocol -> `self.dev_ctrl_cmd_sock`
    - Register the command socket in the poll set -> `self.poller`

    """

    def __init__(self):
        """Initialisation of a new Control Server."""

        from egse.monitoring import MonitoringProtocol
        from egse.services import ServiceProtocol

        self._process_status = ProcessStatus()
        self._metrics_task = None  # Will be created in serve()

        # The logger will be overwritten by the subclass, if not, we use this logger with the name of the subclass.
        # That will help us to identify which subclass did not overwrite the logger attribute.

        self.logger = logging.getLogger(get_full_classname(self))

        self.listeners = Listeners()
        self.scheduled_tasks = []

        # Queue for sequential operations that must preserve ordering
        self.sequential_queue = asyncio.Queue()

        self.interrupted = False
        self.mon_delay = 1000  # Delay between publish status information [ms]
        self.hk_delay = 1000  # Delay between saving housekeeping information [ms]
        self.scheduled_task_delay = 10  # delay time between successive executions of scheduled tasks [seconds]

        self.zcontext = zmq.asyncio.Context.instance()

        # No need for explicit poller in asyncio version
        # Instead, we'll use asyncio.gather with tasks for each socket

        self.device_protocol = None  # This will be set in the subclass
        self.service_protocol = ServiceProtocol(self)
        self.monitoring_protocol = MonitoringProtocol(self)

        # Set up the Control Server waiting for service requests
        self.dev_ctrl_service_sock = self.zcontext.socket(zmq.REP)
        self.service_protocol.bind(self.dev_ctrl_service_sock)

        # Set up the Control Server for sending monitoring info
        self.dev_ctrl_mon_sock = self.zcontext.socket(zmq.PUB)
        self.monitoring_protocol.bind(self.dev_ctrl_mon_sock)

        # Set up the Control Server waiting for device commands.
        # The device protocol shall bind the socket in the subclass
        self.dev_ctrl_cmd_sock = self.zcontext.socket(zmq.REP)

        # Tasks will be created in serve()
        self.tasks = []
        self.event_loop = None

    @abc.abstractmethod
    def get_communication_protocol(self) -> str:
        """Returns the communication protocol used by the Control Server.

        Returns:
            Communication protocol used by the Control Server, as specified in the settings.
        """

        pass

    @abc.abstractmethod
    def get_commanding_port(self) -> int:
        """Returns the commanding port used by the Control Server.

        Returns:
            Commanding port used by the Control Server, as specified in the settings.
        """

        pass

    @abc.abstractmethod
    def get_service_port(self) -> int:
        """Returns the service port used by the Control Server.

        Returns:
            Service port used by the Control Server, as specified in the settings.
        """

        pass

    @abc.abstractmethod
    def get_monitoring_port(self) -> int:
        """Returns the monitoring port used by the Control Server.

        Returns:
            Monitoring port used by the Control Server, as specified in the settings.
        """

        pass

    @staticmethod
    def get_ip_address() -> str:
        """Returns the IP address of the current host."""
        return get_host_ip()

    def get_storage_mnemonic(self) -> str:
        """Returns the storage mnemonics used by the Control Server.

        This is a string that will appear in the filename with the housekeeping information of the device, as a way of
        identifying the device.  If this is not implemented in the subclass, then the class name will be used.

        Returns:
            Storage mnemonics used by the Control Server, as specified in the settings.
        """

        return self.__class__.__name__

    def get_process_status(self) -> dict:
        """Returns the process status of the Control Server.

        Returns:
            Dictionary with the process status of the Control Server.
        """

        return self._process_status.as_dict()

    def get_average_execution_times(self) -> dict:
        """Returns the average execution times of all functions that have been monitored by this process.

        Returns:
            Dictionary with the average execution times of all functions that have been monitored by this process.
                The dictionary keys are the function names, and the values are the average execution times in ms.
        """

        return get_average_execution_times()

    def set_mon_delay(self, seconds: float) -> float:
        """Sets the delay time for monitoring.

        The delay time is the time between two successive executions of the `get_status()` function of the device
        protocol.

        It might happen that the delay time that is set is longer than what you requested. That is the case when the
        execution of the `get_status()` function takes longer than the requested delay time. That should prevent the
        server from blocking when a too short delay time is requested.

        Args:
            seconds (float): Number of seconds between the monitoring calls

        Returns:
            Delay that was set [ms].
        """

        execution_time = get_average_execution_time(self.device_protocol.get_status)
        self.mon_delay = max(seconds * 1000, (execution_time + 0.2) * 1000)

        return self.mon_delay

    def set_hk_delay(self, seconds: float) -> float:
        """Sets the delay time for housekeeping.

        The delay time is the time between two successive executions of the `get_housekeeping()` function of the device
        protocol.

        It might happen that the delay time that is set is longer than what you requested. That is the case when the
        execution of the `get_housekeeping()` function takes longer than the requested delay time. That should prevent
        the server from blocking when a too short delay time is requested.

        Args:
            seconds (float): Number of seconds between the housekeeping calls

        Returns:
            Delay that was set [ms].
        """

        execution_time = get_average_execution_time(self.device_protocol.get_housekeeping)
        self.hk_delay = max(seconds * 1000, (execution_time + 0.2) * 1000)

        return self.hk_delay

    def set_scheduled_task_delay(self, seconds: float):
        """
        Sets the delay time between successive executions of scheduled tasks.

        Args:
            seconds: the time interval between two successive executions [seconds]

        """
        self.scheduled_task_delay = seconds

    def set_logging_level(self, level: Union[int, str]) -> None:
        """Sets the logging level to the given level.

        Allowed logging levels are:

        - "CRITICAL" or "FATAL" or 50
        - "ERROR" or 40
        - "WARNING" or "WARN" or 30
        - "INFO" or 20
        - "DEBUG" or 10
        - "NOTSET" or 0

        Args:
            level (int | str): Logging level to use, specified as either a string or an integer
        """

        self.logger.setLevel(level=level)

    def quit(self) -> None:
        """Interrupts the Control Server."""

        self.interrupted = True
        if self.event_loop:
            for task in self.tasks:
                if not task.done():
                    task.cancel()

    async def before_serve(self) -> None:
        """
        This method needs to be overridden by the subclass if certain actions need to be executed before the control
        server is activated.
        """

        pass

    async def after_serve(self) -> None:
        """
        This method needs to be overridden by the subclass if certain actions need to be executed after the control
        server has been deactivated.
        """

        pass

    async def is_storage_manager_active(self) -> bool:
        """Checks if the Storage Manager is active.

        This method has to be implemented by the subclass if you need to store information.

        Note: You might want to set a specific timeout when checking for the Storage Manager.

        Note: If this method returns True, the following methods shall also be implemented by the subclass:

        - register_to_storage_manager()
        - unregister_from_storage_manager()
        - store_housekeeping_information()

        Returns:
            True if the Storage Manager is active; False otherwise.
        """

        return False

    async def handle_scheduled_tasks(self):
        """
        Executes or reschedules tasks in the `serve()` event loop.
        """
        self.scheduled_tasks.reverse()
        rescheduled_tasks = []
        while self.scheduled_tasks:
            task_info = self.scheduled_tasks.pop()
            task = task_info["task"]
            task_name = task_info.get("name")

            at = task_info.get("after")
            if at and at > datetime.datetime.now(tz=datetime.timezone.utc):
                rescheduled_tasks.append(task_info)
                continue

            condition = task_info.get("when")
            if condition and not condition():
                self.logger.debug(
                    f"Task {task_name} rescheduled in {self.scheduled_task_delay}s, condition not met...."
                )
                self.logger.info(f"Task {task_name} rescheduled in {self.scheduled_task_delay}s")
                current_time = datetime.datetime.now(tz=datetime.timezone.utc)
                scheduled_time = current_time + datetime.timedelta(seconds=self.scheduled_task_delay)
                task_info["after"] = scheduled_time
                rescheduled_tasks.append(task_info)
                continue

            self.logger.debug(f"Running scheduled task: {task_name}")
            try:
                # Handle both regular functions and coroutines
                if asyncio.iscoroutinefunction(task):
                    await task()
                else:
                    task()
            except Exception as exc:
                self.logger.error(f"Task {task_name} has failed: {exc!r}")
                self.logger.info(f"Task {task_name} rescheduled in {self.scheduled_task_delay}s")
                current_time = datetime.datetime.now(tz=datetime.timezone.utc)
                scheduled_time = current_time + datetime.timedelta(seconds=self.scheduled_task_delay)
                task_info["after"] = scheduled_time
                rescheduled_tasks.append(task_info)
            else:
                self.logger.debug(f"Scheduled task finished: {task_name}")

        if self.scheduled_tasks:
            self.logger.warning(f"There are still {len(self.scheduled_tasks)} scheduled tasks.")

        if rescheduled_tasks:
            self.scheduled_tasks.extend(rescheduled_tasks)

    def schedule_task(self, callback: Union[Callable, Coroutine], after: float = 0.0, when: Callable = None):
        """
        Schedules a task to run in the control server event loop.

        The `callback` function will be executed as soon as possible in the `serve()` event loop.

        Some simple scheduling options are available:

        * after: the task will only execute 'x' seconds after the time of scheduling. I.e.
          the task will be rescheduled until time > scheduled time + 'x' seconds.
        * when: the task will only execute when the condition is True.

        The `after` and the `when` arguments can be combined.

        Note:
            * This function is intended to be used in order to prevent a deadlock.
            * Since the `callback` function is executed in the `serve()` event loop, it shall not block!

        """
        try:
            name = callback.func.__name__ if isinstance(callback, partial) else callback.__name__
        except AttributeError:
            name = "unknown"

        current_time = datetime.datetime.now(tz=datetime.timezone.utc)
        scheduled_time = current_time + datetime.timedelta(seconds=after)

        self.logger.info(f"Task {name} scheduled")

        self.scheduled_tasks.append({"task": callback, "name": name, "after": scheduled_time, "when": when})

    async def process_device_command(self):
        """Handle commands for the device protocol"""
        while not self.interrupted:
            try:
                # Check if there's a command pending with non-blocking recv
                try:
                    # Use poll with a short timeout to check for messages
                    events = await self.dev_ctrl_cmd_sock.poll(timeout=50, flags=zmq.POLLIN)
                    if events == zmq.POLLIN:
                        # If we have a command, we can either:
                        # 1. Process it directly (parallel to other operations)
                        # await self.device_protocol.execute_async()

                        # 2. Or enqueue it for sequential processing if order matters
                        self.enqueue_sequential_operation(self.device_protocol.execute_async)
                except Exception as exc:
                    self.logger.error(f"Error checking for device command: {exc}")
                    await asyncio.sleep(0.05)

                await asyncio.sleep(0.01)  # Short sleep to prevent CPU hogging
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.error(f"Error in device command processor: {exc}")

    async def process_service_command(self):
        """Handle commands for the service protocol"""
        while not self.interrupted:
            try:
                # Check if there's a command pending with non-blocking recv
                try:
                    # Use poll with a short timeout to check for messages
                    events = await self.dev_ctrl_service_sock.poll(timeout=50, flags=zmq.POLLIN)
                    if events == zmq.POLLIN:
                        # If we have a command, we can either:
                        # 1. Process it directly (parallel to other operations)
                        # await self.service_protocol.execute_async()

                        # 2. Or enqueue it for sequential processing if order matters
                        self.enqueue_sequential_operation(self.service_protocol.execute_async)
                except Exception as exc:
                    self.logger.error(f"Error checking for service command: {exc}")
                    await asyncio.sleep(0.05)

                await asyncio.sleep(0.01)  # Short sleep to prevent CPU hogging
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.error(f"Error in service command processor: {exc}")

    async def send_status_updates(self):
        """Send periodic status updates"""
        while not self.interrupted:
            try:
                # Convert milliseconds to seconds for asyncio.sleep
                await asyncio.sleep(self.mon_delay / 1000)

                # Create a coroutine for the status update
                async def status_update_operation():
                    try:
                        status = save_average_execution_time(self.device_protocol.get_status)
                        await self.monitoring_protocol.send_status_async(status)
                    except Exception as exc:
                        _LOGGER.error(
                            textwrap.dedent(
                                f"""\
                                An Exception occurred while collecting status info from the control server \
                                 {self.__class__.__name__}.
                                This might be a temporary problem, still needs to be looked into:

                                {exc}
                                """
                            )
                        )

                # You can choose to run status updates sequentially if they must be in order
                # with other operations from the polling loop
                self.enqueue_sequential_operation(status_update_operation)

                # Or run them independently if order doesn't matter:
                # await status_update_operation()

            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.error(f"Error sending status: {exc}")

    async def send_housekeeping_updates(self):
        """Send periodic housekeeping updates if storage manager is active"""
        storage_manager = await self.is_storage_manager_active()
        if not storage_manager:
            return

        while not self.interrupted:
            try:
                # Convert milliseconds to seconds for asyncio.sleep
                await asyncio.sleep(self.hk_delay / 1000)

                # Create a coroutine for the housekeeping update
                async def housekeeping_update_operation():
                    try:
                        housekeeping = save_average_execution_time(self.device_protocol.get_housekeeping)
                        await self.store_housekeeping_information(housekeeping)
                    except Exception as exc:
                        _LOGGER.error(
                            textwrap.dedent(
                                f"""\
                                An Exception occurred while collecting housekeeping from the device to be stored in \
                                 {self.get_storage_mnemonic()}.
                                This might be a temporary problem, still needs to be looked into:

                                {exc}
                                """
                            )
                        )

                # You can choose to run housekeeping updates sequentially if they must be in order
                # with other operations from the polling loop
                self.enqueue_sequential_operation(housekeeping_update_operation)

                # Or run them independently if order doesn't matter:
                # await housekeeping_update_operation()

            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.error(f"Error sending housekeeping: {exc}")

    async def process_scheduled_tasks(self):
        """Process scheduled tasks periodically"""
        while not self.interrupted:
            try:
                # Create a coroutine for handling scheduled tasks
                async def scheduled_tasks_operation():
                    await self.handle_scheduled_tasks()

                # You can choose to run scheduled tasks sequentially if they must
                # maintain order with other operations from the polling loop
                self.enqueue_sequential_operation(scheduled_tasks_operation)

                # Or run them independently if order doesn't matter:
                # await scheduled_tasks_operation()

                await asyncio.sleep(0.05)  # Small sleep to not hog CPU
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.error(f"Error processing scheduled tasks: {exc}")

    async def update_metrics(self):
        """Update process metrics periodically"""
        while not self.interrupted:
            try:
                self._process_status.update()
                await asyncio.sleep(PROCESS_SETTINGS.METRICS_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.error(f"Error updating metrics: {exc}")

    async def check_device_protocol_alive(self):
        """Check if device protocol is still alive"""
        while not self.interrupted:
            try:
                await asyncio.sleep(1.0)  # Check every second

                if not self.device_protocol.is_alive():
                    self.logger.error(
                        "Some Thread or sub-process that was started by Protocol has died, terminating..."
                    )
                    self.quit()
                    break
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.error(f"Error checking if device protocol is alive: {exc}")

    async def process_sequential_queue(self):
        """
        Process operations that need to be executed sequentially.
        This ensures that certain operations maintain the same order as in the original polling loop.
        """
        while not self.interrupted:
            try:
                # Get operation from queue with timeout to allow checking for interruption
                try:
                    operation = await asyncio.wait_for(self.sequential_queue.get(), 0.1)
                    await operation()
                    self.sequential_queue.task_done()
                except asyncio.TimeoutError:
                    continue
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.error(f"Error processing sequential operation: {exc}")

    def enqueue_sequential_operation(self, coroutine_func):
        """
        Add an operation to the sequential queue.
        This ensures the operation will run in order with other sequential operations.

        Args:
            coroutine_func: A coroutine function (async function) to be executed sequentially
        """
        if self.sequential_queue is not None:  # Check if server is initialized
            self.sequential_queue.put_nowait(coroutine_func)

    async def serve(self) -> None:
        """Activation of the Control Server.

        This comprises the following steps:

        - Executing the `before_serve` method;
        - Checking if the Storage Manager is active and registering the Control Server to it;
        - Start accepting (listening to) commands;
        - Start sending out monitoring information;
        - Start sending out housekeeping information;
        - Start listening for quit commands;
        - After a quit command has been received:
            - Unregister from the Storage Manager;
            - Execute the `after_serve` method;
            - Close all sockets;
            - Clean up all tasks.
        """
        # Store reference to event loop
        self.event_loop = asyncio.get_event_loop()

        # Execute before_serve hook
        await self.before_serve()

        # Check if Storage Manager is available
        storage_manager = await self.is_storage_manager_active()
        if storage_manager:
            await self.register_to_storage_manager()

        # Set up signal handler
        killer = SignalCatcher()

        # Create tasks for each aspect of the control server
        self.tasks = [
            asyncio.create_task(self.process_device_command()),
            asyncio.create_task(self.process_service_command()),
            asyncio.create_task(self.send_status_updates()),
            asyncio.create_task(self.process_scheduled_tasks()),
            asyncio.create_task(self.update_metrics()),
            asyncio.create_task(self.check_device_protocol_alive()),
            asyncio.create_task(self.process_sequential_queue()),  # Add sequential queue processor
        ]

        # Add housekeeping task if storage manager is active
        if storage_manager:
            self.tasks.append(asyncio.create_task(self.send_housekeeping_updates()))

        # Wait for interruption or signal
        try:
            while not self.interrupted and not killer.term_signal_received:
                await asyncio.sleep(0.1)

                if killer.term_signal_received:
                    self.logger.info(f"TERM Signal received, closing down the {self.__class__.__name__}.")
                    break

                if self.interrupted:
                    self.logger.info(f"Quit command received, closing down the {self.__class__.__name__}.")
                    break

        except asyncio.CancelledError:
            self.logger.info("Main server loop cancelled.")
        finally:
            # Cancel all running tasks
            for task in self.tasks:
                if not task.done():
                    task.cancel()

            # Wait for tasks to complete their cancellation
            if self.tasks:
                try:
                    await asyncio.gather(*self.tasks, return_exceptions=True)
                except asyncio.CancelledError:
                    pass

            # Cleanup
            if storage_manager:
                await self.unregister_from_storage_manager()

            await self.after_serve()

            await self.device_protocol.quit_async()

            self.dev_ctrl_mon_sock.close(linger=0)
            self.dev_ctrl_service_sock.close(linger=0)
            self.dev_ctrl_cmd_sock.close(linger=0)

            close_all_zmq_handlers()

            self.zcontext.term()

    async def store_housekeeping_information(self, data: dict) -> None:
        """Sends housekeeping information to the Storage Manager.

        This method has to be overwritten by the subclasses if they want the device housekeeping information to be
        saved.

        Args:
            data (dict): a dictionary containing parameter name and value of all device housekeeping. There is also
                a timestamp that represents the date/time when the HK was received from the device.
        """
        pass

    async def register_to_storage_manager(self) -> None:
        """Registers this Control Server to the Storage Manager.

        By doing so, the housekeeping information of the device will be sent to the Storage Manager, which will store
        the information in a dedicated CSV file.

        This method has to be overwritten by the subclasses if they have housekeeping information that must be stored.

        Subclasses need to overwrite this method if they have housekeeping information to be stored.

        The following information is required for the registration:

        - origin: Storage mnemonic, which can be retrieved from `self.get_storage_mnemonic()`
        - persistence_class: Persistence layer (one of the TYPES in egse.storage.persistence)
        - prep: depending on the type of the persistence class (see respective documentation)

        The `egse.storage` module provides a convenience method that can be called from the method in the subclass:

            >>> from egse.storage import register_to_storage_manager_async  # noqa

        Note:
            the `egse.storage` module might not be available, it is provided by the `cgse-core` package.
        """
        pass

    async def unregister_from_storage_manager(self) -> None:
        """Unregisters the Control Server from the Storage Manager.

        This method has to be overwritten by the subclasses.

        The following information is required for the registration:

        - origin: Storage mnemonic, which can be retrieved from `self.get_storage_mnemonic()`

        The `egse.storage` module provides a convenience method that can be called from the method in the subclass:

            >>> from egse.storage import unregister_from_storage_manager_async  # noqa

        Note:
            the `egse.storage` module might not be available, it is provided by the `cgse-core` package.
        """
        pass

    async def notify_listeners(self, event_id: int = 0, context: dict = None):
        """
        Notifies registered listeners about an event.

        This function creates an Event object with the provided `event_id` and `context`
        and notifies all registered listeners with the created event.

        Args:
            event_id (int, optional): The identifier for the event. Defaults to 0.
            context (dict, optional): Additional context information associated with the event.
                Defaults to None.

        Note:
            The notification is performed by the `notify_listeners` method of the `listeners` object
            associated with this instance.
            The notification is executed as a task to avoid blocking the commanding chain.
        """
        self.logger.info(f"Notifying listeners for {EVENT_ID(event_id).name}")

        # Create a task for notification instead of a daemon thread
        event = Event(event_id=event_id, context=context)
        asyncio.create_task(self.listeners.notify_listeners_async(event))

    def get_listener_names(self):
        return self.listeners.get_listener_names()

    async def register_as_listener(self, proxy: Type, listener: dict):
        """
        Registers a listener with the specified proxy.

        This function attempts to add the provided listener to the specified proxy.
        It employs a retry mechanism to handle potential ConnectionError exceptions.

        Args:
            proxy: A callable object representing the proxy to which the listener will be added.
            listener (dict): The listener to be registered. Should be a dictionary containing
                listener details.

        Raises:
            ConnectionError: If the connection to the proxy encounters issues even after
                multiple retry attempts.
        """

        @retry_with_exponential_backoff(exceptions=[ConnectionError])
        async def _add_listener(proxy, listener):
            async with proxy() as x, x.get_service_proxy() as srv:
                rc = await srv.add_listener_async(listener)
                _LOGGER.info(f"Response from {proxy.__name__} service add_listener: {rc}")

        _LOGGER.info(f"Registering {self.__class__.__name__} as a listener to {proxy.__name__}")
        await _add_listener(proxy, listener)

    async def unregister_as_listener(self, proxy: Type, listener: dict):
        """
        Removes a registered listener from the specified proxy.

        This function attempts to remove the provided listener from the specified proxy.
        It employs a retry mechanism to handle potential ConnectionError exceptions.

        Args:
            proxy: A callable object representing the proxy from which the listener will be removed.
            listener (dict): The listener to be removed. Should be a dictionary containing
                listener details.

        Raises:
            ConnectionError: If the connection to the proxy encounters issues even after
                multiple retry attempts.
        """

        @retry(times=5, exceptions=[ConnectionError])
        async def _remove_listener(proxy, listener):
            async with proxy() as x, x.get_service_proxy() as srv:
                rc = await srv.remove_listener_async(listener)
                _LOGGER.debug(f"Response from remove_listener: {rc=}")

        # Check if the CS is available
        try:
            async with proxy():
                pass
        except ConnectionError:
            _LOGGER.warning(
                f"The {proxy.__class__.__name__} endpoint is not responding, {listener['name']} not un-registered."
            )
            return

        _LOGGER.info(f"Removing {self.__class__.__name__} as a listener from {proxy.__name__}")
        await _remove_listener(proxy, listener)
