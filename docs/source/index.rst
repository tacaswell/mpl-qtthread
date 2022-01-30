.. Packaging Scientific Python documentation master file, created by
   sphinx-quickstart on Thu Jun 28 12:35:56 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

mpl-qtthread Documentation
==========================

.. toctree::
   :maxdepth: 2

   api
   release_history
   min_versions


Theory of operation
-------------------

When working with Qt and threads you have to be sure to create QObjects on the
thread you are going to use them on and you can only draw to the screen from
the main thread.  Combined, this means that all of the UI creation and work
needs to be done on the main thread.  However, background threads are able to
influence the UI via Qt's Signal/Slot mechanism which can be safely used for
inter-thread communication.

However, when you use the function is `matplotlib.pyplot` to make new
Matplotlib figures it will create a ``QtWidget`` subclass instance for the
canvas and a ``MainWindow`` instance to put the canvas and toolbar in.  Thus,
if you try to use pyplot from any Python thread but the main thread you can run
into significant issue from Qt (never mind that the rest of Matplotlib is not
very thread safe) ranging from windows that never render to crashes.

This works by creating a ``QtCore.QObject`` on the main thread (manually done
via `mpl_qtthread.initialize_qt_teleporter`).  This object has two signals, one
for creating the `~matplotlib.backend_bases.FigureCanvasBase` instance and one for
creating the `~matplotlib.backend_bases.FigureManagerBase` that we need.  As part of
creating this (private) object Slots (aka callbacks) are connected to the
Signals that will do the actual work of creating the instances.

These Signals are used by the Matplotlib Backend that the package implements.
The main thing than is over-ridden from the upstream behavior is that rather
than directly instantiating the ``FigureCanvas`` and ``FigureManager``
instances, it emits enough information to create them to the Signals.  Because
the callbacks for a Signal are processed on the thread the QObject is
affiliated with (and they are by default affiliated with the thread they are
created on) the callbacks to create the QWidgets will run on the main thread.
Thus, we are able to create and update Matplotlib figures from a background
thread while the QApplication runs in the main thread.

Matplotlib still is not actually thread safe so it is important to only update
the Figure from one thread.  If you are extensively panning or zooming while
the background thread is simultaneously updating Figure, it is very likely that
you will suffer race conditions.  Many of these issues should be render
failures due to a temporarily inconsistent Figure state (e.g. updating the x
and y values of a `~matplotlib.lines.Line2D` object to be different
lengths). It is possible that this package will need to develop a way to add
some locking to Matplotilb.


Examples
--------

Python Threads
**************

.. code-block:: python

   import threading
   import time
   import mpl_qtthread.backend
   import matplotlib
   import matplotlib.backends.backend_qt
   import matplotlib.pyplot as plt

   # set up the teleporter
   mpl_qtthread.backend.initialize_qt_teleporter()
   # tell Matplotlib to use this backend
   matplotlib.use("module://mpl_qtthread.backend_agg")

   # import pyplot and make it interactive
   plt.ion()

   # suppress (now) spurious warnings for mpl3.3+
   mpl_qtthread.monkeypatch_pyplot()


   def background():
       # make a figure and plot some data
       fig, ax = plt.subplots()
       (ln,) = ax.plot(range(5))
       # periodically update the figure
       for j in range(5):
           print(f"starting to block {j}")
           ln.set_color(f"C{j}")
           ax.set_title(f"cycle {j}")
           fig.canvas.draw_idle()
           time.sleep(5)
       plt.close(fig)


   # start the thread
   threading.Thread(target=background).start()
   # start the QApplication main loop
   matplotlib.backends.backend_qt.qApp.exec()
