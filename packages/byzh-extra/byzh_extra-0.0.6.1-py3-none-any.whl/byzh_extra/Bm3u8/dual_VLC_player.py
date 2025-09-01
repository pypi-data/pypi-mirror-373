# https://www.videolan.org/vlc/

import sys
try:
    import vlc
except:
    raise ImportError("[m3u8] 请先安装vlc库: pip install vlc 并且 安装https://www.videolan.org/vlc/")
try:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QPushButton, QVBoxLayout,
        QHBoxLayout, QLineEdit, QLabel, QFrame, QSlider, QSplitter
    )
    from PyQt5.QtCore import Qt
except:
    raise ImportError("[m3u8] 请先安装PyQt5库: pip install PyQt5")


class VLCWidget(QWidget):
    def __init__(self, title="播放器", m3u8="", volume=50):
        super().__init__()
        self.setMinimumSize(400, 500)

        # VLC 初始化
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        self.mediaplayer.audio_set_volume(volume)

        # 控件
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入 .m3u8 链接")
        self.url_input.setText(m3u8)

        self.play_button = QPushButton("播放")
        self.pause_button = QPushButton("暂停")
        self.stop_button = QPushButton("停止")
        self.fullscreen_button = QPushButton("全屏")
        self.status_label = QLabel("状态：就绪")

        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: black;")

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(volume)
        self.volume_slider.setToolTip("音量")
        self.volume_slider.valueChanged.connect(self.set_volume)

        # 布局
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.fullscreen_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"{title}"))
        layout.addWidget(self.url_input)
        layout.addWidget(self.video_frame, stretch=1)
        layout.addLayout(control_layout)
        layout.addWidget(QLabel("音量："))
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # 信号连接
        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        self.stop_button.clicked.connect(self.stop_video)
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)

        self.is_fullscreen = False
        self.fullscreen_window = None

    def set_volume(self, value):
        self.mediaplayer.audio_set_volume(value)

    def play_video(self):
        url = self.url_input.text()
        if not url:
            self.status_label.setText("状态：请输入链接！")
            return

        media = self.instance.media_new(url)
        self.mediaplayer.set_media(media)
        self.set_video_output()
        self.mediaplayer.play()
        self.status_label.setText("状态：播放中")

    def pause_video(self):
        self.mediaplayer.pause()
        self.status_label.setText("状态：暂停")

    def stop_video(self):
        self.mediaplayer.stop()
        self.status_label.setText("状态：停止")

    def set_video_output(self):
        if sys.platform.startswith('linux'):
            self.mediaplayer.set_xwindow(self.video_frame.winId())
        elif sys.platform == "win32":
            self.mediaplayer.set_hwnd(self.video_frame.winId())
        elif sys.platform == "darwin":
            self.mediaplayer.set_nsobject(int(self.video_frame.winId()))

    def toggle_fullscreen(self):
        if not self.is_fullscreen:
            # 创建全屏窗口
            self.video_frame.setParent(None)
            self.fullscreen_window = QWidget()
            self.fullscreen_window.setWindowFlags(Qt.Window)
            self.fullscreen_window.setWindowTitle("全屏播放")
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.video_frame)
            self.fullscreen_window.setLayout(layout)
            self.fullscreen_window.showFullScreen()

            self.set_video_output()
            self.is_fullscreen = True

            # ESC 退出
            self.fullscreen_window.keyPressEvent = self.exit_fullscreen
        else:
            self.exit_fullscreen()

    def exit_fullscreen(self, event=None):
        if event and event.key() != Qt.Key_Escape:
            return

        if self.is_fullscreen:
            self.fullscreen_window.close()
            self.layout().insertWidget(2, self.video_frame, stretch=1)
            self.set_video_output()
            self.is_fullscreen = False


class DualVLCPlayer(QWidget): # 双路 VLC 播放器
    def __init__(self, lm3u8='', rm3u8='', lvolume=50, rvolume=0):
        super().__init__()
        self.setWindowTitle("双路 M3U8 播放器")
        self.setGeometry(100, 100, 1000, 600)

        self.left_player = VLCWidget(title="左播放器", m3u8=lm3u8, volume=lvolume)
        self.right_player = VLCWidget(title="右播放器", m3u8=rm3u8, volume=rvolume)

        # ✨ 使用 QSplitter 替代 QHBoxLayout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_player)
        splitter.addWidget(self.right_player)

        # 设置初始大小比例（可选）
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

class B_DualVLCPlayer:
    def __init__(self, left='', right='', lvolume=50, rvolume=0):
        self.app = QApplication(sys.argv)
        self.player = DualVLCPlayer(lm3u8=left, rm3u8=right, lvolume=lvolume, rvolume=rvolume)

    def play(self):
        self.player.show()
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # player = DualVLCPlayer(
    #     left="http://202.117.115.53:8092/pag/202.117.115.50/7302/009021/0/MAIN/TCP/live.m3u8",
    #     right="http://202.117.115.53:8092/pag/202.117.115.50/7302/009023/0/MAIN/TCP/live.m3u8",
    # )
    # player.show()
    # sys.exit(app.exec_())

    player = B_DualVLCPlayer(
        left="http://202.117.115.53:8092/pag/202.117.115.50/7302/009021/0/MAIN/TCP/live.m3u8",
        right="http://202.117.115.53:8092/pag/202.117.115.50/7302/009023/0/MAIN/TCP/live.m3u8",
    )
    player.play()
