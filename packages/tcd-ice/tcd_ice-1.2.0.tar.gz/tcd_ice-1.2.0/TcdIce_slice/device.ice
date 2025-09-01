#ifndef _DEVICE_ICE
#define _DEVICE_ICE

#include <tcd_ice_base.ice>
#include <IceStorm/IceStorm.ice>

[["python:pkgdir:TcdIce_gen"]]
module TcdIce {
module Devices {

    // Device information structure
    struct device_info_t {
        string sysname;          // system name (for logfiles, FITS headers, etc)
        string visname;          // visible name (e.g. GUI window title)
        string description;      // description
    };

    // Hardware states of abstract device in TcdIce scope
    enum device_hw_state_t {
        WORKING,        // Device is prepared and ready to work
        DISCONNECTED,   // Device is disconnected from Ice-server host
        PREPARING,      // Device is connected, but not prepared to work (it's busy by some initialization process)
        FAULT           // Device cannot work due to some hardware fault in system
    };

    // Basic impurity interface for asynchronous devices
    interface Asynchronous {
        // Returns information about device's error.
        // error_count: number of errors occured since device server startup,
        // error_code: code of last error ( = 0 if no errors occurred yet),
        // error_message: textual description of error.
        idempotent void get_last_error (out int error_count, out int error_code, out string error_message);
    };

    // Basic impurity interface for devices which can be stopped during operation
    interface Stoppable {
        // Stops current device operation (if device is running one)
        idempotent void stop () throws BaseException;
    };

    // Basic interface for all devices in TcdIce scope
    interface Device {
        // Returns some descriptive information about device
        idempotent device_info_t get_device_info ();

        // Current device state
        idempotent device_hw_state_t get_hw_state ();

        // Get IceStorm topic proxy with interface DeviceMonitor (returns NULL if topic currently is unavailable)
        idempotent IceStorm::Topic *get_device_topic () throws TopicUnsupportedException;
    };

    // Message-based interface for all devices in TcdIce scope (this interface is provided by IceStorm)
    interface DeviceMonitor {
        // Message informing about new device hardware state
        void on_new_hardware_state (device_hw_state_t hw_state);

        // Message informing about error, occurred during device functioning
        void on_error (int error_count, int error_code, string error_message);
    };

};
};

#endif
