#ifndef _FOCUSER_ICE
#define _FOCUSER_ICE

#include <mover.ice>

[["python:pkgdir:TcdIce_gen"]]
module TcdIce {
module Devices {

    // Interface of an abstract focuser device
    // Focuser relative position units are millimeters in focal plane
    interface Focuser extends Mover {
    };

    // Interface of an abstract focuser device, which has encoder
    // Absolute focuser position is offset of focal distance relative to nominal focus in millimeters
    interface AbsoluteFocuser extends Focuser, AbsoluteMover {

    };
};
};

#endif
