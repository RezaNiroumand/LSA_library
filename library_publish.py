from PySide2 import QtCore, QtUiTools, QtWidgets, QtGui
from maya import OpenMayaUI as omu
from shiboken2 import wrapInstance
import maya.cmds as cmds
import os, shutil, re, sys
import getpass
import glob
import maya.mel as mel
SCRIPT_FILE_PATH = 'N:/pipeline/Tools/Maya/scripts/comm/LSA_library/'
# SCRIPT_FILE_PATH = 'D:/Sumesh/VSCode/LSA_library/'
#print("local")
mainObject = omu.MQtUtil.mainWindow()
mayaMainWind = wrapInstance(int(mainObject), QtWidgets.QWidget)
class AssetPublish(QtWidgets.QWidget):    
    
    def __init__(self,parent=mayaMainWind):
        
        super(AssetPublish, self).__init__(parent=parent)
        
        if(__name__ == '__main__'):
            user_file_path = SCRIPT_FILE_PATH+'config/config.txt'
            self.instruction_file_path = SCRIPT_FILE_PATH+'doc/library_publish.pdf'
        else:
            user_file_path = os.path.abspath(os.path.dirname(__file__)+'/config/config.txt')
            self.instruction_file_path = os.path.abspath(os.path.dirname(__file__)+'/doc/library_publish.pdf')

        with open(user_file_path, "r") as user_file:
            lines = user_file.readlines()
                
        #create main folders if they aren't already there
        if not (os.path.exists(lines[0])):
            os.makedirs(lines[0])
                   
        if(__name__ == '__main__'):
            self.ui = SCRIPT_FILE_PATH+"ui/asset_publish.ui"
        else:
            self.ui = os.path.abspath(os.path.dirname(__file__)+'/ui/asset_publish.ui')
        
        self.setAcceptDrops(True)        
        self.asset_library_root_path = lines[0]
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('Library Publish')
        self.setFixedSize(450,300)                
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(self.ui)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.theMainWidget = loader.load(ui_file)
        ui_file.close()
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.theMainWidget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self.pushButton_add_asset_group = self.findChild(QtWidgets.QPushButton, "pushButton_add_group")
        self.pushButton_add_asset_type = self.findChild(QtWidgets.QPushButton, "pushButton_add_asset_type")
        self.pushButton_take_screen_shot = self.findChild(QtWidgets.QPushButton, "pushButton_take_screen_shot")
        self.pushButton_save_textures = self.findChild(QtWidgets.QPushButton, "pushButton_save_textures")
        
        self.comboBox_asset_group = self.findChild(QtWidgets.QComboBox, "comboBox_group")
        self.comboBox_add_type = self.findChild(QtWidgets.QComboBox, "comboBox_asset_type")
        
        self.lineEdit_asset_name = self.findChild(QtWidgets.QLineEdit, "lineEdit_asset_name")
        self.lineEdit_asset_name.setText(os.path.splitext(os.path.basename(cmds.file(q=True, sceneName=True)))[0])
        
        self.plainTextEdit_description = self.findChild(QtWidgets.QPlainTextEdit, "plainTextEdit_description")
        
        self.actionAdd_User = self.theMainWidget.findChild(QtWidgets.QAction, 'actionAdd_User')
        self.actionAdd_User.triggered.connect(self.addUser)
        
        self.actionRemove_User = self.theMainWidget.findChild(QtWidgets.QAction, 'actionRemove_User')
        self.actionRemove_User.triggered.connect(self.removeUser)
        
        self.actionInstructions = self.theMainWidget.findChild(QtWidgets.QAction, 'actionInstructions')
        self.actionInstructions.triggered.connect(self.action_Instructions)
        
        
        self.comboBox_asset_group.currentIndexChanged.connect(self.load_asset_Types)
        self.pushButton_add_asset_group.clicked.connect(self.enter_asset_group_dialog)
        self.pushButton_add_asset_type.clicked.connect(self.enter_asset_type_dialog)
        self.pushButton_take_screen_shot.clicked.connect(self.thumbnail_switch)
        self.pushButton_save_textures.clicked.connect(self.save_swtich)

        self.loadasset_group()
    
    def action_Instructions(self):
        os.startfile(self.instruction_file_path)
    
    def check_form_is_filled(self):
        if(self.comboBox_asset_group.currentIndex()==-1):
            cmds.confirmDialog( title='Warning', message='Select an Asset Group!')
            return False
        if(self.comboBox_add_type.currentIndex()==-1):
            cmds.confirmDialog( title='Warning', message='Select an Asset Type!')
            return False
        if(self.lineEdit_asset_name.text()==''):
            cmds.confirmDialog( title='Warning', message='Type an Asset Name!')
            return False
        if not re.match(r'^[a-zA-Z]', self.lineEdit_asset_name.text()):
            cmds.confirmDialog( title='Warning', message='Asset Name Should Starts With Letter!')
            return False
        else:
            return True

    def addUser(self):       
        result = cmds.promptDialog(title='New User LSID', message='New User LSID:', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
        if result == 'OK':
            new_user_LSID = cmds.promptDialog(query=True, text=True).lower()
            if(__name__ == '__main__'):
                user_file_path = SCRIPT_FILE_PATH+'config/user.txt'
            else:
                user_file_path = os.path.abspath(os.path.dirname(__file__)+'/config/user.txt')
            if (new_user_LSID.startswith('ls') and new_user_LSID.replace('ls','').isdigit() and len(new_user_LSID)==6):
                with open(user_file_path, "r") as user_file:
                    lines = user_file.readlines()
                    if(new_user_LSID+'\n') not in lines:
                        with open(user_file_path, "a") as user_file:
                            user_file.write(new_user_LSID+'\n')
                    else:
                        cmds.confirmDialog( title='Warning', message='Use Already Exists!')
            else:
                cmds.confirmDialog( title='Warning', message='Wrong User Name!')
    
    def removeUser(self):       
        result = cmds.promptDialog(title='Remove User LSID', message='Remove User LSID:', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
        if result == 'OK':
            to_remove_user_LSID = cmds.promptDialog(query=True, text=True).lower()
            if(__name__ == '__main__'):
                user_file_path = SCRIPT_FILE_PATH+'config/user.txt'
            else:
                user_file_path = os.path.abspath(os.path.dirname(__file__)+'/config/user.txt')
            with open(user_file_path, "r") as user_file:
                lines = user_file.readlines()
            if (to_remove_user_LSID.lower()+'\n') in lines:
                with open(user_file_path, "w") as user_file:
                    for line in lines:
                        if line.strip().lower() != to_remove_user_LSID.lower():
                            user_file.write(line)
            else:
                cmds.confirmDialog( title='Warning', message='User Not Exists!')
        
    
    def loadasset_group(self):       
        asset_group_names = next(os.walk(self.asset_library_root_path))[1]
        self.comboBox_asset_group.clear()
        self.comboBox_asset_group.addItems(asset_group_names)        
 
    
    def load_asset_Types(self):
        current_asset_group_path = self.asset_library_root_path+'/'+self.comboBox_asset_group.currentText()
        asset_type_name = next(os.walk(current_asset_group_path))[1]
        self.comboBox_add_type.clear()
        self.comboBox_add_type.addItems(asset_type_name)
    
    
    def saveTextures(self):
        if(self.check_form_is_filled()):
            project_path = cmds.workspace( q=True, act=True)
                   
            file_nodes = cmds.ls(type = ('file'))
            if cmds.pluginInfo( 'mtoa.mll', query=True, loaded=True ):
                ai_nodes = cmds.ls(type = ('aiImage'))
                file_nodes.extend(ai_nodes)

            textures_to_copy = []
            for item in file_nodes:
                if cmds.objectType(item)=='file':
                    texture = cmds.getAttr(item+'.fileTextureName')
                else:
                    texture = cmds.getAttr(item+'.filename')    
                if os.path.exists(texture):
                    textures_to_copy.append(texture)
                elif os.path.exists(project_path+'/'+texture):
                    textures_to_copy.append(texture)
                else:
                    cmds.confirmDialog( title='Warning', message='Missing textures, If there is a relative texture path, you should set the appropriate Maya project!')
                    textures_to_copy = []
                    break
            if  textures_to_copy:  
                print("save_textures.....")
                print(self.lineEdit_asset_name.text().capitalize())
                self.alphabetic_folder = self.lineEdit_asset_name.text().capitalize()[0]
                self.file_name_folder = self.lineEdit_asset_name.text().capitalize().rsplit('.', 1)[0]
                print(self.alphabetic_folder)
                self.sourceimages_folder = os.path.join(self.asset_library_root_path.replace("/", "\\"), self.comboBox_asset_group.currentText(), self.comboBox_add_type.currentText(), self.alphabetic_folder, self.file_name_folder, 'sourceimages')
                if not os.path.exists(self.sourceimages_folder):
                    os.makedirs(self.sourceimages_folder)
            
                for item in textures_to_copy:
                    print(item)
                    shutil.copy(item, self.sourceimages_folder)        

                for item in file_nodes:
                    if cmds.objectType(item)=='file':
                        texture = cmds.getAttr(item+'.fileTextureName')
                        cmds.setAttr(item + ".fileTextureName", os.path.join(self.sourceimages_folder,os.path.basename(texture)), type="string")                
                    else:
                        texture = cmds.getAttr(item+'.filename')
                        cmds.setAttr(item + ".filename", os.path.join(self.sourceimages_folder,os.path.basename(texture)), type="string")
    
    def screenShot(self):
        if(self.check_form_is_filled()):
            self.asset_file_folder = os.path.join(self.asset_library_root_path, self.comboBox_asset_group.currentText() ,self.comboBox_add_type.currentText())
            self.asset_file_name = self.lineEdit_asset_name.text().capitalize()+".ma"
            self.full_file_path = self.asset_file_folder + "/" + self.asset_file_name
            print(self.full_file_path)
            if(os.path.exists(self.full_file_path)):
                result = cmds.confirmDialog( title='Confirm', message='The file already exists. Do you want to overwrite it?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
                if (result == 'Yes'):
                    mel.eval('thumbnailCaptureComponent -capture -fdc "start_save;";proc start_save(){python("AssetPublish().saveFile(UI)");}')
                else:
                    return
            else:
                mel.eval('thumbnailCaptureComponent -capture -fdc "start_save;";proc start_save(){python("AssetPublish().saveFile(UI)");}')    

    @staticmethod
    def saveFile(self ): 
        
        print("save_file.....")
        print(self.lineEdit_asset_name.text().capitalize())
        self.alphabetic_folder = self.lineEdit_asset_name.text().capitalize()[0]
        self.file_name_folder = self.lineEdit_asset_name.text().capitalize().rsplit('.', 1)[0]
        print(self.alphabetic_folder)
        self.icon_name = self.lineEdit_asset_name.text().capitalize()+".png"       
        print(self.icon_name)
        
        self.icon_folder = os.path.join(self.asset_library_root_path.replace("/", "\\"), self.comboBox_asset_group.currentText(), self.comboBox_add_type.currentText(), self.alphabetic_folder, self.file_name_folder, 'previews')
        print(self.icon_folder)
        if not os.path.exists(self.icon_folder):
            os.makedirs(self.icon_folder)
        icon_path = os.path.join(self.icon_folder, self.icon_name)
        print(icon_path)   
        print("save_thumbnail.....")
        cmds.thumbnailCaptureComponent(save=icon_path)
        sequence_path = os.path.join(self.icon_folder, '.mayaSwatches', self.icon_name)
        # make image_sequence
        if(os.path.exists(sequence_path)):        
            preview_sequence_list = []
            for filename in os.listdir(sequence_path):
                filepath = os.path.join(sequence_path, filename)  
                if os.path.isfile(filepath):  
                    preview_sequence_list.append(filepath)  
            print(preview_sequence_list)
            for filename in os.listdir(sequence_path):
                if filename.endswith('.preview'):
                    old_filepath = os.path.join(sequence_path, filename)
                    new_filepath = os.path.join(sequence_path, filename[:-8].replace('.png','') + '.png')
                    os.rename(old_filepath, new_filepath)
            shutil.copytree(sequence_path, self.icon_folder+'/image_sequence')
            shutil.rmtree(sequence_path)
        # make icon
        print("swatch saved")
        swatch_path = os.path.join(self.icon_folder, ".mayaSwatches", self.icon_name+".swatch")
        print("save")
        print(swatch_path) 
        tif_swatch_path = os.path.splitext(swatch_path)[0]
        os.rename(swatch_path, tif_swatch_path)
        print("rename")
        print(swatch_path)
        print(tif_swatch_path)
        shutil.copy(tif_swatch_path, self.icon_folder)
        
        shutil.rmtree(os.path.join(self.icon_folder, ".mayaSwatches"))
        
        #save_file        
        self.asset_file_folder = os.path.join(self.asset_library_root_path, self.comboBox_asset_group.currentText() ,self.comboBox_add_type.currentText(),self.alphabetic_folder, self.file_name_folder, 'scenes')
        print(self.asset_file_folder)
        self.asset_file_name = self.lineEdit_asset_name.text().capitalize()+".ma"
        print(self.asset_file_name)
        full_file_path = os.path.join(self.asset_file_folder, self.asset_file_name)
        print(full_file_path)
        if not os.path.exists(self.asset_file_folder):
            os.makedirs(self.asset_file_folder)
        
        cmds.file(rename=full_file_path)
        cmds.file(save=True, type="mayaAscii")
        
        description_file_path = os.path.join(self.icon_folder, self.icon_name.replace(".png", ".txt"))
        print(description_file_path)
        if not (self.plainTextEdit_description.toPlainText()==""):
            with open(description_file_path, "w") as file:
                file.write(self.plainTextEdit_description.toPlainText())        
          
    def enter_asset_group_dialog(self):        
        result = cmds.promptDialog(title='Asset Group Name', message='Asset Group Name:', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
        if result == 'OK':
            asset_group_name = cmds.promptDialog(query=True, text=True).capitalize()
            new_folder = os.path.join(self.asset_library_root_path, asset_group_name)
            if not os.path.exists(new_folder):
                os.makedirs(new_folder)
                self.loadasset_group()
                self.comboBox_asset_group.setCurrentText(asset_group_name)
            else:
                cmds.confirmDialog( title='Warning', message='This Asset Group Already Exists!')
  
    def enter_asset_type_dialog(self):
        if(self.comboBox_asset_group.currentIndex()==-1):
            cmds.confirmDialog( title='Warning', message='Select a Asset Group!')
            return 
        result = cmds.promptDialog(title='Asset Type Name', message='Asset Type Name:', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
        if result == 'OK':
            asset_type_name = cmds.promptDialog(query=True, text=True).capitalize()     
            new_folder = os.path.join(self.asset_library_root_path, self.comboBox_asset_group.currentText() , asset_type_name)
            print(new_folder)
            if not os.path.exists(new_folder):
                os.makedirs(new_folder)
                self.load_asset_Types()
                self.comboBox_add_type.setCurrentText(asset_type_name)
            else:
                cmds.confirmDialog( title='Warning', message='This Asset Type Already Exists!')

    def seq_to_glob(self,path):
        """Takes an image sequence path and returns it in glob format,
        with the frame number replaced by a '*'.
        Image sequences may be numerical sequences, e.g. /path/to/file.1001.exr
        will return as /path/to/file.*.exr.
        Image sequences may also use tokens to denote sequences, e.g.
        /path/to/texture.<UDIM>.tif will return as /path/to/texture.*.tif.
        Args:
            path (str): the image sequence path
        Returns:
            str: Return glob string that matches the filename pattern.
        """

        if path is None:
            return path

        # If any of the patterns, convert the pattern
        patterns = {
            "<udim>": "<udim>",
            "<tile>": "<tile>",
            "<uvtile>": "<uvtile>",
            "#": "#",
            "u<u>_v<v>": "<u>|<v>",
            "<frame0": "<frame0\d+>",
            "<f>": "<f>"
        }

        lower = path.lower()
        has_pattern = False
        for pattern, regex_pattern in patterns.items():
            if pattern in lower:
                path = re.sub(regex_pattern, "*", path, flags=re.IGNORECASE)
                has_pattern = True

        if has_pattern:
            return path

        base = os.path.basename(path)
        matches = list(re.finditer(r'\d+', base))
        if matches:
            match = matches[-1]
            new_base = '{0}*{1}'.format(base[:match.start()],
                                        base[match.end():])
            head = os.path.dirname(path)
            return os.path.join(head, new_base)
        else:
            return path

    def get_file_textures_from_shading_group(self,shading_group):
        # Get the surface shader connected to the shading group
        surface_shader = cmds.listConnections(shading_group + '.surfaceShader', source=True, destination=False)
        if not surface_shader:
            print(f"No surface shader found for shading group: {shading_group}")
            return []
        surface_shader = surface_shader[0]
        # Get the file textures connected to the shader
        self.file_textures = []
        # List all the connections from the shader
        connections = cmds.listConnections(surface_shader, source=True, destination=False)
        if not connections:
            print(f"No connections found for shader: {surface_shader}")
            return []
        for conn in connections:
            # Check if the connection is a file node
            if cmds.nodeType(conn) == 'file' or cmds.nodeType(conn) == 'aiImage':
                self.file_textures.append(conn)
            else:
                # If the connection is not a file node, check its connections
                sub_connections = cmds.listConnections(conn, source=True, destination=False)
                if sub_connections:
                    for sub_conn in sub_connections:
                        if cmds.nodeType(sub_conn) == 'file' or cmds.nodeType(sub_conn) == 'aiImage':
                            self.file_textures.append(sub_conn)
                        else:
                            # If the connection is not a file node, check its connections
                            sub_connections_1 = cmds.listConnections(sub_conn, source=True, destination=False)
                            if sub_connections_1:
                                for sub_conn_1 in sub_connections_1:
                                    if cmds.nodeType(sub_conn_1) == 'file' or cmds.nodeType(sub_conn_1) == 'aiImage':
                                        self.file_textures.append(sub_conn_1)
        return self.file_textures

    def save_shaders(self):
        self.alphabetic_folder = self.lineEdit_asset_name.text().capitalize()[0]
        self.file_name_folder = self.lineEdit_asset_name.text().rsplit('.', 1)[0]
        print(self.alphabetic_folder)
        self.sourceimages_folder = os.path.join(self.asset_library_root_path.replace("/", "\\"), self.comboBox_asset_group.currentText(), self.comboBox_add_type.currentText(), self.alphabetic_folder, self.file_name_folder, 'sourceimages')
        if not os.path.exists(self.sourceimages_folder):
            os.makedirs(self.sourceimages_folder)
        self.shader_folder = os.path.join(self.asset_library_root_path.replace("/", "\\"), self.comboBox_asset_group.currentText(), self.comboBox_add_type.currentText(), self.alphabetic_folder, self.file_name_folder,'scenes')
        if not os.path.exists(self.shader_folder):
            os.makedirs(self.shader_folder)
        shadingGrp=[]
        self.file_to_copy = []
        objj = cmds.ls(sl=1)[0]
        shape = cmds.listRelatives(objj,s=True)[0]
        shadingGrp_list = cmds.listConnections(shape, type='shadingEngine')

        for lst in shadingGrp_list:
            if lst in shadingGrp:
                continue
            shadingGrp.append(lst)

        shading_groups = shadingGrp

        for sg in shading_groups:
            textures = self.get_file_textures_from_shading_group(sg)
            textures = list( dict.fromkeys(textures) )
            if textures:
                for tex in textures:
                    print(tex)
                    if cmds.nodeType(tex) == 'file':
                        file_path = cmds.getAttr(tex+'.fileTextureName')
                        print(file_path)
                        file_pattern_name = cmds.getAttr(tex+'.computedFileTextureNamePattern')
                        tex_file = self.seq_to_glob(file_path)
                        tex_file= tex_file.replace('\\','/')
                        print(tex_file)
                        if tex_file not in self.file_to_copy:
                            self.file_to_copy.append(tex_file)
                        # print(f" - File Texture: {file_path}")
                        old = file_pattern_name.split('/')
                        new = self.sourceimages_folder+'/'+old[-1]
                        print(new)
                        cmds.setAttr(tex+'.fileTextureName',new,type='string')
                    elif cmds.nodeType(tex) == 'aiImage':
                        file_path = cmds.getAttr(tex+'.filename')
                        tex_file = self.seq_to_glob(file_path)
                        print(tex_file)
                        tex_file= tex_file.replace('\\','/')
                        if tex_file not in self.file_to_copy:
                            self.file_to_copy.append(tex_file)
                        old = file_path.split('/')
                        new = self.sourceimages_folder+'/'+old[-1]
                        cmds.setAttr(tex+'.filename',new,type='string')

        for files in self.file_to_copy:
            for img_path in glob.glob(files):
                shutil.copy(img_path, self.sourceimages_folder)

        cmds.select(cl=1)
        cmds.select(shadingGrp, ne=True)
        cmds.file( self.shader_folder+'/'+self.file_name_folder+'.ma', force=True, es=True, type="mayaAscii")

    def save_swtich(self):
        if self.comboBox_asset_group.currentText() == 'materials':
            self.save_shaders()
        else:
            self.saveTextures()  

    def load_and_configure_arnold_render(self):
        # Check that IPR and Batch is not running. Otherwise - cancel:
        try:
            cmds.arnoldRenderView(opt = ('Run IPR', 'False'))
        except:
            pass
        try:
            cmds.batchRender()
        except:
            pass
        if 'mtoa' in cmds.moduleInfo(listModules = True):
            if not cmds.pluginInfo('mtoa', query = True, loaded = True):
                print(('{0}{1}{2}{0}'
                    ).format('\n','\t', ' Loaded Arnold MtoA Plugin ...'))
                try:
                    cmds.loadPlugin('mtoa', quiet = True)
                    print(('{0}{1}{2}{0}'
                        ).format('\n', '\t',
                                ' Loaded Arnold MtoA Plugin - successful.'))
                    from mtoa.core import createOptions
                    if not cmds.objExists('defaultArnoldRenderOptions'):
                        print(('{0}{1}{2}{0}'
                            ).format('\n', '\t',
                                    ' Create Arnold Render Options ...'))
                        createOptions()
                        print(('{0}{1}{2}{0}'
                            ).format('\n', '\t',
                                    ' Create Arnold Render Options -' +
                                    ' successful.'))
                    print(('{0}{1}{2}{0}'
                        ).format('\n', '\t',
                                ' Configure Arnold Render Options ...'))
                    cmds.setAttr(
                        'defaultArnoldRenderOptions.render_device_fallback', 1)
                    cmds.setAttr(
                        'defaultArnoldRenderOptions.renderDevice', 0)
                    cmds.setAttr(
                        'defaultArnoldRenderOptions.abortOnError', 0)
                    print(('{0}{1}{2}{0}'
                        ).format('\n', '\t',
                                ' Arnold Render Options configure -' +
                                ' successful.'))
                except Exception:
                    print(('{0}{1}{2}{0}'
                        ).format('\n', '\t',
                                ' !!! Error loading Arnold MtoA Plugin !!!'))
                    traceback_print_exc()
                    return 0
                else:
                    return 1
            else:
                try:
                    print(('{}{}'
                        ).format('\t',
                                ' Create and configure Arnold Render Options ' +
                                '...'))
                    from mtoa.core import createOptions
                    createOptions()
                    cmds.setAttr(
                        'defaultArnoldRenderOptions.render_device_fallback', 1)
                    cmds.setAttr(
                        'defaultArnoldRenderOptions.renderDevice', 0)
                    cmds.setAttr(
                        'defaultArnoldRenderOptions.abortOnError', 0)
                    cmds.arnoldFlushCache(flushall = True)
                    print(('{1}{2}{0}'
                        ).format('\n', '\t',
                                ' Arnold Render Options create and configure' +
                                ' - successful'))
                except Exception:
                    print(('{0}{1}{2}{0}'
                        ).format('\n', '\t',
                                ' !!! Error Create and configure Arnold' +
                                ' Render Options !!!'))
                    traceback_print_exc()
                    return 0
                else:
                    return 1
        else:
            print(('{0}{0}{1}{2}{0}{0}'
                ).format('\n', '\t',
                        ' !!! Arnold MtoA Plugin Not registred in this' +
                        ' MAYA_PLUG_IN_PATH !!!'))
            return 0


    # Def for configure minimal Renderer options:
    def prerender_settings(self,output_dir, image_base_name, camera_name, start_frame, end_frame, step_frame = 1, image_format = 'exr'):

        # Create output dir if not exists.
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # Create output file name with camera name and resolution parametrs.
        output_file_base_name = ('{}').format(image_base_name)

        if self.load_and_configure_arnold_render():
            # Set "defaultArnoldRenderOptions" "renderGlobals" attribut from "defaultRenderGlobals" node attributes.
            cmds.setAttr('defaultArnoldRenderOptions.renderGlobals', 'defaultRenderGlobals', type = 'string')

            # Set "defaultArnoldDriver" attribut for output render file format ("exr").
            cmds.setAttr('defaultArnoldDriver.aiTranslator', image_format, type = 'string')
            cmds.setAttr('defaultArnoldDriver.outputMode', 2)
            cmds.setAttr('defaultArnoldDriver.exrCompression', 0)
            cmds.setAttr('defaultArnoldDriver.colorManagement', 1)

            # Set defaultRenderGlobals attributes for prefix (replace default render path)
            cmds.setAttr('defaultRenderGlobals.imageFilePrefix', output_file_base_name, type = 'string')
            cmds.setAttr('defaultRenderGlobals.useFrameExt', 0)
            cmds.setAttr('defaultRenderGlobals.useMayaFileName', 1)

            # Set defaultRenderGlobals attributes for naming with frame ext.
            cmds.setAttr('defaultRenderGlobals.animation', 0)
            # cmds.setAttr('defaultRenderGlobals.outFormatControl', 0)
            # cmds.setAttr('defaultRenderGlobals.putFrameBeforeExt', 1)
            # cmds.setAttr('defaultRenderGlobals.periodInExt', 2)
            #cmds.setAttr('defaultRenderGlobals.extensionPadding', 4)

            # Set defaultRenderGlobals attributes for animation range
            # cmds.setAttr('defaultRenderGlobals.animationRange', 0)
            # cmds.setAttr('defaultRenderGlobals.startFrame', start_frame)
            # cmds.setAttr('defaultRenderGlobals.endFrame', end_frame)
            # cmds.setAttr('defaultRenderGlobals.byFrameStep', step_frame)
            return 1
        else:
            cmds.error('\n', '\t',
                    ' !!! Error Create and configure Arnold' +
                    ' Render Options !!!')
            return 0

    def thumbnail_render(self):
        # Set Custom input parametrs:
        self.alphabetic_folder = self.lineEdit_asset_name.text().capitalize()[0]
        self.file_name_folder = self.lineEdit_asset_name.text().rsplit('.', 1)[0]
        image_format = 'png'
        camera_name = 'persp'
        im_h = 128
        im_w = 128
        start_frame = 0
        end_frame = 0
        step_frame = 1
        image_base_name = self.lineEdit_asset_name.text()
        temp_dir = 'C:/temp'
        output_dir = os.path.normpath(temp_dir)
        self.thumbnail_folder = os.path.join(self.asset_library_root_path.replace("/", "\\"), self.comboBox_asset_group.currentText(), self.comboBox_add_type.currentText(), self.alphabetic_folder, self.file_name_folder,'previews')
        if not os.path.exists(self.thumbnail_folder):
            os.makedirs(self.thumbnail_folder)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        # Get current "images" folder:
        workspace_file_rule_images = cmds.workspace(fileRuleEntry = 'images')
        # Get extend current "images" folder:
        cmds.workspace(expandName = workspace_file_rule_images)
        # Set output dir for current "images" folder:
        cmds.workspace(fileRule=[workspace_file_rule_images, temp_dir])

        # We will do all preparatory work:
        alloved = self.prerender_settings(output_dir, image_base_name, camera_name, start_frame, end_frame, step_frame, image_format)

        # Rendering current frame. Only camera flag. Resolution from value in defaultResolution node
        if alloved: cmds.arnoldRender(camera = camera_name)
        # Assign the previos value for "images" folder (relative):
        cmds.workspace(fileRule = ['images', workspace_file_rule_images])
        cmds.RenderViewWindow()
        cmds.renderWindowEditor("renderView",e=True,li=temp_dir+'/tmp/'+image_base_name+'.png')
        shutil.copy2(temp_dir+'/tmp/'+image_base_name+'.png',self.thumbnail_folder)
        self.icon_name = self.thumbnail_folder+'/'+image_base_name+'.png'
        description_file_path = self.icon_name.replace(".png", ".txt")
        print(description_file_path)
        if not (self.plainTextEdit_description.toPlainText()==""):
            with open(description_file_path, "w") as file:
                file.write(self.plainTextEdit_description.toPlainText())   

    def thumbnail_switch(self):
        if self.comboBox_asset_group.currentText() == 'materials':
            self.thumbnail_render()
        else:
            self.screenShot()  







#####
current_user = getpass.getuser().lower()

if(__name__ == '__main__'):
    user_file_path = SCRIPT_FILE_PATH+'config/user.txt'
else:
    user_file_path = os.path.abspath(os.path.dirname(__file__)+'/config/user.txt')
user_list = []
with open(user_file_path, "r") as user_file:
    lines = user_file.readlines()
    for line in lines:
        new=line.replace('\n','')
        user_list.append(new)

if current_user not in user_list:
    cmds.confirmDialog( title='Warning', message="You don't have permission to publish assets!")
else:
    try:
        UI.close()
    except:
        pass
    UI = AssetPublish()
    UI.show()

