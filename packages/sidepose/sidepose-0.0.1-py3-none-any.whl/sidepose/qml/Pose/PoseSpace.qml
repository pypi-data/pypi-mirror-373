import QtQuick
import Pose 1.0

Item {
    id: root
    // Headless processor that supplies frame size
    property var processor: null
    // 0: PreserveAspectFit, 1: Fill, 2: FitWidth, 3: FitHeight
    // Keep numeric until enums are added
    property int fitMode: 0
    // Horizontal mirror (flip across vertical axis)
    property bool mirror: false

    // Expose mapping parameters for children if they want them
    readonly property real _srcW: Math.max(1, processor ? processor.frameWidth : 1)
    readonly property real _srcH: Math.max(1, processor ? processor.frameHeight : 1)

    // Helpers (PreserveAspectFit default)
    function _calcScaleOff() {
        const w = Math.max(1, root.width), h = Math.max(1, root.height)
        if (!_srcW || !_srcH) return { scale: 1.0, offx: 0, offy: 0 }
        if (fitMode === 1) { // Fill
            return { scale: Math.max(w/_srcW, h/_srcH), offx: (w - _srcW*Math.max(w/_srcW, h/_srcH))*0.5, offy: (h - _srcH*Math.max(w/_srcW, h/_srcH))*0.5 }
        }
        if (fitMode === 2) { // FitWidth
            const s = w/_srcW; return { scale: s, offx: 0, offy: (h - _srcH*s)*0.5 }
        }
        if (fitMode === 3) { // FitHeight
            const s = h/_srcH; return { scale: s, offx: (w - _srcW*s)*0.5, offy: 0 }
        }
        // PreserveAspectFit
        const s = Math.min(w/_srcW, h/_srcH)
        return { scale: s, offx: (w - _srcW*s)*0.5, offy: (h - _srcH*s)*0.5 }
    }

    // Expose mapping rect like VideoOutput.contentRect
    readonly property real mapX: _calcScaleOff().offx
    readonly property real mapY: _calcScaleOff().offy
    readonly property real mapWidth: _srcW * _calcScaleOff().scale
    readonly property real mapHeight: _srcH * _calcScaleOff().scale
}
