<p align="center">
	<img src="https://gitlab.com/acemetrics-oss/sidepose/-/raw/main/sidepose.png" alt="Sidepose" width="160"/>
	<!-- Fallback for local viewers -->
	<br/>
	<img src="sidepose.png" alt="Sidepose" width="1" style="display:none"/>
</p>

# Pose QML (sidepose)

QML-friendly, headless pose processing with simple anchors for overlaying items on people, bones, and faces.

## Sample outputs

Quick screencasts of the overlay running on sample videos:

- Single person: [sample_outputs/out_single_person.mp4](sample_outputs/out_single_person.mp4)
- Two people: [sample_outputs/out_multi.mp4](sample_outputs/out_multi.mp4)

## Features

- Headless `PoseProcessor` (QObject) for frames from `VideoOutput`/camera.
- QML anchors: `PoseKeypointAnchor`, `PoseBoneAnchor`, `PoseFaceAnchor` to position any QML item.
- `PoseSpace` wrapper auto-computes mapping (like `VideoOutput.contentRect`) so anchors just work.
- Multi-platform model cache with automatic download of MediaPipe pose models.

## Requirements

- Python 3.10+
- PySide6 (Qt 6)
- MediaPipe Tasks (via the `mediapipe` Python package)

Install deps (example):

```bash
python3 -m pip install -U pip
pip install PySide6 mediapipe numpy
```

## Quick start (minimal demo)

Run the example app:

```bash
python3 -m example.main
```

What it does:
- Plays `example/sample.mp4` in a `VideoOutput`.
- Starts `PoseProcessor` and overlays keypoints, bones, and a face mask using anchors inside `PoseSpace`.
- On first run, downloads the default model (`pose_landmarker_full.task`) into a cache.

## Publishing (maintainers)

This project ships wheels and sdists via GitLab CI:

- Create a tag for TestPyPI (e.g., v0.2.0-rc1) to trigger the testpypi job.
- Create a tag like v0.2.0 to enable the manual PyPI publish job.
- Provide CI variables: TWINE_USERNAME (usually __token__), TWINE_PASSWORD_TESTPYPI, TWINE_PASSWORD_PYPI.

## Automatic model handling

You don’t need to specify a model path. If `modelAssetPath` is empty:
- Sidepose defaults to `pose_landmarker_full` and downloads it the first time.
- You can override with a name (`pose_landmarker_lite|full|heavy`), a local path, or a URL (`file://`, `https://`).

Cache location:
- Env override: `SIDEPOSE_CACHE_DIR`.
- Windows: `%LOCALAPPDATA%/sidepose/models` (fallback: `%USERPROFILE%/AppData/Local/sidepose/models`).
- macOS: `~/Library/Caches/sidepose/models`.
- Linux: `$XDG_CACHE_HOME/sidepose/models` or `~/.cache/sidepose/models`.

## Minimal QML snippet

```qml
import QtQuick
import QtQuick.Window
import QtMultimedia
import Pose 1.0
import "../sidepose/qml/Pose"

Window {
	width: 1280
	height: 720
	visible: true

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
	}

	PoseSpace {
		anchors.fill: parent
		processor: pose

		Repeater {
			model: 33
			delegate: PoseKeypointAnchor {
				processor: pose
				keypoint: index
				Rectangle {
					anchors.centerIn: parent
					width: 6; height: 6; radius: 3
					color: "#FF4081"
				}
			}
		}

		Repeater {
			model: 12
			delegate: PoseBoneAnchor {
				processor: pose
				bone: index
				height: 4
				Rectangle {
					anchors.fill: parent
					color: "#40C4FF"
					radius: 2
				}
			}
		}

		PoseFaceAnchor {
			processor: pose
			strategy: Pose.FaceStrategy.EyesEars
			rotationFrom: Pose.FaceRotation.EarLine
			scaleFactor: 1.0
			Image {
				anchors.fill: parent
				source: Qt.resolvedUrl("face_mask.png")
				fillMode: Image.PreserveAspectFit
			}
		}
	}
}
```

## Troubleshooting

- If the model fails to load, check your internet connection on first run, or set `SIDEPOSE_CACHE_DIR` to a writable directory.
- If QML types aren’t found, ensure `register_qml_types()` is called in your runner (example/main.py does this).
- For CPU fallback when GPU init fails, the processor automatically retries; see logs for details.

## License

MIT

