from concurrent.futures import Future

from typing import Callable, List, Optional

import threading
import functools


from matplotlib.backends.qt_compat import QtCore

try:
    from matplotlib.backends.backend_qt import _BackendQT
except ImportError:
    from matplotlib.backends.backend_qt5 import _BackendQT5 as _BackendQT


# Addapted from
# https://github.com/napari/superqt/blob/ba1ae92bccc282da040281751b71afcbe4c0e302/src/superqt/utils/_ensure_thread.py
class CallCallable(QtCore.QObject):
    finished = QtCore.Signal(object)
    instances: List["CallCallable"] = []

    def __init__(self, callable, *args, **kwargs):
        super().__init__()
        self._callable = callable
        self._args = args
        self._kwargs = kwargs
        CallCallable.instances.append(self)

    @QtCore.Slot()
    def call(self):
        CallCallable.instances.remove(self)
        res = self._callable(*self._args, **self._kwargs)
        self.finished.emit(res)


def ensure_main_thread(
    func: Optional[Callable] = None, await_return: bool = True, timeout: int = 5
):
    """Decorator that ensures a function is called in the main QApplication thread.
    It can be applied to functions or methods.
    Parameters
    ----------
    func : callable
        The method to decorate, must be a method on a QObject.
    await_return : bool, optional
        Whether to block and wait for the result of the function, or return immediately.
        by default True
    timeout : float, optional
        If `await_return` is `True`, time (in seconds) to wait for the result
        before raising a TimeoutError, by default 5
    """

    def _out_func(func_):
        @functools.wraps(func_)
        def _func(*args, **kwargs):
            return _run_in_thread(
                func_,
                QtCore.QCoreApplication.instance().thread(),
                await_return,
                timeout,
                *args,
                **kwargs,
            )

        return _func

    if func is None:
        return _out_func
    return _out_func(func)


def _run_in_thread(
    func: Callable,
    thread: QtCore.QThread,
    await_return: bool,
    timeout: int,
    *args,
    **kwargs,
):
    future = Future()  # type: ignore
    if thread is QtCore.QThread.currentThread():
        result = func(*args, **kwargs)
        if not await_return:
            future.set_result(result)
            return future
        return result
    f = CallCallable(func, *args, **kwargs)
    f.moveToThread(thread)
    f.finished.connect(future.set_result, QtCore.Qt.ConnectionType.DirectConnection)
    QtCore.QMetaObject.invokeMethod(f, "call", QtCore.Qt.ConnectionType.QueuedConnection)  # type: ignore
    return future.result(timeout=timeout) if await_return else future


class FigureCanvasQT(_BackendQT.FigureCanvas):
    def flush_events(self):
        # only try to flush events if we are on main thread
        if threading.current_thread() is threading.main_thread():
            return super().flush_events()

    def start_event_loop(self, timeout=0):
        # only try to flush events if we are on main thread
        if threading.current_thread() is threading.main_thread():
            return super().start_event_loop(timeout=timeout)


class FigureManagerQT(_BackendQT.FigureManager):
    @ensure_main_thread
    def destroy(self):
        return super().destroy()

    @ensure_main_thread
    def resize(self, width, height):
        return super().resize(width, height)

    @ensure_main_thread
    def show(self):
        return super().show()


class _BackendThreads(_BackendQT):
    @classmethod
    @ensure_main_thread
    def new_figure_manager_given_figure(cls, num, figure):
        return super().new_figure_manager_given_figure(num, figure)

    FigureManager = FigureManagerQT
    FigureCanvas = FigureCanvasQT
