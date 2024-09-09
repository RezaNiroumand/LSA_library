from PySide2 import QtCore, QtWidgets
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtMultimediaWidgets import QVideoWidget

class MouseOverLabel(QtWidgets.QLabel):
    mouseEntered = QtCore.Signal()
    mouseLeft = QtCore.Signal()
    def __init__(self):
        super(MouseOverLabel, self).__init__()
        
    def enterEvent(self, event):
        self.mouseEntered.emit()

    def leaveEvent(self, event):
        self.mouseLeft.emit()

class VideoWidget(QVideoWidget):
    def __init__(self, video_path, parent=None):
        super(VideoWidget, self).__init__(parent)
        self.setMouseTracking(True)

        # Create a media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self)
        
        # Set the media content
        video_url = QtCore.QUrl.fromLocalFile(video_path)
        self.media_player.setMedia(video_url)
        #self.media_player.play()
        self.media_player.pause()
    def enterEvent(self, event):
        # Play the video when the mouse enters the widget
        self.media_player.stop()
        self.media_player.play()

    def leaveEvent(self, event):
        # Stop the video when the mouse leaves the widget
        self.media_player.pause()

class CapitalizedFileSystemModel(QtWidgets.QFileSystemModel):
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                item_name = super(CapitalizedFileSystemModel, self).data(index, role)
                return item_name.capitalize()
        return super(CapitalizedFileSystemModel, self).data(index, role)

class CutLeavesFileSystemModel(CapitalizedFileSystemModel):
    def hasChildren(self, index):
        if not self.isDir(index):
            return False

        # Get the directory path
        dir_path = self.filePath(index)

        # Check if the directory contains any subdirectories
        dir_entries = QtCore.QDir(dir_path).entryInfoList(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot)
        return bool(dir_entries)

class ThreeLevelLimitedFileSystemModel(CutLeavesFileSystemModel):
    def __init__(self,default_depth):
        super(ThreeLevelLimitedFileSystemModel, self).__init__()
        self.val = default_depth
        
    def hasChildren(self, index):
        # Get the depth of the index
        depth = 0
        while index.isValid():
            index = index.parent()
            depth += 1
        # Return False for folders beyond the second level
        if depth > 4+self.val:
            return False

        return super(ThreeLevelLimitedFileSystemModel, self).hasChildren(index)

class CustomTreeView(QtWidgets.QTreeView):
    def __init__(self, *args, **kwargs):
        super(CustomTreeView, self).__init__(*args, **kwargs)

    def drawBranches(self, painter, rect, index):
        if not self.model().hasChildren(index):
            return
        super(CustomTreeView, self).drawBranches(painter, rect, index)

class ListViewLengthCustomDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ListViewLengthCustomDelegate, self).__init__(parent)

    def displayText(self, value, locale):
        # Truncate the file name to 10 characters
        truncated_name = value[:14] + "..." if len(value) > 14 else value
        return truncated_name