============
mpl-qtthread
============

A Matplotlib backend for working with (Q)Threads and Qt

* Free software: 3-clause BSD license
* Documentation: (COMING SOON!) https://tacaswell.github.io/mpl-qtthread.

Features
--------

A minimal example:

.. code-block:: python



   import threading
   import time
   import matplotlib
   import matplotlib.backends.backend_qt
   import matplotlib.pyplot as plt

   import mpl_qtthread

   matplotlib.use("module://mpl_qtthread.backend_agg")

   matplotlib.backends.backend_qt._create_qApp()

   mpl_qtthread.monkeypatch_pyplot()

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
       print("Done! please close the window")

   threading.Thread(target=background).start()
   matplotlib.backends.backend_qt.qApp.exec()
