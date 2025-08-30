import QtQuick
import QtQuick.Window
import QtMultimedia
import Pose 1.0
import "../sidepose/qml/Pose"

Window {
    visible: true
    width: 1280
    height: 720
    title: "Pose Minimal"

    VideoOutput {
        id: view
        anchors.fill: parent
        fillMode: VideoOutput.PreserveAspectFit
    }

    MediaPlayer {
        id: player
        source: Qt.resolvedUrl("sample.mp4")
        autoPlay: true
        loops: MediaPlayer.Infinite
        videoOutput: view
    }

    PoseProcessor {
        id: pose
        videoSink: view.videoSink
        backend: "mediapipe"
        useGpu: true
        modelAssetPath: "pose_landmarker_heavy"
        numPoses: 2
        onError: function (msg) { console.error(msg); }
    }

    PoseSpace {
        id: overlay
        anchors.fill: parent
        processor: pose
        fitMode: Pose.FitMode.PreserveAspectFit
        property real confThresh: 0.7

        // Keypoints (all 33)
        Repeater {
            model: 33
            delegate: PoseKeypointAnchor {
                processor: pose
                personIndex: 0
                keypoint: index
                minConfidence: overlay.confThresh
                fitMode: Pose.FitMode.PreserveAspectFit
                Rectangle {
                    anchors.centerIn: parent
                    width: 6; height: 6; radius: 3
                    color: "#FF4081"
                }
            }
        }

        // Keypoints for person 2
        Repeater {
            model: 33
            delegate: PoseKeypointAnchor {
                processor: pose
                personIndex: 1
                keypoint: index
                minConfidence: overlay.confThresh
                fitMode: Pose.FitMode.PreserveAspectFit
                Rectangle {
                    anchors.centerIn: parent
                    width: 6; height: 6; radius: 3
                    color: "#FF4081"
                }
            }
        }

        // Bones (12 pairs)
        Repeater {
            model: 12
            delegate: PoseBoneAnchor {
                processor: pose
                personIndex: 0
                bone: index
                minConfidence: overlay.confThresh
                fitMode: Pose.FitMode.PreserveAspectFit
                height: 4
                Rectangle { anchors.fill: parent; color: "#40C4FF"; radius: 2 }
            }
        }

        // Bones for person 2
        Repeater {
            model: 12
            delegate: PoseBoneAnchor {
                processor: pose
                personIndex: 1
                bone: index
                minConfidence: overlay.confThresh
                fitMode: Pose.FitMode.PreserveAspectFit
                height: 4
                Rectangle { anchors.fill: parent; color: "#40C4FF"; radius: 2 }
            }
        }

        // Face mask overlay
        PoseFaceAnchor {
            processor: pose
            personIndex: 0
            strategy: Pose.FaceStrategy.EyesEars
            rotationFrom: Pose.FaceRotation.EarLine
            scaleFactor: 3.0
            fitMode: Pose.FitMode.PreserveAspectFit
            Image {
                anchors.fill: parent
                source: Qt.resolvedUrl("face_mask.png")
                fillMode: Image.PreserveAspectFit
                smooth: true
            }
        }

        // Face mask overlay for person 2
        PoseFaceAnchor {
            processor: pose
            personIndex: 1
            strategy: Pose.FaceStrategy.EyesEars
            rotationFrom: Pose.FaceRotation.EarLine
            scaleFactor: 3.0
            fitMode: Pose.FitMode.PreserveAspectFit
            Image {
                anchors.fill: parent
                source: Qt.resolvedUrl("face_mask.png")
                fillMode: Image.PreserveAspectFit
                smooth: true
            }
        }
    }
}
