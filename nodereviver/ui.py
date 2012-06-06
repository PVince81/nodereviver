'''
    This file is part of nodereviver

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    @author: Vincent Petry <PVince81@yahoo.fr>
'''

class UI(object):
    def __init__(self):
        self.widgets = []
        self.dirty = False

    def addWidget(self, widget):
        self.widgets.append(widget)
        self.dirty = True

class Widget(object):
    def __init__(self, rect):
        self.rect = rect
        self.visible = True

class Button(Widget):
    def __init__(self, rect, text, action = None):
        Widget.__init__(self, rect)
        self.text = text
        self.action = action

class GameUI(UI):
    def __init__(self, config):
        UI.__init__(self)
        buttonSize = 80
        offset = (config.screenSize[0] - buttonSize * 3, config.screenSize[1] - buttonSize * 2)
        self.upButton = Button((offset[0]+buttonSize, offset[1], buttonSize, buttonSize), "Up", "up")
        self.leftButton = Button((offset[0], offset[1] + buttonSize, buttonSize, buttonSize), "Left", "left")
        self.downButton = Button((offset[0]+buttonSize, offset[1] + buttonSize, buttonSize, buttonSize), "Down", "down")
        self.rightButton = Button((offset[0] + buttonSize * 2, offset[1] + buttonSize, buttonSize, buttonSize), "Right", "right")

        offset = (config.screenSize[0] - 50, 0)
        self.backButton = Button((config.screenSize[0] - buttonSize, 0, buttonSize, buttonSize), "Back", "back")
        self.pauseButton = Button((config.screenSize[0] - buttonSize, 150, buttonSize, buttonSize), "Pause", "togglepause")

        taskSwitchButton = Button((0, 0, 50, 50), "[]", "taskswitch")

        self.addWidget(self.upButton)
        self.addWidget(self.downButton)
        self.addWidget(self.leftButton)
        self.addWidget(self.rightButton)
        self.addWidget(self.pauseButton)
        self.addWidget(self.backButton)
        #self.addWidget(taskSwitchButton)

    def getWidgetAt(self, pos):
        for widget in self.widgets:
            rect = widget.rect
            if ( rect[0] < pos[0] and (rect[0] + rect[2]) > pos[0] and
                 rect[1] < pos[1] and (rect[1] + rect[3]) > pos[1] ):
                return widget

    def setControlsVisibility(self, visible):
        self.upButton.visible = visible
        self.downButton.visible = visible
        self.leftButton.visible = visible
        self.rightButton.visible = visible
        self.pauseButton.visible = visible
        self.dirty = True

