
# Originally Created by: PyQt6 UI code generator 6.1.0
# but heavily edited during further development

"""
This is the main file designed to be run to play the 2048 game on a PC user interface.
"""

from math import modf, log2
from time import ctime
from csv import reader as csvreader
from csv import writer as csvwriter

from PyQt6.QtCore import (Qt, QRect, QMetaObject, QTimer, QCoreApplication,
                          QParallelAnimationGroup, QPropertyAnimation, QPoint,
                          QEasingCurve)
from PyQt6.QtGui import (QKeyEvent, QFont)
from PyQt6.QtWidgets import (QWidget, QLabel, QFrame, QHBoxLayout, QVBoxLayout,
                             QPushButton, QFileDialog, QMessageBox, QSlider,
                             QComboBox, QMenuBar, QStatusBar,
                             QApplication, QMainWindow)

import GameMgr
import AutoPlay
# import pprint

SIZE = 4
BOARD_SIZE_PX = 450
BOARD_MARGIN = 25

# ------------------------------


class CentralWidget(QWidget):
    """
    Custom Subclass of QWidget to handle keyboard-triggered QKeyEvent(s)
    A single instance can receive and process all keyboard events

    ----- Method -----

    - keyPressEvent(QKeyEvent)
    """

    def __init__(self, mainwindow, ui_main):
        super().__init__(mainwindow)     # Establish parent, Initialize parent class
        self.custom_init()
        self.ui_main = ui_main

    def custom_init(self):
        pass

    def keyPressEvent(self, event):
        """Custom callback handler to process key press QKeyEvent(s)"""

        self.releaseKeyboard()

        if not isinstance(event, QKeyEvent):
            raise TypeError("CentralWidget keyPressEvent() event is NOT QKeyEvent() ")

        # Identify Up / Down / Left / Right key presses

        if event.key() == Qt.Key.Key_Up.value:
            valid_move, tile_move_vect, _, _ = self.ui_main.game.move_tiles(0, True)  # '0' means 'Up'

        elif event.key() == Qt.Key.Key_Right.value:
            valid_move, tile_move_vect, _, _ = self.ui_main.game.move_tiles(1, True)  # '1' means 'Right'

        elif event.key() == Qt.Key.Key_Down.value:
            valid_move, tile_move_vect, _, _ = self.ui_main.game.move_tiles(2, True)  # '2' means 'Down'

        elif event.key() == Qt.Key.Key_Left.value:
            valid_move, tile_move_vect, _, _ = self.ui_main.game.move_tiles(3, True)  # '3' means 'Left'

        # If any other key is pressed
        else:
            return

        if valid_move:
            self.ui_main.animate_tiles(tile_move_vect)

        else:   # Invalid move

            # Use add_random_tile() to detect possible game over
            _, num_empty, game_over, _ = self.ui_main.game.add_random_tile(commit=False)

            if game_over:
                self.ui_main.game_over()
            else:   # Game not over, continue
                self.grabKeyboard()

# ------------------------------


class TileWidget(QLabel):
    """Custom object for each tile displayed on the game board

    Subclass of QLabel with additional state for number and background color."""

    tile_colors = ("FFFFC8", "FFE6C8", "FFCC99", "FFCCCC", "FF9999",
                   "CCECFF", "99CCFF", "CCFFFF", "CCFFCC", "CCFF99",
                   "66FF66", "00CCFF", "9999FF", "FF99FF", "FF0066")

    def __init__(self, parent, num, row, col):
        """
        :param parent: "parent" widget (optional) in Qt widget hierarchy
        :param num: number displayed on tile
        :param row: row position in tiles grid. 0 is top row, increasing downwards
        :param col: column position in tiles grid. 0 is top row, increasing downwards"""

        # Call parent QLabel.__init__()
        super().__init__(str(num), parent)

        self.num = num

        self.setGeometry(col*100+25, row*100+25, 100, 100)
        # self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.setStyleSheet("margin: 2px; border: 4px solid grey; border-radius: 5px; " +
                           "background-color: #" + TileWidget.tile_colors[int(log2(self.num)) - 1] +
                           "; font: bold 32px;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(str(self.num))

    def __repr__(self):
        return str(self.num)

    def update_num(self, num):
        """
        Updates the displayed number, font, and color on a tile

        :param num: number to be displayed on tile
        :return: None """

        self.num = num

        if self.num < 10000:
            self.setStyleSheet("margin: 2px; border: 4px solid grey; border-radius: 5px; " +
                               "background-color: #" + TileWidget.tile_colors[int(log2(self.num)) - 1] +
                               "; font: bold 32px;")
        elif self.num > 9999:
            self.setStyleSheet("margin: 2px; border: 4px solid grey; border-radius: 5px; " +
                               "background-color: #" + TileWidget.tile_colors[int(log2(self.num)) - 1] +
                               "; font: bold 24px;")

        self.setText(str(self.num))

