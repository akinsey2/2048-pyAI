# Form implementation generated from reading ui file '2048ui.ui'
#
# Originally Created by: PyQt6 UI code generator 6.1.0

from PyQt6 import QtCore, QtGui, QtWidgets
from math import log2
import GameMgr
import AutoPlay
# import pprint

SIZE = 4
BOARD_SIZE_PX = 450
BOARD_MARGIN = 25


# To handle keyPressEvent, must create custom subclass with default overridden.
class CentralWidget(QtWidgets.QWidget):

    def __init__(self, mainwindow, ui_mainwindow):
        super().__init__(mainwindow)     # Establish parent, Initialize parent QWidget class
        self.custom_init()
        self.ui_mainwindow = ui_mainwindow

    def custom_init(self):
        pass

    # Custom Handler for keyboard key press events
    def keyPressEvent(self, event):

        self.releaseKeyboard()

        if not isinstance(event, QtGui.QKeyEvent):
            raise TypeError("CentralWidget keyPressEvent() event is NOT QKeyEvent() ")

        if event.key() == QtCore.Qt.Key.Key_Up.value:
            # print("MOVE UP")
            valid_move, tile_move_vect, _, _ = self.ui_mainwindow.game.move_tiles(0, True)  # '0' means 'Up'

        elif event.key() == QtCore.Qt.Key.Key_Right.value:
            # print("MOVE RIGHT")
            valid_move, tile_move_vect, _, _ = self.ui_mainwindow.game.move_tiles(1, True)  # '1' means 'Right'

        elif event.key() == QtCore.Qt.Key.Key_Down.value:
            # print("MOVE DOWN")
            valid_move, tile_move_vect, _, _ = self.ui_mainwindow.game.move_tiles(2, True)  # '2' means 'Down'

        elif event.key() == QtCore.Qt.Key.Key_Left.value:
            # print("MOVE LEFT")
            valid_move, tile_move_vect, _, _ = self.ui_mainwindow.game.move_tiles(3, True)  # '3' means 'Left'

        else:
            valid_move = False

        if valid_move:
            self.ui_mainwindow.animate_tiles(tile_move_vect)

        else:   # Invalid move

            # Use add_random_tile() to detect possible game over
            _, _, game_over, _ = self.ui_mainwindow.game.add_random_tile(commit=False)

            if game_over:
                self.ui_mainwindow.game_over()
            else:   # Game not over, continue
                self.grabKeyboard()


# Custom class for the Tiles displayed on board, subclass of "QLabel"
class TileWidget(QtWidgets.QLabel):

    tile_colors = ("FFFFC8", "FFE6C8", "FFCC99", "FFCCCC", "FF9999",
                   "CCECFF", "99CCFF", "CCFFFF", "CCFFCC", "CCFF99",
                   "66FF66", "00CCFF", "9999FF", "FF99FF", "FF0066")

    def __init__(self, parent, num, row, col):
        super().__init__(str(num), parent)

        self.num = property(self.get_num, self.set_num)
        self._num = num

        self.setGeometry(col*100+25, row*100+25, 100, 100)
        # self.setFrameStyle(QtWidgets.QFrame.Shape.Panel | QtWidgets.QFrame.Shadow.Raised)
        self.setStyleSheet("margin: 2px; border: 4px solid grey; border-radius: 5px; " +
                           "background-color: #" + TileWidget.tile_colors[int(log2(self._num)) - 1] +
                           "; font: bold 32px;")
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setText(str(self._num))

    def __repr__(self):
        return str(self._num)

    def get_num(self):
        return self._num

    def set_num(self, val):
        self._num = val

    def update_num(self, num):

        self._num = num

        if self._num < 10000:
            self.setStyleSheet("margin: 2px; border: 4px solid grey; border-radius: 5px; " +
                               "background-color: #" + TileWidget.tile_colors[int(log2(self._num)) - 1] +
                               "; font: bold 32px;")
        elif self._num > 9999:
            self.setStyleSheet("margin: 2px; border: 4px solid grey; border-radius: 5px; " +
                               "background-color: #" + TileWidget.tile_colors[int(log2(self._num)) - 1] +
                               "; font: bold 24px;")

        self.setText(str(self._num))


