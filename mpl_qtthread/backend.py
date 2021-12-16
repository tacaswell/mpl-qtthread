import threading
import functools

from matplotlib.figure import Figure

from matplotlib.backends.qt_compat import QtCore
from matplotlib.backends.backend_qt import FigureCanvasQT, _BackendQT, _create_qApp

# The purpose of initialize_qt_teleporter, _get_teleporter is to ensure that Qt
# GUI events are processed on the main thread.
# this is adapted from github.com/bluesky/bluesky

_teleporter = None


def initialize_qt_teleporter():
    """
    Set up the Qt 'teleporter' to move widget creation to the main thread.

    This makes it safe to create Matplotlib figures from threads other than the
    main one.

    .. warning ::

        This must be run on the main thread.

    Raises
    ------
    RuntimeError
        If called from any thread but the main thread

    """
    global _teleporter
    if _build_teleporter.cache_info().currsize:
        # Already initialized.
        return
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError(
            "initialize_qt_teleporter() may only be called from the main " "thread."
        )
    # first make sure we have the q
    _create_qApp()
    _teleporter = _build_teleporter()


# make sure we only do this once
@functools.lru_cache(maxsize=1)
def _build_teleporter():
    # TODO sort out what this does with QThreads
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError("Must initialize teleporter on main thread!")

    def create_widget(figure, canvas_class, evt):
        # do not worry, circular references mean the canvas gets put
        # on the figure here!
        canvas_class(figure)
        evt.set()

    def create_manager(figure, num, manager_class, evt):
        # Again, we are relying on circular references to stash the newly
        # created object
        manager_class(figure.canvas, num)
        evt.set()

    class Teleporter(QtCore.QObject):
        create_widget = QtCore.Signal(Figure, type, threading.Event)
        # TODO make the second argument int or str
        create_manager = QtCore.Signal(Figure, int, type, threading.Event)

    t = Teleporter()
    t.create_widget.connect(create_widget)
    t.create_manager.connect(create_manager)
    return t


class _BackendThreads(_BackendQT):
    @classmethod
    def new_figure_manager_given_figure(cls, num, figure):
        if _teleporter is None:
            raise RuntimeError("teleporter not inited")
        evt = threading.Event()
        _teleporter.create_widget.emit(figure, cls.FigureCanvas, evt)
        if not evt.wait(5):
            raise RuntimeError("failed to create canvas")

        canvas = figure.canvas
        evt = threading.Event()
        _teleporter.create_manager.emit(figure, num, cls.FigureManager, evt)
        if not evt.wait(5):
            raise RuntimeError("failed to create manager")

        return canvas.manager
