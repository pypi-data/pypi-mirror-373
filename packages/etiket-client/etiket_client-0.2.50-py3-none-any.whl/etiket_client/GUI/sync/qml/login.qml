import QtQuick 2.0
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
import QtQuick.Controls.Material 2.12

Item {
    Text {
        id: institutionDescription
        text: "Please select the server you want to connect to:"
        anchors.top: parent.top
        anchors.topMargin: 30
        font.pixelSize: 14
        x : parent.width * 0.1
        color: "#D3D3D3"
    }

    ComboBox {
        id: institutionComboBox
        width: parent.width * 0.8
        anchors.top: institutionDescription.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 7
        model: loginMgr.institutions
        currentIndex: -1
        // add on selection change
        onCurrentIndexChanged: {
            Qt.callLater(function() {
                authOptions.set_institution_data(institutionComboBox.currentText)
                login_method_selector.push(ssoLogin)
            })
        }
    }

    StackView {
        id: login_method_selector
        anchors.top: institutionComboBox.bottom
        anchors.bottom: parent.bottom
        width: parent.width

        initialItem: emptyWindow
    }

    Component{
        id : emptyWindow
        Item{}
    }

    Component{
        id: legacyLogin

        Item {
            TextField {
                id: usernameInput
                width: parent.width * 0.8
                placeholderText: "username"
                anchors.top: parent.top
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.topMargin: 45
                selectByMouse: true
            }

            TextField {
                id: passwordInput
                width: parent.width * 0.8
                placeholderText: "Password"
                anchors.top: usernameInput.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.topMargin: 10
                echoMode: TextInput.Password
                selectByMouse: true
                KeyNavigation.tab : loginBotton
                Keys.onReturnPressed: loginBotton.clicked()
            }

            Text {
                anchors.top: passwordInput.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.topMargin: 50
                
                id: errorLogIn
                visible : false
                color: Material.color(Material.Red, Material.Shade300)
                font.pixelSize: 12
                text: "Username or password is incorrect, please try again."
                Layout.preferredHeight: 100
                
                SequentialAnimation {
                    id : errorLogInAnimation
                    NumberAnimation { target: errorLogIn; property: "anchors.horizontalCenterOffset"; to: 10; duration: 60 }
                    NumberAnimation { target: errorLogIn; property: "anchors.horizontalCenterOffset"; to: -10; duration: 60 }
                    NumberAnimation { target: errorLogIn; property: "anchors.horizontalCenterOffset"; to: 10; duration: 60 }
                    NumberAnimation { target: errorLogIn; property: "anchors.horizontalCenterOffset"; to: -10; duration: 60 }
                    NumberAnimation { target: errorLogIn; property: "anchors.horizontalCenterOffset"; to: 0; duration: 30 }
                }
            }

            Button {
                id : loginBotton
                text: "Login"
                width: parent.width * 0.4
                anchors.top: errorLogIn.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.topMargin: 20

                Material.accent: Material.BlueGrey

                function login() {
                    errorLogIn.visible = false;
                    var state = loginMgr.login(usernameInput.text, passwordInput.text, institutionComboBox.currentText);
                    errorLogIn.visible = !state;
                    errorLogInAnimation.restart();
                    if (state==true){
                        login_method_selector.push(emptyWindow)
                        institutionComboBox.currentIndex = -1
                        scopeMgr.rebuild()
                    }
                }

                onClicked: loginBotton.login()
                Keys.onReturnPressed: loginBotton.login()
                Keys.onEnterPressed: loginBotton.login()
            }

            Text {
                anchors.top: loginBotton.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.topMargin: 30

                text: "Click here if you don't have an account."
                font.pixelSize: 12
                color: "white"
            }
        }
    }

    Component{
        id: ssoLogin

        Item{
            ScrollView {
                id: authOptionsScrollView
                y : 40
                width: etiketApp.width
                height: parent.height - 150
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

                ListView {
                    id: authOptions_list
                    spacing: 18
                    model: authOptions
                    

                    delegate: Rectangle {
                        width: etiketApp.width - 80
                        x : 40
                        height: 40
                        color: "transparent"
                        border.color: "white"


                        MouseArea {
                            anchors.fill: parent  // Fill the entire rectangle
                            hoverEnabled: true

                            onClicked: {
                                // You can add additional actions here
                                if(is_legacy_login){
                                    login_method_selector.push(legacyLogin)
                                }else{
                                    errorLogInSSO.visible = false;
                                    var state = loginMgr.login_sso(auth_provider_id, institution);
                                    if (state==true){
                                        login_method_selector.push(emptyWindow)
                                        institutionComboBox.currentIndex = -1
                                        scopeMgr.rebuild()
                                    }
                                    if (state==false){
                                        errorLogInSSO.visible = true;
                                        errorLogInSSOAnimation.restart();
                                    }
                                }
                                parent.color = "transparent"
                            }

                            // Optional: Change color on hover
                            onEntered: {
                                parent.color = "gray"
                            }

                            onExited: {
                                parent.color = "transparent"
                            }
                        }

                        Text {
                            anchors.centerIn: parent
                            text: auth_provider_name
                            color: "white"
                        }
                    }

                }
            }

            Text {
                anchors.top: authOptionsScrollView.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.topMargin: 50
                
                id: errorLogInSSO
                visible : false
                color: Material.color(Material.Red, Material.Shade300)
                font.pixelSize: 12
                textFormat: Text.RichText
                text: "Error in SSO login, please try again <br> (see terminal for more information)."
                Layout.preferredHeight: 100
                
                SequentialAnimation {
                    id : errorLogInSSOAnimation
                    NumberAnimation { target: errorLogInSSO; property: "anchors.horizontalCenterOffset"; to: 10; duration: 60 }
                    NumberAnimation { target: errorLogInSSO; property: "anchors.horizontalCenterOffset"; to: -10; duration: 60 }
                    NumberAnimation { target: errorLogInSSO; property: "anchors.horizontalCenterOffset"; to: 10; duration: 60 }
                    NumberAnimation { target: errorLogInSSO; property: "anchors.horizontalCenterOffset"; to: -10; duration: 60 }
                    NumberAnimation { target: errorLogInSSO; property: "anchors.horizontalCenterOffset"; to: 0; duration: 30 }
                }
            }
        }
    }
}