class UiMainWindow(object):

    def __init__(self, main_window):

        main_window.setObjectName("MainWindow")
        main_window.resize(500, 775)
        self.centralwidget = CentralWidget(main_window, self)      # Custom subclass of QWidget
        self.centralwidget.setObjectName("centralwidget")

        # Game Title
        self.game_title = QtWidgets.QLabel(self.centralwidget)
        self.game_title.setGeometry(QtCore.QRect(180, 10, 121, 61))
        font = QtGui.QFont()
        font.setPointSize(36)
        font.setBold(True)
        self.game_title.setFont(font)
        self.game_title.setMidLineWidth(0)
        self.game_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.game_title.setObjectName("game_title")

        # Scores Area
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(50, 70, 133, 54))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.curr_score_label = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.curr_score_label.setFont(font)
        self.curr_score_label.setObjectName("curr_score_label")
        self.verticalLayout.addWidget(self.curr_score_label)
        self.curr_score = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.curr_score.setFont(font)
        self.curr_score.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.curr_score.setObjectName("curr_score")
        self.verticalLayout.addWidget(self.curr_score)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(320, 70, 133, 54))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.record_score_label = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.record_score_label.setFont(font)
        self.record_score_label.setObjectName("record_score_label")
        self.verticalLayout_2.addWidget(self.record_score_label)
        self.record_score = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.record_score.setFont(font)
        self.record_score.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.record_score.setObjectName("record_score")
        self.verticalLayout_2.addWidget(self.record_score)

        # Game Board
        self.game_board = QtWidgets.QFrame(self.centralwidget)
        self.game_board.setGeometry(QtCore.QRect(25, 130, 450, 450))
        self.game_board.setFrameStyle(QtWidgets.QFrame.Shape.StyledPanel.value)
        self.game_board.setAutoFillBackground(True)
        self.game_board.setObjectName("game_board")

        # Start, Save and Load
        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_button.setGeometry(QtCore.QRect(20, 610, 100, 100))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.start_button.setFont(font)
        self.start_button.setObjectName("start_button")
        self.start_button.clicked.connect(self.start_clicked)

        self.save_button = QtWidgets.QPushButton(self.centralwidget)
        self.save_button.setEnabled(False)
        self.save_button.setGeometry(QtCore.QRect(140, 620, 100, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.save_button.setFont(font)
        self.save_button.setObjectName("save_button")

        self.load_but = QtWidgets.QPushButton(self.centralwidget)
        self.load_but.setGeometry(QtCore.QRect(140, 670, 100, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.load_but.setFont(font)
        self.load_but.setObjectName("load_but")
        self.load_but.setEnabled(False)

        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(240, 600, 20, 131))
        self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")

        # Auto-Play Area
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(260, 600, 211, 131))
        self.widget.setObjectName("widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.ap_spd_label = QtWidgets.QLabel(self.widget)
        self.ap_spd_label.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.ap_spd_label.setFont(font)
        self.ap_spd_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.ap_spd_label.setObjectName("ap_spd_label")
        self.verticalLayout_3.addWidget(self.ap_spd_label)
        self.horizontalSlider = QtWidgets.QSlider(self.widget)
        self.horizontalSlider.setEnabled(False)
        self.horizontalSlider.setMinimum(30)
        self.horizontalSlider.setMaximum(3000)
        self.horizontalSlider.setPageStep(5)
        self.horizontalSlider.setSingleStep(50)
        self.horizontalSlider.setPageStep(1000)
        self.horizontalSlider.setTickInterval(200)
        self.horizontalSlider.setInvertedAppearance(True)
        self.horizontalSlider.setInvertedControls(True)
        self.horizontalSlider.setValue(1000)
        self.horizontalSlider.valueChanged.connect(self.update_ap_speed)
        self.horizontalSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.horizontalSlider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.horizontalSlider.setTickInterval(5)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.verticalLayout_3.addWidget(self.horizontalSlider)
        self.comboBox = QtWidgets.QComboBox(self.widget)
        self.comboBox.setEnabled(False)
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout_3.addWidget(self.comboBox)
        self.ap_start_button = QtWidgets.QPushButton(self.widget)
        self.ap_start_button.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.ap_start_button.setFont(font)
        self.ap_start_button.setObjectName("ap_start_button")
        self.ap_start_button.clicked.connect(self.autoplay_clicked)
        self.verticalLayout_3.addWidget(self.ap_start_button)

        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 499, 22))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        # for enabling multi-language support
        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

        self.game = None
        self.current_game = False
        self.is_paused = True

        self.tile_widgets = [[None] * SIZE for _ in range(SIZE)]
        self.next_tile_widgets = [[None] * SIZE for _ in range(SIZE)]
        self.tiles_to_delete = []

        self.anim_group = None
        self.anim_duration = 100

        # Setup for Auto-Play function
        self.autoplayer = None
        self.autoplaying = False
        self.autoplay_speed = 1.0

        self.autoplay_timer = QtCore.QTimer(self.centralwidget)
        self.autoplay_timer.setInterval(1000)
        self.autoplay_timer.setSingleShot(False)
        self.autoplay_timer.setTimerType(QtCore.Qt.TimerType.CoarseTimer)
        self.autoplay_timer.timeout.connect(self.autoplay_move)

    def retranslate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.game_title.setText(_translate("MainWindow", "2048"))
        self.start_button.setText(_translate("MainWindow", "Start"))
        self.save_button.setText(_translate("MainWindow", "Save Game"))
        self.load_but.setText(_translate("MainWindow", "Load Game"))
        self.curr_score_label.setText(_translate("MainWindow", "Current Score"))
        self.curr_score.setText(_translate("MainWindow", "0"))
        self.record_score_label.setText(_translate("MainWindow", "Record High Score"))
        self.record_score.setText(_translate("MainWindow", "0"))
        self.ap_spd_label.setText(_translate("MainWindow", "Auto-Play Speed"))
        self.ap_start_button.setText(_translate("MainWindow", "Start Auto-Play"))

    def start_clicked(self):

        # If no game is in progress
        if not self.current_game:
            self.new_game()

        else:
            if self.is_paused:  # User clicked "Play"
                self.is_paused = False
                self.centralwidget.grabKeyboard()
                self.start_button.setText("Pause")
                self.ap_start_button.setEnabled(True)
                self.horizontalSlider.setEnabled(True)

            else:               # User clicked "Pause"
                self.is_paused = True
                self.centralwidget.releaseKeyboard()
                self.start_button.setText("Play")
                self.ap_start_button.setEnabled(False)
                self.horizontalSlider.setEnabled(False)

    def autoplay_clicked(self):

        # If autoplay is currently paused, start AutoPlay
        if self.autoplaying is False:
            self.autoplay_start()
            return

        # If AutoPlay is active, Pause it.
        else:
            self.autoplay_stop()

    def autoplay_start(self):
        self.centralwidget.releaseKeyboard()
        self.autoplayer = AutoPlay.AutoPlayer(self.game)
        self.autoplaying = True
        self.ap_start_button.setText("Pause AutoPlay")
        self.autoplay_timer.start()

    def autoplay_stop(self):
        self.autoplay_timer.stop()
        self.autoplaying = False
        self.ap_start_button.setText("Start AutoPlay")
        self.centralwidget.grabKeyboard()

    def autoplay_move(self):

        move_dir = self.autoplayer.get_move()
        valid_move, tile_move_vect, _, _ = self.game.move_tiles(move_dir, True)

        self.animate_tiles(tile_move_vect)

    def update_ap_speed(self):

        self.autoplay_timer.stop()

        value = self.horizontalSlider.value()
        self.autoplay_timer.setInterval(value)

        if value/4 > 100:
            self.anim_duration = 100
        else:
            self.anim_duration = int(value / 4)

        if self.autoplaying:
            self.autoplay_timer.start()

    def animate_tiles(self, vectors):

        self.anim_group = QtCore.QParallelAnimationGroup()
        anims = []

        # By Row
        for row in range(SIZE):
            for col in range(SIZE):
                if vectors[row][col][0] or vectors[row][col][1]:

                    end_x = self.tile_widgets[row][col].x() + 100 * vectors[row][col][0]
                    end_y = self.tile_widgets[row][col].y() + 100 * vectors[row][col][1]
                    anims.append(QtCore.QPropertyAnimation(self.tile_widgets[row][col], b"pos"))
                    anims[-1].setStartValue(self.tile_widgets[row][col].pos())
                    anims[-1].setEndValue(QtCore.QPoint(end_x, end_y))
                    anims[-1].setDuration(self.anim_duration)
                    anims[-1].setEasingCurve(QtCore.QEasingCurve.Type.Linear)
                    self.anim_group.addAnimation(anims[-1])

        self.anim_group.finished.connect(self.delete_and_new)
        self.autoplay_timer.stop()
        self.anim_group.start()

    def delete_and_new(self):

        if self.autoplaying:
            self.autoplay_timer.start()

        for tile in self.tiles_to_delete:
            tile.hide()
            tile.destroy()

        self.curr_score.setText(str(self.game.score))
        self.tile_widgets = self.next_tile_widgets

        empty = 0
        for row in range(SIZE):
            for col in range(SIZE):

                if self.tile_widgets[row][col]:
                    self.tile_widgets[row][col].update_num(self.game.tiles[row][col])
                    self.tile_widgets[row][col].show()

                    if (not self.game.already_won) and self.game.tiles[row][col] == 2048:
                        keep_playing = self.won_game()
                        if keep_playing:
                            self.game.already_won = True
                            continue
                        else:
                            self.stop_game()

        self.tiles_to_delete.clear()
        _, _, game_over, _ = self.game.add_random_tile(commit=True)

        if game_over:
            self.game_over()
        else:
            self.centralwidget.grabKeyboard()

    def add_tile(self, row, col, value):

        self.tile_widgets[row][col] = TileWidget(self.game_board, value, row, col)
        self.tile_widgets[row][col].show()

    def game_over(self):

        self.centralwidget.releaseKeyboard()
        self.autoplay_stop()

        game_over_dlg = QtWidgets.QMessageBox(self.centralwidget)
        game_over_dlg.setWindowTitle("Game Over. New Game?")
        game_over_dlg.setText("Game Over.")
        game_over_dlg.setInformativeText("Start New Game?")
        game_over_dlg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        game_over_dlg.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Yes)

        selection = game_over_dlg.exec()

        if selection == QtWidgets.QMessageBox.StandardButton.Yes:
            self.new_game()
        elif selection == QtWidgets.QMessageBox.StandardButton.No:
            self.stop_game()
        else:
            raise ValueError("Invalid selection returned from Game_Over dialog")

    def won_game(self):

        self.centralwidget.releaseKeyboard()
        self.autoplay_stop()

        won_game_dlg = QtWidgets.QMessageBox(self.centralwidget)
        won_game_dlg.setWindowTitle("You Win!!")
        won_game_dlg.setText("You Win!!")
        won_game_dlg.setInformativeText("Continue Playing?")
        won_game_dlg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        won_game_dlg.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Yes)

        selection = won_game_dlg.exec()

        if selection == QtWidgets.QMessageBox.StandardButton.Yes:
            return True
        elif selection == QtWidgets.QMessageBox.StandardButton.Yes:
            return False

    def new_game(self):

        # If a previous game exists, clear previous tiles on board
        if self.game:
            for row in range(SIZE):
                for col in range(SIZE):
                    if self.tile_widgets[row][col]:
                        self.tile_widgets[row][col].hide()
                        self.tile_widgets[row][col].destroy()
                        self.tile_widgets[row][col] = None

        # Tiles
        self.game = GameMgr.Game(self)
        self.current_game = True
        self.is_paused = False
        self.start_button.setText("Pause")
        self.ap_start_button.setEnabled(True)
        self.horizontalSlider.setEnabled(True)

        self.game.add_random_tile(commit=True)
        self.centralwidget.grabKeyboard()  # Enable keyboard events to be processed

    def stop_game(self):

        self.current_game = False
        self.is_paused = True
        self.start_button.setText("New Game")


if __name__ == "__main__":
    import sys
    tile_id = ord("A")-1
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMainWindow(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
