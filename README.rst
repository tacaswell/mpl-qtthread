============
mpl-qtthread
============

.. image:: https://img.shields.io/travis/tacaswell/mpl-qtthread.svg
        :target: https://travis-ci.org/tacaswell/mpl-qtthread

.. image:: https://img.shields.io/pypi/v/mpl-qtthread.svg
        :target: https://pypi.python.org/pypi/mpl-qtthread


A Matplotlib backend for working with (Q)Threads and Qt

* Free software: 3-clause BSD license
* Documentation: (COMING SOON!) https://tacaswell.github.io/mpl-qtthread.

Features
--------

A Mininal example ::


   import threading
   import time
   import mpl_qtthread.backend
   import matplotlib
   import matplotlib.backends.backend_qt

   mpl_qtthread.backend.initialize_qt_teleporter()
   matplotlib.use("module://mpl_qtthread.backend_agg")

   import matplotlib.pyplot as plt

   plt.ion()


   def background():
       # time.sleep(1)
       fig, ax = plt.subplots()
       (ln,) = ax.plot(range(5))
       for j in range(5):
           print(f"starting to block {j}")
           ln.set_color(f"C{j}")
           ax.set_title(f'cycle {j}')
           fig.canvas.draw_idle()
           time.sleep(5)


   threading.Thread(target=background).start()
   matplotlib.backends.backend_qt.qApp.exec()
