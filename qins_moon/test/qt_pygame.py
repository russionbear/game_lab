#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :qt_pygame.py
# @Time      :16/02/2023
# @Author    :russionbear
# @Function  :function
import pygame_gui
from PyQt5 import QtGui, QtWidgets, QtCore
import pygame
import sys

# pygame.init()


class CustomLabel(QtWidgets.QLabel):
    def __init__(self, parent, size):
        super().__init__(parent)
        self.setFixedSize(size)
        pygame.display.set_caption('Quick Start')
        self.window_surface = pygame.display.set_mode((self.width(), self.height()))

        self.background = pygame.Surface(self.window_surface.get_size())
        self.background.fill(pygame.Color('#000000'))
        self.manager = pygame_gui.UIManager(self.window_surface.get_size())
        self.hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                                    text='Say Hello',
                                                    manager=self.manager)
        self.clock = pygame.time.Clock()

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.tick)
        self.timer.start()

    def tick(self):
        # for event in pygame.event.get():
        #     # print(event, hasattr(event, 'uu'))
        #     if event.type == pygame.QUIT:
        #         is_running = False
        #
        #     self.manager.process_events(event)

        # time_delta = self.clock.tick(60) / 1000.0
        # self.manager.update(time_delta)

        self.window_surface.blit(self.background, (0, 0))
        # self.manager.draw_ui(self.window_surface)

        pygame.display.update()
        data = self.window_surface.get_buffer().raw
        image = QtGui.QImage(data, self.width(), self.height(), QtGui.QImage.Format_RGB32)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.setPixmap(pixmap)


class MainWin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # self.customLabel = CustomLabel(self, QtCore.QSize(500, 500))





from multiprocessing import Process

def f(name):
    APP = QtWidgets.QApplication(sys.argv)
    WINDOW = MainWin()
    WINDOW.show()
    sys.exit(APP.exec_())

def f2(name):
    import pygame
    import pygame_gui

    pygame.init()

    pygame.display.set_caption('Quick Start')
    window_surface = pygame.display.set_mode((800, 600), pygame.NOFRAME|pygame.HIDDEN)

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((800, 600))

    hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                                text='Say Hello',
                                                manager=manager)

    clock = pygame.time.Clock()
    is_running = True
    # window_surface.

    while is_running:
        time_delta = clock.tick(60) / 1000.0
        event = pygame.event.Event(pygame.KEYUP, uu=90)
        pygame.event.post(event)
        for event in pygame.event.get():
            # print(event, hasattr(event, 'uu'))
            if event.type == pygame.QUIT:
                is_running = False

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()

if __name__ == '__main__':
    p = Process(target=f, args=('bob',))
    p.start()
    p2 = Process(target=f2, args=('ccc',))
    p2.start()
    p.join()
    p2.join()

