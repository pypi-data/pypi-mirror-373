#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/20 11:04
# @Author  : 江斌
# @Software: PyCharm
import sys
import time
import queue
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWinExtras import QWinThumbnailToolBar, QWinThumbnailToolButton


class TaskThread(QtCore.QThread):
    task_finished = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_queue = queue.Queue()
        self.task_results = {}
        self._stop = False
        self._task_running = False

    def delegate_task(self, task_name, task_func, args=None, kwargs=None):
        self.task_queue.put((task_name, task_func, args, kwargs))

    def get_task_result(self, task_name=None):
        if task_name is None:
            if self.task_results:
                item = self.task_results.popitem()
                task_name, task_result = item
                return task_result
        if task_name in self.task_results:
            result = self.task_results.pop(task_name)
            return result

    def is_busy(self):
        if not self.task_queue.empty():
            return True
        return self._task_running

    def clear_tasks(self):
        self.task_queue.queue.clear()

    def stop(self):
        self._stop = True

    def task_count(self):
        if not self.is_busy():
            return 0
        return max(1, self.task_queue.qsize() + (1 if self._task_running else 0))

    def run(self):
        while not self._stop:
            if self.task_queue.empty():
                time.sleep(0.01)
                continue
            self._task_running = True
            task = self.task_queue.get()
            task_name, task_func, args, kwargs = task[:4]
            try:
                ret = task_func(*(args or ()), **(kwargs or {}))
                result = {"task_name": task_name, "result": "SUC", "info": ret}
            except Exception as exc:
                result = {"task_name": task_name, "result": "ERROR", "info": exc}
            self.task_finished.emit(result)
            self.task_results[task_name] = result
            self._task_running = False


class SimpleProgress(object):
    def __init__(self, parent=None):
        self.task_thread = TaskThread(parent=parent)
        self.task_thread.start()
        self.parent = parent

    def get_dlg(self, title, max_num):
        progress_dlg = QtWidgets.QProgressDialog(title, "取消", 0, max_num, self.parent)
        progress_dlg.setWindowTitle(title)
        progress_dlg.setWindowModality(QtCore.Qt.WindowModal)
        progress_dlg.setWindowFlags(progress_dlg.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        progress_dlg.forceShow()
        progress_dlg.setValue(0)
        progress_dlg.setAutoClose(False)
        progress_dlg.setAutoReset(False)
        return progress_dlg

    def stop(self):
        self.task_thread.stop()

    def wait(self, wait_time):
        self.task_thread.wait(wait_time)

    def run_func_in_progress(self, task_name, task_func, args=None, kwargs=None, desc_info="操作中请等待\n%s/%s",
                             desc_title="请等待操作完成", post_process_func=None):
        self.delegate_task(task_name, task_func, args, kwargs)
        self.wait_for_all_tasks(desc_info, desc_title, post_process_func)

    def delegate_task(self, task_name, task_func, args=None, kwargs=None):
        self.task_thread.delegate_task(task_name, task_func, args, kwargs)

    def wait_for_all_tasks(self, desc_info="操作中请等待\n%s/%s",
                           desc_title="请等待操作完成",
                           post_func=None, error_func=None):
        count = self.task_thread.task_count()
        total_progress = max(count, 1)
        results = {}
        dialog = self.get_dlg(title=desc_title, max_num=total_progress)
        print(f'----------------------->{count}')
        while self.task_thread.is_busy():
            if dialog.wasCanceled():
                self.task_thread.clear_tasks()
                continue
            result = self.task_thread.get_task_result()
            if result is not None:
                results[result["task_name"]] = result
            print(len(results), total_progress)
            progress = min(len(results), total_progress)
            dialog.setLabelText(desc_info % (len(results), count))
            dialog.setValue(progress)
            time.sleep(0.01)

        dialog.setValue(total_progress)

        print(total_progress)
        time.sleep(0.1)
        result = self.task_thread.get_task_result()
        if result is not None:
            results[result["task_name"]] = result
            dialog.close()
        if post_func is not None:
            post_func(results)


class TestWidget(QtWidgets.QWidget):
    def __init__(self):
        super(TestWidget, self).__init__()
        self.p = SimpleProgress()
        self.init_ui()

    def init_ui(self):
        self.button = QtWidgets.QPushButton('开始任务')
        self.button.clicked.connect(self.run_task)
        v = QtWidgets.QVBoxLayout()
        v.addWidget(self.button)
        self.setLayout(v)

    def run_task(self):
        self.p.delegate_task(task_name='task_xx1', task_func=self.task1)
        self.p.delegate_task(task_name='task_xx2', task_func=self.task2)
        self.p.delegate_task(task_name='task_xx3', task_func=self.task3)
        self.p.delegate_task(task_name='task_xx3', task_func=self.task3)
        self.p.wait_for_all_tasks()

    def task1(self):
        for i in range(10):
            print(f'task1: {i}')
            time.sleep(0.1)

    def task2(self):
        for i in range(10):
            print(f'task2: {i}')
            time.sleep(0.1)

    def task3(self):
        for i in range(10):
            print(f'task3: {i}')
            time.sleep(0.1)


def testxx(widget):
    thumbbar = QWinThumbnailToolBar(widget)
    thumbbar.setWindow(widget.windowHandle())

    settings = QWinThumbnailToolButton(thumbbar)

    settings.setToolTip("Settings")
    settings.setIcon(QtGui.QIcon('radarxx.png'))
    settings.setDismissOnClick(True)
    settings.clicked.connect(lambda: print('settings.....'))

    playPause = QWinThumbnailToolButton(thumbbar)
    playPause.setToolTip("Play/Pause")
    playPause.setIcon(QtGui.QIcon('start_on.png'))
    playPause.clicked.connect(lambda: print('pause.....'))

    thumbbar.addButton(settings)
    thumbbar.addButton(playPause)


def test():
    app = QApplication(sys.argv)
    w = TestWidget()
    w.show()
    testxx(w)
    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
