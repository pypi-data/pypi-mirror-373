#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.08.11 14:00:00                  #
# ================================================== #

import os
import time

from PySide6.QtCore import QObject, Signal, QRunnable, Slot


class Camera:
    def __init__(self, window=None):
        """
        Camera core

        :param window: Window instance
        """
        self.window = window
        self.capture = None
        self.current = None

    def install(self):
        """Install provider data"""
        img_dir = self.window.core.config.get_user_dir('capture')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir, exist_ok=True)


class CaptureSignals(QObject):
    finished = Signal()
    unfinished = Signal()
    destroyed = Signal()
    started = Signal()
    stopped = Signal()
    capture = Signal(object)
    error = Signal(object)


class CaptureWorker(QRunnable):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.signals = CaptureSignals()
        self.args = args
        self.kwargs = kwargs
        self.window = None
        self.initialized = False
        self.capture = None
        self.frame = None
        self.allow_finish = False

    def setup_camera(self):
        """Initialize camera"""
        try:
            import cv2
            # get params from global config
            self.capture = cv2.VideoCapture(self.window.core.config.get('vision.capture.idx'))
            if not self.capture or not self.capture.isOpened():
                self.allow_finish = False
                self.signals.unfinished.emit()
                return
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.window.core.config.get('vision.capture.width'))
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.window.core.config.get('vision.capture.height'))
        except Exception as e:
            self.window.core.debug.log(e)
            if self.signals is not None:
                self.signals.error.emit(e)
                self.signals.finished.emit(e)

    @Slot()
    def run(self):
        """Frame capture loop"""
        target_fps = 30
        fps_interval = 1.0 / target_fps
        self.allow_finish = True
        try:
            import cv2
            if not self.initialized:
                self.setup_camera()
                self.signals.started.emit()
                self.initialized = True
            last_frame_time = time.time()
            while True:
                if self.window.is_closing \
                        or self.capture is None \
                        or not self.capture.isOpened() \
                        or self.window.controller.camera.stop:
                    self.release()  # release camera
                    self.signals.stopped.emit()
                    break
                _, frame = self.capture.read()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                now = time.time()
                if now - last_frame_time >= fps_interval:
                    self.signals.capture.emit(frame)
                    last_frame_time = now

        except Exception as e:
            self.window.core.debug.log(e)
            if self.signals is not None:
                self.signals.error.emit(e)

        finally:
            self.release()  # release camera
            if self.signals is not None:
                if self.allow_finish:
                    self.signals.finished.emit()
                else:
                    self.signals.unfinished.emit()
            self.cleanup()

    def release(self):
        """Release camera"""
        if self.capture is not None and self.capture.isOpened():
            self.capture.release()
            self.capture = None
            self.frame = None
            self.initialized = False

    def cleanup(self):
        """Cleanup resources after worker execution."""
        sig = self.signals
        self.signals = None
        if sig is not None:
            try:
                sig.deleteLater()
            except RuntimeError:
                pass