# ------------------------------


class UiMain(object):
    """
    The Primary Class of User Interface where most UI state is stored.

    ----- Attributes -----

    MANY. Widgets for each UI element, among others.

    ----- "Main" Functional Methods -----

    - autoplay_start()
    - autoplay_stop()
    - load_tile_widgets(tiles)
    - animate_tiles(vectors)
    - delete_and_new()
    - add_tile(row, col, value)
    - game_over()
    - stop_game()
    - won_game()
    - new_game()
    - retranslate_ui(main_window)

    ----- Callback / Handler Methods -----

    - start_clicked()
    - save_clicked()
    - load_clicked()
    - autoplay_clicked()
    - autoplay_move()
    - ap_speed_changed()
    - ap_type_changed(i)
    """

    def __init__(self, main_window):

        main_window.setObjectName("MainWindow")
        main_window.resize(500, 775)
        self.centralwidget = CentralWidget(main_window, self)      # Custom subclass of QWidget
        self.centralwidget.setObjectName("centralwidget")

        # Game Title
        self.game_title = QLabel(self.centralwidget)
        self.game_title.setGeometry(QRect(180, 10, 121, 61))
        font = QFont()
        font.setPointSize(36)
        font.setBold(True)
        self.game_title.setFont(font)
        self.game_title.setMidLineWidth(0)
        self.game_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.game_title.setObjectName("game_title")

        # Scores Area
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QRect(50, 70, 133, 54))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.curr_score_label = QLabel(self.layoutWidget)
        font = QFont()
        font.setPointSize(12)
        self.curr_score_label.setFont(font)
        self.curr_score_label.setObjectName("curr_score_label")
        self.verticalLayout.addWidget(self.curr_score_label)
        self.curr_score = QLabel(self.layoutWidget)
        font = QFont()
        font.setPointSize(16)
        self.curr_score.setFont(font)
        self.curr_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.curr_score.setObjectName("curr_score")
        self.verticalLayout.addWidget(self.curr_score)
        self.layoutWidget1 = QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QRect(320, 70, 133, 54))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_2 = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.record_score_label = QLabel(self.layoutWidget1)
        font = QFont()
        font.setPointSize(12)
        self.record_score_label.setFont(font)
        self.record_score_label.setObjectName("record_score_label")
        self.verticalLayout_2.addWidget(self.record_score_label)
        self.record_score = QLabel(self.layoutWidget1)
        font = QFont()
        font.setPointSize(16)
        self.record_score.setFont(font)
        self.record_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.record_score.setObjectName("record_score")
        self.verticalLayout_2.addWidget(self.record_score)

        # Game Board
        self.game_board = QFrame(self.centralwidget)
        self.game_board.setGeometry(QRect(25, 130, 450, 450))
        self.game_board.setFrameStyle(QFrame.Shape.StyledPanel.value)
        self.game_board.setAutoFillBackground(True)
        self.game_board.setObjectName("game_board")

        # Start
        self.start_button = QPushButton(self.centralwidget)
        self.start_button.setGeometry(QRect(20, 610, 100, 100))
        font = QFont()
        font.setPointSize(12)
        self.start_button.setFont(font)
        self.start_button.setObjectName("start_button")
        self.start_button.clicked.connect(self.start_clicked)

        # Save
        self.save_button = QPushButton(self.centralwidget)
        self.save_button.setEnabled(False)
        self.save_button.setGeometry(QRect(140, 620, 100, 30))
        font = QFont()
        font.setPointSize(12)
        self.save_button.setFont(font)
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self.save_clicked)

        self.save_dlg = QFileDialog(self.centralwidget, caption="Save As")
        self.save_dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        self.save_dlg.setFileMode(QFileDialog.FileMode.AnyFile)
        self.save_dlg.setNameFilter("CSV Files (*.csv)")
        self.save_dlg.setViewMode(QFileDialog.ViewMode.Detail)

        # Load
        self.load_button = QPushButton(self.centralwidget)
        self.load_button.setGeometry(QRect(140, 670, 100, 30))
        font = QFont()
        font.setPointSize(12)
        self.load_button.setFont(font)
        self.load_button.setObjectName("load_button")
        self.load_button.clicked.connect(self.load_clicked)
        self.load_button.setEnabled(True)

        self.load_dlg = QFileDialog(self.centralwidget, caption="Open File")
        self.load_dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        self.load_dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.load_dlg.setNameFilters(["CSV Files (*.csv)", "Text Files (*.txt)"])
        self.load_dlg.setViewMode(QFileDialog.ViewMode.Detail)

        self.loadfile_err_dlg = QMessageBox(self.centralwidget)
        self.loadfile_err_dlg.setWindowTitle("Error")
        self.loadfile_err_dlg.setText("Error Detected in File. Cannot load.")
        self.loadfile_err_dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.loadfile_err_dlg.setDefaultButton(QMessageBox.StandardButton.Yes)

        self.line = QFrame(self.centralwidget)
        self.line.setGeometry(QRect(240, 600, 20, 131))
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setObjectName("line")

        # Auto-Play Area
        self.ap_area_widget = QWidget(self.centralwidget)
        self.ap_area_widget.setGeometry(QRect(260, 600, 211, 150))
        self.ap_area_widget.setObjectName("widget")
        self.verticalLayout_3 = QVBoxLayout(self.ap_area_widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.ap_spd_label = QLabel(self.ap_area_widget)
        self.ap_spd_label.setEnabled(False)
        font = QFont()
        font.setPointSize(10)

        # Autoplay Speed Slider
        self.ap_spd_label.setFont(font)
        self.ap_spd_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ap_spd_label.setObjectName("ap_spd_label")
        self.verticalLayout_3.addWidget(self.ap_spd_label)
        self.horizontalSlider = QSlider(self.ap_area_widget)
        self.horizontalSlider.setEnabled(False)
        self.horizontalSlider.setMinimum(100)
        self.horizontalSlider.setMaximum(3000)
        self.horizontalSlider.setPageStep(5)
        self.horizontalSlider.setSingleStep(50)
        self.horizontalSlider.setPageStep(1000)
        self.horizontalSlider.setTickInterval(200)
        self.horizontalSlider.setInvertedAppearance(True)
        self.horizontalSlider.setInvertedControls(True)
        self.horizontalSlider.setValue(1000)
        self.horizontalSlider.valueChanged.connect(self.ap_speed_changed)
        self.horizontalSlider.setOrientation(Qt.Orientation.Horizontal)
        self.horizontalSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.horizontalSlider.setTickInterval(5)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.verticalLayout_3.addWidget(self.horizontalSlider)

        # Autoplay Strategy ComboBox
        self.ap_strat_label = QLabel(self.ap_area_widget)
        self.ap_strat_label.setEnabled(False)
        font = QFont()
        font.setPointSize(10)
        self.ap_strat_label.setFont(font)
        self.ap_strat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ap_strat_label.setObjectName("ap_strat_label")
        self.verticalLayout_3.addWidget(self.ap_strat_label)

        self.comboBox = QComboBox(self.ap_area_widget)
        self.comboBox.addItems(["Most Blank Tiles", "Maximize Upper Right Chain",
                                "Any Corner Chain + Blanks", "Aligned Corner Chains Only"])
        self.comboBox.currentIndexChanged.connect(self.ap_type_changed)
        self.comboBox.setEnabled(True)
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout_3.addWidget(self.comboBox)

        # AutoPlay Start Button
        self.ap_start_button = QPushButton(self.ap_area_widget)
        self.ap_start_button.setEnabled(False)
        font = QFont()
        font.setFamily("Tahoma")
        font.setPointSize(12)
        self.ap_start_button.setFont(font)
        self.ap_start_button.setObjectName("ap_start_button")
        self.ap_start_button.clicked.connect(self.autoplay_clicked)
        self.verticalLayout_3.addWidget(self.ap_start_button)

        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(main_window)
        self.menubar.setGeometry(QRect(0, 0, 499, 22))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        # for enabling multi-language support
        self.retranslate_ui(main_window)
        QMetaObject.connectSlotsByName(main_window)

        # State variables
        self.game = None
        self.current_game = False
        self.is_paused = True

        self.tile_widgets = [[None] * SIZE for _ in range(SIZE)]
        self.next_tile_widgets = [[None] * SIZE for _ in range(SIZE)]
        self.tiles_to_delete = []

        self.anim_group = None
        self.anim_duration = 100

        # Setup for Auto-Play function
        self.ap_type = 0
        self.autoplayer = None
        self.autoplaying = False
        self.autoplay_speed = 1.0

        # QTimer to trigger "autoplay_move()" on interval
        self.autoplay_timer = QTimer(self.centralwidget)
        self.autoplay_timer.setInterval(1000)
        self.autoplay_timer.setSingleShot(False)
        self.autoplay_timer.setTimerType(Qt.TimerType.CoarseTimer)
        self.autoplay_timer.timeout.connect(self.autoplay_move)

    def retranslate_ui(self, main_window):
        """Enables all text fields to be translated into other languages"""

        _translate = QCoreApplication.translate
        main_window.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.game_title.setText(_translate("MainWindow", "2048"))
        self.start_button.setText(_translate("MainWindow", "Start"))
        self.save_button.setText(_translate("MainWindow", "Save Game"))
        self.load_button.setText(_translate("MainWindow", "Load Game"))
        self.curr_score_label.setText(_translate("MainWindow", "Current Score"))
        self.curr_score.setText(_translate("MainWindow", "0"))
        self.record_score_label.setText(_translate("MainWindow", "Record High Score"))
        self.record_score.setText(_translate("MainWindow", "0"))
        self.ap_spd_label.setText(_translate("MainWindow", "Slow   --   Auto-Play Speed   --   Fast"))
        self.ap_strat_label.setText(_translate("MainWindow", "Auto-Play Strategy"))
        self.ap_start_button.setText(_translate("MainWindow", "Start Auto-Play"))

    def start_clicked(self):
        """Handler auto-called when Start/Play/Pause button is clicked"""

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
                self.ap_spd_label.setEnabled(True)
                self.ap_strat_label.setEnabled(True)
                self.load_button.setEnabled(False)
                self.save_button.setEnabled(False)

            else:               # User clicked "Pause"
                if self.autoplaying:
                    self.autoplay_stop()
                self.is_paused = True
                self.centralwidget.releaseKeyboard()
                self.start_button.setText("Play")
                self.ap_start_button.setEnabled(False)
                self.horizontalSlider.setEnabled(False)
                self.ap_spd_label.setEnabled(False)
                self.ap_strat_label.setEnabled(False)
                self.load_button.setEnabled(True)
                self.save_button.setEnabled(True)
                self.anim_duration = 100


    def save_clicked(self):
        """Handler auto-called when Save button is clicked"""

        accepted = self.save_dlg.exec()
        if not accepted:
            return

        save_filename = self.save_dlg.selectedFiles()

        # DEBUG
        for str1 in save_filename:
            print(str1)

        # Read saved game data from file
        with open(save_filename[0], mode="w", newline='') as file1:
            csv_writer = csvwriter(file1, dialect="excel", delimiter=",")
            csv_writer.writerow([self.game.score, self.game.num_moves,
                                 self.game.num_empty, self.game.already_won,
                                 self.game.game_over])
            for i in range(4):
                csv_writer.writerow([self.game.tiles[i][j] for j in range(4)])
            csv_writer.writerow([ctime()])

    def load_clicked(self):
        """Handler auto-called when Load button is clicked"""

        # Warning Dialog
        if self.current_game:
            losegame_err_dlg = QMessageBox(self.centralwidget)
            losegame_err_dlg.setWindowTitle("Warning")
            losegame_err_dlg.setText("Current Game in progress will be lost.")
            losegame_err_dlg.setInformativeText("Are you sure you want to load a saved game?")
            losegame_err_dlg.setStandardButtons(QMessageBox.StandardButton.Yes |
                                                QMessageBox.StandardButton.No)
            losegame_err_dlg.setDefaultButton(QMessageBox.StandardButton.No)
            response = losegame_err_dlg.exec()
            if response == QMessageBox.StandardButton.No:
                return

        accepted = self.load_dlg.exec()
        if not accepted:
            return

        load_filename = self.load_dlg.selectedFiles()

        # DEBUG
        for str1 in load_filename:
            print(str1)

        # Read saved game data from file
        with open(load_filename[0], mode="r") as file1:
            csv_reader = csvreader(file1, dialect="excel", delimiter=",")
            [score, num_moves, num_empty, already_won, game_over] = next(csv_reader)  # Collect header row
            tiles = []
            for _ in range(4):
                tiles.append([int(i) for i in next(csv_reader)])

        # Error checking of file
        try:
            score = int(score)
            num_moves = int(num_moves)
            num_empty = int(num_empty)
            already_won = bool(already_won)
            game_over = bool(game_over)

        except Exception as e:
            self.loadfile_err_dlg.exec()
            return

        game_state_error = any([score < 0, num_moves < 1, num_empty > 15, num_empty < 2])
        tiles_error = False
        for row in range(4):
            for col in range(4):
                if tiles[row][col] == 0:
                    continue

                frac, _ = modf(log2(tiles[row][col]))
                if tiles[row][col] < 0 or frac != 0.0:
                    tiles_error = True

        if game_state_error or tiles_error:
            self.loadfile_err_dlg.exec()
            return

        self.game = GameMgr.Game(self, tiles, score, num_moves)
        self.game.num_empty = num_empty
        self.game.already_won = already_won
        self.game.game_over = game_over

        self.load_tile_widgets(tiles)

        self.current_game = True

    def load_tile_widgets(self, tiles):
        """During loading of a saved game, updates the game board TileWidgets displayed"""

        for row in range(SIZE):
            for col in range(SIZE):

                if tiles[row][col] == 0:
                    if self.tile_widgets[row][col]:
                        self.tile_widgets[row][col].hide()
                        self.tile_widgets[row][col].destroy()
                    continue

                elif tiles[row][col] > 0:
                    if self.tile_widgets[row][col]:
                        self.tile_widgets[row][col].update_num(tiles[row][col])
                        self.tile_widgets[row][col].show()
                    else:
                        self.tile_widgets[row][col] = TileWidget(self.game_board, tiles[row][col], row, col)
                        self.tile_widgets[row][col].show()

    def ap_speed_changed(self):
        """Handler auto-called when AutoPlay speed slider is changed"""

        self.autoplay_timer.stop()

        value = self.horizontalSlider.value()
        self.autoplay_timer.setInterval(value)

        if value/4 > 100:
            self.anim_duration = 100
        else:
            self.anim_duration = int(value / 4)

        if self.autoplaying:
            self.autoplay_timer.start()

    def ap_type_changed(self, i):
        """Handler auto-called when AutoPlay strategy ComboBox option is changed

        :param i: index of selection in ComboBox automatically passed"""

        self.ap_type = int(i)

    def autoplay_clicked(self):
        """Handler auto-called when AutoPlay button is clicked"""

        # If autoplay is currently paused, start AutoPlay
        if self.autoplaying is False:
            self.autoplay_start()
            return

        # If AutoPlay is active, Pause it.
        else:
            self.autoplay_stop()

    def autoplay_start(self):
        """Update game state to start AutoPlay after AutoPlay button press"""

        self.centralwidget.releaseKeyboard()
        self.comboBox.setEnabled(False)
        self.ap_strat_label.setEnabled(False)
        self.ap_speed_changed()     # Update speed (specifically anim_duration)
        # self.load_button.setEnabled(False)
        # self.save_button.setEnabled(False)

        self.autoplayer = AutoPlay.AutoPlayer(self.game, calc_option=self.ap_type)

        self.autoplaying = True
        self.ap_start_button.setText("Pause AutoPlay")
        self.autoplay_timer.start()

    def autoplay_stop(self):
        """Update game state to stop AutoPlay after AutoPlay button press"""

        self.autoplay_timer.stop()
        self.autoplaying = False
        self.ap_strat_label.setEnabled(True)
        self.comboBox.setEnabled(True)
        self.anim_duration = 100
        # self.load_button.setEnabled(False)
        # self.save_button.setEnabled(True)
        self.ap_start_button.setText("Start AutoPlay")
        self.centralwidget.grabKeyboard()

    def autoplay_move(self):
        """Called by AutoPlay QTimer timeout to initiate an automatic move"""

        # Calculate "best" move using chosen strategy
        move_dir = self.autoplayer.get_move()

        valid_move, tile_move_vect, _, _ = self.game.move_tiles(move_dir, True)

        self.animate_tiles(tile_move_vect)

    def animate_tiles(self, vectors):
        """Visually moves tiles according to the result of GameMgr.Game.move_tiles()
        Automatically calls delete_and_new() upon completion of animation

        :param vectors: Array of vectors describing correct movement of each tile"""

        self.anim_group = QParallelAnimationGroup()
        anims = []

        # By Row
        for row in range(SIZE):
            for col in range(SIZE):
                if vectors[row][col][0] or vectors[row][col][1]:

                    end_x = self.tile_widgets[row][col].x() + 100 * vectors[row][col][0]
                    end_y = self.tile_widgets[row][col].y() + 100 * vectors[row][col][1]
                    anims.append(QPropertyAnimation(self.tile_widgets[row][col], b"pos"))
                    anims[-1].setStartValue(self.tile_widgets[row][col].pos())
                    anims[-1].setEndValue(QPoint(end_x, end_y))
                    anims[-1].setDuration(self.anim_duration)
                    anims[-1].setEasingCurve(QEasingCurve.Type.Linear)
                    self.anim_group.addAnimation(anims[-1])

        # Upon animation finished, automatically call delete_and_new()
        self.anim_group.finished.connect(self.delete_and_new)

        # Must not trigger another move while animation in progress
        self.autoplay_timer.stop()

        self.anim_group.start()

    def delete_and_new(self):
        """Removes merged (deleted) tiles from display, and updates displayed numbers
        Automatically called by animate_tiles()"""

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
        """Creates a new TileWidget for display on game_board.
        Called by GameMgr.Game.add_random_tile()"""

        self.tile_widgets[row][col] = TileWidget(self.game_board, value, row, col)
        self.tile_widgets[row][col].show()

    def game_over(self):
        """Updates game state upon game over with dialog to ask user for next action"""

        self.centralwidget.releaseKeyboard()
        self.autoplay_stop()

        game_over_dlg = QMessageBox(self.centralwidget)
        game_over_dlg.setWindowTitle("Game Over. New Game?")
        game_over_dlg.setText("Game Over.")
        game_over_dlg.setInformativeText("Start New Game?")
        game_over_dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        game_over_dlg.setDefaultButton(QMessageBox.StandardButton.Yes)

        selection = game_over_dlg.exec()

        if selection == QMessageBox.StandardButton.Yes:
            self.new_game()
        elif selection == QMessageBox.StandardButton.No:
            self.stop_game()
        else:
            raise ValueError("Invalid selection returned from Game_Over dialog")

    def stop_game(self):
        """Ends game upon user selection after win or game over."""

        self.current_game = False
        self.is_paused = True
        self.start_button.setText("New Game")
        self.load_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.ap_spd_label.setEnabled(False)
        self.ap_strat_label.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.horizontalSlider.setEnabled(False)

    def won_game(self):
        """Updates UI state upon game win with dialog to ask user for next action

        :returns: bool. True if user wants to continue playing, False otherwise"""

        self.centralwidget.releaseKeyboard()
        self.autoplay_stop()

        won_game_dlg = QMessageBox(self.centralwidget)
        won_game_dlg.setWindowTitle("You Win!!")
        won_game_dlg.setText("You Win!!")
        won_game_dlg.setInformativeText("Continue Playing?")
        won_game_dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        won_game_dlg.setDefaultButton(QMessageBox.StandardButton.Yes)

        selection = won_game_dlg.exec()

        if selection == QMessageBox.StandardButton.Yes:
            return True
        elif selection == QMessageBox.StandardButton.Yes:
            return False

    def new_game(self):
        """Sets all needed UI and Game state for new game."""

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
        self.ap_spd_label.setEnabled(True)
        self.ap_strat_label.setEnabled(True)
        self.load_button.setEnabled(False)
        self.save_button.setEnabled(False)

        self.game.add_random_tile(commit=True)
        self.centralwidget.grabKeyboard()  # Enable keyboard events to be processed


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = UiMain(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
