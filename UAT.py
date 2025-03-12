import threading
import time
import mpl_qtthread.backend
import matplotlib
import matplotlib.backends.backend_qt
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtWidgets, QtCore, QT_API

app = QtWidgets.QApplication.instance()
print(app)

if app is None:
    if QT_API in {"PyQt6", "PySide6"}:
        qt_version = 6
    elif QT_API in {"PyQt5", "PySide2"}:
        qt_version = 5
    else:
        raise RuntimeError("Should never be here")

    if qt_version == 5:
        try:
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        except AttributeError:  # Only for Qt>=5.6, <6.
            pass
    try:
        QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
            QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except AttributeError:  # Only for Qt>=5.14.
        pass
    app = QtWidgets.QApplication(["mpl qtthread UAT"])

    app.setQuitOnLastWindowClosed(True)

# tell Matplotlib to use this backend
matplotlib.use("module://mpl_qtthread.backend_agg")

# suppress (now) spurious warnings for mpl3.3+
mpl_qtthread.monkeypatch_pyplot()


# button to exit early and to make sure qapp does not quit!
bt = QtWidgets.QPushButton("Quit")
bt.pressed.connect(app.quit)
bt.show()

tot_time = 15

# stop UAT in 12s
timer = QtCore.QTimer()
timer.setSingleShot(True)
timer.timeout.connect(app.quit)
timer.start(tot_time * 1000)  # this is in ms


def background():
    # make a figure and plot some data
    fig, ax = plt.subplots()

    plt.show(block=False)
    (ln,) = ax.plot(range(5))
    thread_start_time = start_time = time.monotonic()
    fig.canvas.flush_events()
    # periodically update the figure
    for j in range(5):
        print(
            f"starting block {j} at Δt {time.monotonic() - start_time:.3f} "
            f"(expected ~{j})"
        )
        ln.set_color(f"C{j}")
        ax.set_title(f"cycle {j}")
        fig.set_size_inches(1 + j, 1 + j)
        fig.canvas.draw_idle()
        print(f"line should now be color 'C{j}'")
        time.sleep(1)

    plt.close(fig)
    print("figure is now closed, take a 1s nap")
    time.sleep(1)
    fig2 = plt.figure()
    fig2.show()
    print("New figure!")
    start_time = time.monotonic()
    for j in range(4):
        time.sleep(1)
        fig2.canvas.manager.full_screen_toggle()
        fig2.canvas.manager.set_window_title(f"toggled {j}")
        print(f"toggled Δt {time.monotonic() - start_time:.3f} (expected ~{j + 1})")

    fig3, _ = plt.subplots(3, 1)
    fig3.show()
    print("figure is small again and there are two figures.")
    print("take 1s nap")
    time.sleep(1)
    plt.close("all")
    print(
        f"all figures should be closed\n"
        f"app will exit in {12 - (time.monotonic() - thread_start_time):.02f}s or hit quit."
    )


# start the thread
threading.Thread(target=background, daemon=True).start()


# start the QApplication main loop
app.exec()
