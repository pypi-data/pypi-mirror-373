import os, sys
from typing import Optional
from PyQt5.QtCore import QLibraryInfo, QCoreApplication

def fix_qt_plugin_paths(prefer_platform: Optional[str] = None) -> None:
    # Limpa variáveis que atrapalham
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
    os.environ.pop("QT_PLUGIN_PATH", None)

    # Escolhe plataforma correta por SO
    if prefer_platform:
        platform = prefer_platform
    else:
        if sys.platform.startswith("win"):      # Windows
            platform = "windows"
        elif sys.platform == "darwin":          # macOS
            platform = "cocoa"
        else:                                   # Linux/BSD
            # xcb (X11) ou wayland – escolha a que seu público usa mais
            platform = "xcb"

    os.environ["QT_QPA_PLATFORM"] = platform

    # Remova caminhos herdados ruins
    for p in list(QCoreApplication.libraryPaths()):
        if "cv2/qt/plugins" in p.replace("\\", "/"):
            QCoreApplication.removeLibraryPath(p)

    # Garanta os plugins do PyQt5
    QCoreApplication.addLibraryPath(QLibraryInfo.location(QLibraryInfo.PluginsPath))


def assert_not_using_cv2_plugins() -> None:

    for p in QCoreApplication.libraryPaths():
        if "cv2/qt/plugins" in p:
            raise RuntimeError(
                "Error"
            )
