import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
import QtQuick.Controls.Material 2.12

Item {
    id: settingsTab
    width : etiketApp.width
    Item{
        id : userLoggedIn
        width : parent.width
        height : usernameinfo.height + usernameinfoSeparator.height
        
        RowLayout{
            id : usernameinfo
            anchors.topMargin : 10
            width: parent.width
            spacing : 10

            Item { width : 5 }
            Rectangle{
                width: parent.width - 110
                height: 30
                color: "transparent"
                Text{
                    width : parent.width
                    text : "Hi " + loginMgr.getCurrentUser() + "!"
                    font.pixelSize: 22
                    elide: Text.ElideRight
                    color: "white"
                }
            }
            Item {
                Layout.fillWidth: true
            }
            Button {
                icon.source: "./../icons/logout.svg"
                icon.height: 20
                icon.width: 20
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Click to logout!")
                onClicked: loginMgr.logout()
            }
            Item { width : 5 }
        }

        RowLayout{
            id : usernameinfoSeparator
            anchors.top : usernameinfo.bottom
            anchors.topMargin : 0
            width: parent.width

            Item { width : 5 }

            Rectangle{
                Layout.fillWidth: true
                height : 2
            }

            Item { width : 5 }
        }
    }
    Item{
        id : scopeInformation
        width: parent.width
        anchors.top : userLoggedIn.bottom
        anchors.topMargin : 20
        
        

        ColumnLayout{
            width : parent.width

            Item{
                Layout.leftMargin: 18
                Layout.rightMargin: 18
                width : parent.width - 36
                height : 50
            
                Text{
                    id  : selScopeText
                    y : 11
                    text : "Selected scope :"
                    font.pixelSize: 16
                    font.bold : true
                    color: "white"
                }
                Item {
                    id : fillerScope
                    width : selScopeText.contentWidth +10
                    height : 45
                }
                ComboBox {
                    anchors.left : fillerScope.right
                    currentIndex: scopeMgr.currentIndex()
                    model: scopeMgr

                    width : etiketApp.width - 36 - selScopeText.contentWidth - 10 - 26
                    height : 30+16
                    font.pixelSize: 16

                    onCurrentIndexChanged:{
                        scopeMgr.setCurrentIndex(currentIndex)
                        
                    }

                }
                Image {
                    anchors.right: parent.right
                    id: clickableIconforScope
                    source: "./../icons/refresh.svg"
                    y : 10
                    width: 22
                    height: 22
                    // anchors.centerIn: parent
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            scopeMgr.rebuild()
                        }
                        
                    }
                }
            }

            Item {
                Layout.leftMargin: 8+10
                Layout.bottomMargin: 6
                width : description.contentWidth
                height : description.contentHeight
                Text{
                    id : description
                    text : "Description :"
                    font.pixelSize: 16
                    font.bold : true
                    color: "white"
                }
            }

            Item{
                Layout.leftMargin: 8+10
                Layout.rightMargin: 8+10
                width : etiketApp.width-36
                
                Text{
                    id :scopeDescription
                    width : parent.width
                    wrapMode: Text.WordWrap
                    text : "Not implemented."
                    font.pixelSize: 12
                    color: "white"
                }
            }
            Item{
                width : etiketApp.width-36
                height : scopeDescription.contentHeight
            }

            // Item {
            //     Layout.topMargin: 10
            //     Layout.bottomMargin: 6
            //     Layout.leftMargin: 8+10
            //     width : description.contentWidth
            //     height : description.contentHeight
            //     Text{
            //         id : descriptionSchema
            //         text : "Schema settings :"
            //         font.pixelSize: 16
            //         font.bold : true
            //         color: "white"
            //     }
            // }

            // Item{
            //     width: parent.width
            //     height : 200
            //     ListView{
            //         anchors.fill: parent
            //         width: parent.width
            //         model : schemaMgr
                    
            //         delegate : schemaItem
            //         focus : true

            //         Component {
            //             id : schemaItem
                        
            //             Row{
            //                 height : 45
            //                 width : parent.width
            //                 Item{width:20;height:45;}
            //                 Text{
            //                     horizontalAlignment : Text.AlignRight
            //                     y : 10
            //                     id : schemaKeyLabel
            //                     width : 90
            //                     height : 45
            //                     text : name + " :"
            //                     font.pixelSize: 12
            //                     font.bold : true
            //                     color: "white"
                                
            //                 }
            //                 Item{width:10;height:45;}
            //                 Component {
            //                     id: component1
            //                     ComboBox {
            //                         currentIndex: selected_value
            //                         y : -2
            //                         model: values
            //                         width : etiketApp.width - 18 - 120
            //                         height:30+12
            //                         font.pixelSize: 12
            //                         // onCurrentIndexChanged: console.debug(cbItems.get(currentIndex).text)
            //                     }
            //                 }

            //                 Component {
            //                     id: component2
            //                     Item{
            //                         height:45
            //                         width : etiketApp.width - 18 - 120
            //                         TextField {
            //                             selectByMouse: true
            //                             y : 2
            //                             width : etiketApp.width - 18 - 120
            //                             height:40
            //                             text: "SQ124"
            //                             font.pixelSize: 12
            //                         }
            //                     }
                                
            //                 }
            //                 Loader{
            //                     sourceComponent: (fixed_values) ? component1 : component2
            //                 }
            //             }

                        
                    
            //         }
            //     }
            // }
        }
    }
}