#ifndef _MOVER_ICE
#define _MOVER_ICE

#include <encoder.ice>

[["python:pkgdir:TcdIce_gen"]]
module TcdIce {
module Devices {

    // Device moving state
    enum moving_state_t {
        NOT_MOVING,     // Device is not moving now
        MOVING_POSITIVE,// Device is moving towards the positive direction (position of device is increasing)
        MOVING_NEGATIVE,// Device is moving towards the negative direction (position of device is decreasing)
        LIMIT_POSITIVE, // Positive limit is reached by device (device can not move more in positive direction)
        LIMIT_NEGATIVE  // Negative limit is reached by device (device can not move more in negative direction)
    };

    // Interface of abstract relative mover
    interface Mover extends Device {
        // Do relative shift by value (positive or negative)
        // value units are undefined on this level of interface (it depends on the type of child interface)
        void move_relative (double value) throws BaseException;

        // Get current moving state of device
        idempotent moving_state_t get_moving_state () throws BaseException;

        // Returns the flag of availability of limits for the mover (returns true if limits is available for this mover)
        idempotent bool has_limits ();

        // Get IceStorm topic proxy with interface MoverMonitor (returns NULL if topic currently is unavailable)
        idempotent IceStorm::Topic *get_mover_topic () throws TopicUnsupportedException;
    };

    // Message-based interface for abstract position movers (this interface is provided by IceStorm)
    interface MoverMonitor {
        // Message, generated when moving state of device is changed
        void on_new_moving_state (moving_state_t moving_state);
    };

    // Interface of abstract absolute mover
    // Mover position units are undefined on this level of interface (it depends on the type of child interface)
    interface AbsoluteMover extends Mover, Encoder {
        // Do absolute positioning
        idempotent void move_absolute (double pos) throws BaseException;

        // Get current moving position of device, returns device moving state
        idempotent moving_state_t get_moving_position (out double pos) throws BaseException;

        // Get position limits of mover (return false if position limits is unsupported)
        idempotent bool get_limits (out double min, out double max);
    };
};
};

#endif
