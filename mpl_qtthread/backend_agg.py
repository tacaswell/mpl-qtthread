try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
except ImportError:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from .backend import _BackendThreads


@_BackendThreads.export
class BackendAgg(_BackendThreads):
    FigureCanvas = FigureCanvasQTAgg
