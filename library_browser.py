
from PySide2 import QtCore, QtUiTools, QtWidgets, QtGui
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtMultimediaWidgets import QVideoWidget
from maya import OpenMayaUI as omu
from shiboken2 import wrapInstance
import maya.cmds as cmds
import os, time, sys
from LSA_library.modules.custom_widgets import *


ICON_SIZE = QtCore.QSize(64, 64)
mainObject = omu.MQtUtil.mainWindow()
mayaMainWind = wrapInstance(int(mainObject), QtWidgets.QWidget)



class AssetBrowser(QtWidgets.QWidget):
    def __init__(self, parent=mayaMainWind):
        super(AssetBrowser, self).__init__(parent=parent)
        
        if(__name__ == '__main__'):
            self.ui = "D:/Sumesh/VSCode/LSA_library/ui/asset_browser.ui"
            user_file_path = 'D:/Sumesh/VSCode/LSA_library/config/config.txt'
            icons_file_path = 'D:/Sumesh/VSCode/LSA_library/icons/'
        else:
            
            self.ui = os.path.abspath(os.path.dirname(__file__)+"/ui/asset_browser.ui")
            user_file_path = os.path.abspath(os.path.dirname(__file__)+'/config/config.txt')
            icons_file_path = os.path.join(os.path.dirname(__file__)+'/icons/')
        with open(user_file_path, "r") as user_file:
            lines = user_file.readlines()

        self.library_root_path = lines[0].replace("\\", "/")         
        self.path = lines[0].replace("\\", "/")
        self.gallery = True
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('Library Browser')
        self.resize(1300, 925)

        self.setAcceptDrops(True)
        
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(self.ui)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.theMainWidget = loader.load(ui_file)
        ui_file.close()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.theMainWidget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self.orangeFrame = self.findChild(QtWidgets.QFrame, "orange")
        self.hard_pinkFrame = self.findChild(QtWidgets.QFrame, "hard_pink")
        self.red = self.findChild(QtWidgets.QFrame, "red")
        self.size_slider = self.findChild(QtWidgets.QSlider, "size_slider")
        self.list_icon = self.findChild(QtWidgets.QPushButton, "list_icon")
        
        self.list_view_icon = QtGui.QIcon(icons_file_path+'list_icon.png')
        self.thumb_view_icon = QtGui.QIcon(icons_file_path+'thumb_icon.png')
        self.list_icon.setIcon(self.thumb_view_icon)
        
        self.sort = self.findChild(QtWidgets.QPushButton, "sort")
        self.search = self.findChild(QtWidgets.QLineEdit, "search")
        self.lable_root_path = self.findChild(QtWidgets.QLabel, "lable_root_path")
        self.verticalLayout_6 = self.findChild(QtWidgets.QLayout, "verticalLayout_6")
        
        self.preview_lable = MouseOverLabel()
        self.verticalLayout_6.addWidget(self.preview_lable)
        self.preview_lable.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_lable.setText("No Preview")
        self.preview_lable.mouseEntered.connect(self.on_mouse_entered)
        self.preview_lable.mouseLeft.connect(self.on_mouse_left)
    
        self.label_file_name = self.findChild(QtWidgets.QLabel, "label_file_name")
        self.label_type = self.findChild(QtWidgets.QLabel, "label_type")
        self.label_size = self.findChild(QtWidgets.QLabel, "label_size")
        self.label_created_date = self.findChild(QtWidgets.QLabel, "label_created_date")
        self.label_modified_date = self.findChild(QtWidgets.QLabel, "label_modified_date")
        self.plainTextEdit_description = self.findChild(QtWidgets.QPlainTextEdit, "plainTextEdit_description")
        
        
        
        self.lable_root_path.setText(self.path.upper())
        self.search.textChanged.connect(self.new_filter_list_view)        
        self.size_slider.valueChanged.connect(self.update_icon_size)
        
        ### treeViewViewStart
        self.default_depth = self.library_root_path.count('/')-1
        self.treeViewModel = ThreeLevelLimitedFileSystemModel(self.default_depth)
        self.treeViewModel.setRootPath(self.path)
        self.treeViewModel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.treeViewProxyModel = QtCore.QSortFilterProxyModel()
        self.treeViewProxyModel.setSourceModel(self.treeViewModel)
               
        self.treeViewq = QtWidgets.QTreeView()                              
        self.treeViewq.setModel(self.treeViewProxyModel)
        self.treeViewq.setRootIndex(self.treeViewProxyModel.mapFromSource(self.treeViewModel.index(self.path)))        
        self.treeViewq.setAnimated(False)
        self.treeViewq.setIndentation(20)      
        self.treeViewq.setColumnHidden(1, True)
        self.treeViewq.setColumnHidden(2, True)
        self.treeViewq.setColumnHidden(3, True)
        self.treeViewq.setHeaderHidden(True)
        treeView_layout = QtWidgets.QVBoxLayout()
        treeView_layout.addWidget(self.treeViewq)
        self.orangeFrame.setLayout(treeView_layout)
        # Connect the clicked signal to the on_click slot
        self.treeViewq.clicked.connect(self.update_main_list_view) 
        ### treeViewViewEnd  
              
        ### listViewStart                                    
        self.item_icon_provider = QtWidgets.QFileIconProvider()
        file_list = os.listdir(self.path)        
        self.std_model =QtGui.QStandardItemModel()
        for i in file_list:            
            item = QtGui.QStandardItem(i) 
            item.setEditable(False)
            
            if os.path.exists(self.path+'/'+ i + "/previews/"+ i +".jpg"):
                icon_path = self.path+'/'+ i + "/previews/"+ i +".jpg"
            else:
                icon_path = self.path+'/'+ i + "/previews/"+ i +".png"
            
            if ((self.path.replace(self.library_root_path,'')+'/'+i).count('/')) == 4 and not os.path.isfile(self.path+'/'+i):               
                a = QtGui.QPixmap(ICON_SIZE)
                a.load(icon_path)
                item.setIcon(QtGui.QIcon(a))               
            else:
                icon = self.item_icon_provider.icon(QtCore.QFileInfo(self.path+'/'+ i))
                item.setIcon(icon)

            self.std_model.appendRow(item)
        self.mainListView = QtWidgets.QListView()
        self.mainListView.setModel(self.std_model)
        self.mainListView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mainListView.customContextMenuRequested.connect(self.showContextMenu)         
        self.mainListView.setItemDelegate(ListViewLengthCustomDelegate(self))
          
        self.mainListView.setIconSize(QtCore.QSize(100, 100))
        self.mainListView.setViewMode(QtWidgets.QListView.IconMode)
        self.mainListView.setResizeMode(QtWidgets.QListView.Adjust)
        self.mainListView.setMovement(QtWidgets.QListView.Static)        
        self.mainListView.clicked.connect(self.mainListView_item_clicked)
        self.mainListView.doubleClicked.connect(self.mainListView_item_doubleclicked)
        
        list_layout = QtWidgets.QVBoxLayout()
        list_layout.addWidget(self.mainListView)
        list_layout.setContentsMargins(0, 0, 0, 0)
        self.hard_pinkFrame.setLayout(list_layout)
        self.list_icon.clicked.connect(self.change_view)   
        ### listViewEnd        
                       
            

    def on_mouse_entered(self):
        if self.preview_lable.pixmap():  
            if(os.path.exists(os.path.join(os.path.dirname(self.preview_image),'image_sequence'))):
                file_list = []
                image_path = os.path.join(os.path.dirname(self.preview_image),'image_sequence') 
                for filename in os.listdir(image_path):
                    filepath = os.path.join(image_path, filename)  # Construct the full file path
                    if os.path.isfile(filepath):  # Check if the item is a file
                        file_list.append(filepath)  # Add the file path to the list

                self.image_sequence = sorted(file_list, key=lambda x: int(x.split('.')[1]))
                self.timer = QtCore.QTimer()
                self.current_frame = 0
                self.timer.timeout.connect(self.update_frame)
                
                self.timer.start(60)

    def on_mouse_left(self):
        try:
            self.timer.stop()
            del self.timer
        except:
            pass
        if self.preview_lable.pixmap():
            self.pixmap.load(self.preview_image)
            self.preview_lable.setPixmap(self.pixmap.scaled(QtCore.QSize(256, 256), QtCore.Qt.AspectRatioMode.KeepAspectRatio))

    
    
    def showContextMenu(self, pos):
        menu = QtWidgets.QMenu()
        importAction = menu.addAction("Import")
        referenceAction = menu.addAction("Reference")
        globalPos = self.mainListView.mapToGlobal(pos)
        action = menu.exec_(globalPos)
        index = self.mainListView.indexAt(pos)
        item = self.mainListView.model().itemFromIndex(index)
        file_path = self.path+'/'+item.text()
        maya_file_path = file_path+"/scenes/"+ file_path.split('/')[-1] +".ma"
        if action == importAction:
            cmds.file(maya_file_path, i=True)
        if action == referenceAction:
            cmds.file(maya_file_path, r=True, ns=os.path.splitext(os.path.basename(file_path))[0])
    
    def update_frame(self):

        image_path = self.image_sequence[self.current_frame]
        self.pixmap.load(image_path)
        self.preview_lable.setPixmap(self.pixmap.scaled(QtCore.QSize(256, 256), QtCore.Qt.AspectRatioMode.KeepAspectRatio))       
        self.current_frame += 1
        if self.current_frame >= len(self.image_sequence):            
            self.current_frame = 0
        
    
    def load_preview_image(self, image_path):
        try:
            self.verticalLayout_6.removeWidget(self.video_widget)
            self.video_widget.deleteLater()
        except:
            pass                
        if image_path.endswith('.mp4'):

            self.preview_lable.setVisible(False)
            self.video_widget = VideoWidget(image_path)
            self.verticalLayout_6.addWidget(self.video_widget)
        else:
            self.preview_lable.setVisible(True)
            self.pixmap = QtGui.QPixmap(image_path)
            scaled_pixmap = self.pixmap.scaled(256, 256, QtGui.Qt.AspectRatioMode.KeepAspectRatio)
            self.preview_lable.setPixmap(scaled_pixmap)
        self.preview_image = image_path
            
    
    def mainListView_item_doubleclicked(self, index):        
        if self.path.count('/')-self.default_depth>3:
            return
        item = self.mainListView.model().itemFromIndex(index)        
        item_name =item.text()
        base_index = self.treeViewProxyModel.mapFromSource(self.treeViewModel.index(self.path+'/'+item_name))        
        self.treeViewq.expand(base_index)
        self.treeViewq.selectionModel().select(base_index, QtCore.QItemSelectionModel.ClearAndSelect )
        self.update_main_list_view(base_index)
        
    def mainListView_item_clicked(self, index):
        if self.path.count('/')-self.default_depth<=3:
            return        
        self.label_file_name.setText('')
        self.label_type.setText('')
        self.label_size.setText('')
        self.label_created_date.setText('')
        self.label_modified_date.setText('')        
        self.plainTextEdit_description.setPlainText('')                
        item = self.mainListView.model().itemFromIndex(index)
        file_path = self.path+'/'+item.text()
        maya_file_path = file_path+"/scenes/"+ file_path.split('/')[-1] +".ma"
        ti_c = os.path.getctime(maya_file_path)
        ti_m = os.path.getmtime(maya_file_path)
        self.label_file_name.setText(os.path.basename(maya_file_path).capitalize())
        self.label_type.setText(os.path.splitext(os.path.basename(maya_file_path))[1])
        self.label_created_date.setText(time.ctime(ti_c))
        self.label_modified_date.setText(time.ctime(ti_m))

        file_size = os.path.getsize(maya_file_path)
        if(file_size<1048576.0):
            file_size_kb = float(float(file_size) / 1024.0)  
            self.label_size.setText(str(round(file_size_kb,2))+" KB")
        elif(file_size<1073741824.0):
            file_size_mb = float(float(file_size) / 1048576.0) 
            self.label_size.setText(str(round(file_size_mb,2))+" MB")
        else:
            file_size_gb = float(float(file_size) / 1073741824.0) 
            self.label_size.setText(str(round(file_size_gb,2))+" GB")

        if file_path.replace(self.library_root_path,'').count('/') == 4 and not os.path.isfile(file_path):

            if os.path.exists(file_path+"/previews/"+ file_path.split('/')[-1] +".mp4"):
                image_path = file_path+"/previews/"+ file_path.split('/')[-1] +".mp4"
            elif os.path.exists(file_path+"/previews/"+ file_path.split('/')[-1] +".png"):
                image_path = file_path+"/previews/"+ file_path.split('/')[-1] +".png"
            else:
                image_path = file_path+"/previews/"+ file_path.split('/')[-1] +".jpg"

            description_file_path = file_path+"/previews/"+ file_path.split('/')[-1] +".txt"
            if (os.path.exists(description_file_path)):
                with open(description_file_path, "r") as file:
                    file_description = file.read()                
                self.plainTextEdit_description.setPlainText(file_description)
            else:
                self.plainTextEdit_description.setPlainText("")        
            self.load_preview_image(image_path)
    
    
    def update_icon_size(self, value):
        # Update the icon size based on the slider value
        icon_size = QtCore.QSize(value, value)
        self.mainListView.setIconSize(icon_size) 
    
    def update_main_list_view(self, index):
        try:
            self.verticalLayout_6.removeWidget(self.video_widget)
            self.video_widget.deleteLater()
        except:
            pass

        self.preview_lable.setVisible(True)        
        
        self.preview_lable.setText("No Preview")
        self.label_file_name.setText("")
        self.label_type.setText("")
        self.label_created_date.setText("")
        self.label_modified_date.setText("")
        self.label_size.setText("")
        self.plainTextEdit_description.setPlainText("")            
        self.search.clear()
        self.std_model.clear()
        selected_index = self.treeViewProxyModel.mapToSource(index)

        self.path = self.treeViewModel.filePath(selected_index)
        self.lable_root_path.setText(self.path.upper()) 
        file_list = os.listdir(self.path)     
        for i in file_list:            
            item = QtGui.QStandardItem(i) 
            item.setEditable(False)
            if os.path.exists(self.path+'/'+ i + "/previews/"+ i +".jpg"):
                icon_path = self.path+'/'+ i + "/previews/"+ i +".jpg"
            else:
                icon_path = self.path+'/'+ i + "/previews/"+ i +".png"
            if ((self.path.replace(self.library_root_path,'')+'/'+i).count('/')) == 4 and not os.path.isfile(self.path+'/'+i):               
                a = QtGui.QPixmap(ICON_SIZE)
                a.load(icon_path)
                item.setIcon(QtGui.QIcon(a))               
            else:
                icon = self.item_icon_provider.icon(QtCore.QFileInfo(self.path+'/'+ i))
                item.setIcon(icon)

            self.std_model.appendRow(item)
            
    def new_filter_list_view(self):       
        text = self.search.text()
        temp_list = os.listdir(self.path)
        file_list =[]
        for i in temp_list: 
            if text in i:
                file_list.append(i)
        self.std_model.clear()
        for i in file_list:          
            item = QtGui.QStandardItem(i) 
            if os.path.exists(self.path+'/'+ i + "/previews/"+ i +".jpg"):
                icon_path = self.path+'/'+ i + "/previews/"+ i +".jpg"
            else:
                icon_path = self.path+'/'+ i + "/previews/"+ i +".png"
            if ((self.path.replace(self.library_root_path,'')+'/'+i).count('/')) == 4 and not os.path.isfile(self.path+'/'+i):                
                a = QtGui.QPixmap(ICON_SIZE)
                a.load(icon_path)
                item.setIcon(QtGui.QIcon(a))               
            else:
                icon = self.item_icon_provider.icon(QtCore.QFileInfo(self.path+'/'+ i))
                item.setIcon(icon)

            self.std_model.appendRow(item) 
             
    def change_view(self):
        if self.gallery:

            self.list_icon.setIcon(self.list_view_icon)
            self.mainListView.setViewMode(QtWidgets.QListView.ListMode)
            self.mainListView.setIconSize(QtCore.QSize())  # Clear the icon size
            self.mainListView.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
            self.mainListView.setMovement(QtWidgets.QListView.Movement.Static)
            self.mainListView.setTextElideMode(QtCore.Qt.ElideRight)  # Truncate long text with an ellipsis
            self.mainListView.setViewMode(QtWidgets.QListView.ListMode)
            self.size_slider.hide()
            self.mainListView.setItemDelegate(QtWidgets.QStyledItemDelegate())         
            self.gallery = False
        else:

            self.list_icon.setIcon(self.thumb_view_icon)
            self.mainListView.setViewMode(QtWidgets.QListView.IconMode)
            self.mainListView.setIconSize(QtCore.QSize(100, 100))
            self.mainListView.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
            self.mainListView.setMovement(QtWidgets.QListView.Movement.Static)
            self.size_slider.show()
            self.mainListView.setItemDelegate(ListViewLengthCustomDelegate(self))
            self.gallery = True
            self.update_icon_size(self.size_slider.value())
def startUI():
    try:
        UI.close()
    except:
        pass

    UI = AssetBrowser()
    UI.show()
