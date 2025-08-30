# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
"""
Copied from AequilibraE
Original Author:  UNKNOWN. COPIED FROM STACKOVERFLOW BUT CAN'T REMEMBER EXACTLY WHERE
"""

from polaris.utils.env_utils import inside_qgis

if inside_qgis:
    from qgis.PyQt.QtCore import pyqtSignal, QThread  # type: ignore

    class WorkerThread(QThread):
        if inside_qgis:
            jobFinished = pyqtSignal(object)

        def __init__(self, parentThread):
            QThread.__init__(self, parentThread)

        def run(self):
            self.running = True
            success = self.doWork()
            if inside_qgis:
                self.jobFinished.emit(success)

        def stop(self):
            self.running = False
            pass

        def doWork(self):
            "It will overloaded by the classes that subclass this"
            return True

        def cleanUp(self):
            pass

else:

    class WorkerThread:  # type: ignore
        def __init__(self, *arg):
            pass
