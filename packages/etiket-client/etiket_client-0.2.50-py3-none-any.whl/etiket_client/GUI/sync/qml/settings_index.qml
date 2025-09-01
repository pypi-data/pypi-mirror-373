import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
import QtQuick.Controls.Material 2.12

Item{
    StackLayout {
        anchors.top : parent.top
        anchors.bottom : bar.top
        width: parent.width
        currentIndex: bar.currentIndex
        Loader {
            source: "settings_pages/scope_settings.qml"
        }
        Loader {
            source: "settings_pages/sync_settings.qml"
        }
        Item {
            id: synchronizationTab
            Text{
                text : "sync stuff"
                color : "white"

            }
        }
    }

    TabBar {
        anchors.bottom : parent.bottom
        id: bar
        width: parent.width
        TabButton {
            text: qsTr("Settings")
            font.capitalization: Font.MixedCase
        }
        TabButton {
            text: qsTr("Synchronization")
            font.capitalization: Font.MixedCase
        }
    }
}
