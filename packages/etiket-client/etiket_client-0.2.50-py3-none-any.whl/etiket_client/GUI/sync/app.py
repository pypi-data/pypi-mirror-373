from etiket_client.GUI.sync.models.login_mgmt import login_manager, auth_option_list
from etiket_client.GUI.sync.models.scope_mgmt import scope_manager
from etiket_client.GUI.sync.models.schema_mgmt import schema_manager

from etiket_client.GUI.sync.models.sync_def_scope import sync_def_scope
from etiket_client.GUI.sync.models.sync_mgmt import synchronisation_manager
from etiket_client.GUI.sync.models.sync_proc_mgmt import sync_proc_manager

from PyQt5 import QtCore, QtQml, QtGui

import etiket_client.GUI.sync.qml.icons as sync_icons
import etiket_client.GUI.sync.resources.resource_rc
import sys, pathlib, os, inspect


def launch_GUI():
    app = QtGui.QGuiApplication.instance()
    if not app:
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        QtCore.QCoreApplication.setOrganizationName('qDrive')
        QtCore.QCoreApplication.setApplicationName('eTiKet settings manager')
        QtCore.QCoreApplication.setApplicationVersion('0.1.0')
        app = QtGui.QGuiApplication(sys.argv)
    
    path = os.path.join(os.path.dirname(inspect.getfile(sync_icons)), "app_icon.png")
    app.setWindowIcon(QtGui.QIcon(path))

    engine = QtQml.QQmlApplicationEngine()

    login_mgr = login_manager()
    engine.rootContext().setContextProperty("loginMgr", login_mgr)
    
    auth_options = auth_option_list()
    engine.rootContext().setContextProperty("authOptions", auth_options)
    
    scope_mgr = scope_manager()
    engine.rootContext().setContextProperty("scopeMgr", scope_mgr)

    sync_mgr = synchronisation_manager()
    engine.rootContext().setContextProperty("sync_data_model", sync_mgr)


    sync_def_scope_model = sync_def_scope()
    engine.rootContext().setContextProperty("sync_def_scope_model", sync_def_scope_model)

    sync_proc_mgr = sync_proc_manager()
    engine.rootContext().setContextProperty("sync_proc_mgr", sync_proc_mgr)


    qml_file = pathlib.Path(__file__).parent / 'qml/main.qml'
    engine.load(QtCore.QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())