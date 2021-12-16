from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from .backend import _BackendThreads


@_BackendThreads.export
class BackendAgg(_BackendThreads):
    FigureCanvas = FigureCanvasQTAgg
