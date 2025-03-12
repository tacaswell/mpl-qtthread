from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from .backend import FigureCanvasQT

class FigureCanvas(FigureCanvasQT, FigureCanvasQTAgg):
    ...
