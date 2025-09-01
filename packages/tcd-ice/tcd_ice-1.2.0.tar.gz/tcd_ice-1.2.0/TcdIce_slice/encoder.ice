#ifndef _ENCODER_ICE
#define _ENCODER_ICE

#include <device.ice>

[["python:pkgdir:TcdIce_gen"]]
module TcdIce {
module Devices {

    // Encoder positioning mode supported
    enum encoder_posmode_t {
        VOLATILE,   // Position of encoder will be cleared on power off
        PERSISTENT  // Position of encoder will be kept between power cycles
    };

    // Encoder configuration structure
    struct encoder_config_t {
        encoder_posmode_t posmode;
        bool sync_to_pos;   // true if position synchronization is supported, false otherwise
    };

    // Interface of abstract position encoder
    // Encoder position units are undefined on this level of interface (it depends on the type of child interface)
    interface Encoder extends Device {
        // Get encoder configuration
        idempotent encoder_config_t get_encoder_config ();

        // Get current position of the encoder
        idempotent double get_position () throws BaseException;

        // Synchronize encoder to specified position, returns true if position synchronization is supported
        idempotent bool sync_to_pos (double pos) throws BaseException;

        // Get IceStorm topic proxy with interface EncoderMonitor (returns NULL if topic currently is unavailable)
        idempotent IceStorm::Topic *get_encoder_topic () throws TopicUnsupportedException;
    };

    // Message-based interface for abstract position encoder (this interface is provided by IceStorm)
    interface EncoderMonitor {
        // Message, generated when position of encoder changed
        void on_new_position (double pos);
    };

};
};

#endif
