#ifndef _SELECTOR_ICE
#define _SELECTOR_ICE

#include <tcd_ice_base.ice>

[["python:pkgdir:TcdIce_gen"]]
module TcdIce {

    // PositionSelector introduces the class of devices which have a small
    // number of states (positions), with each position having some
    // descriptive name. Examples of such devices can be a filter
    // wheel (with state's names as 'B', 'V', 'R', 'blank'),
    // objective cover ('opened', 'closed') and so on.

    module PositionSelector {

        struct device_info_t {
            string sysname;          // system name (for logfiles, FITS headers, etc)
            string visname;          // visible name (e.g. GUI window title)
            string description;      // description
            bool stoppable;          // if true, one can call stop() to abort setpos()
        };

        const int POS_CHANGE  = -1;  // position changing in progress, please wait
        const int POS_UNKNOWN = -2;  // position is unknown (forgotten), the call of setpos() is required

        struct position_t {
            string sysname;          // system name (for logfiles, FITS headers, etc)
            string visname;          // visible name (e.g. GUI buttons)
            string description;      // description (GUI tooltips, context help hints, etc)
        };

        sequence<position_t> position_seq;

        interface Selector {
            // return device information
            idempotent device_info_t getinfo();

            // return position names
            idempotent position_seq positions();

            // start moving to a new position
            idempotent void setpos(int pos) throws BaseException;

            // return current position number, or POS_CHANGE, or POS_UNKNOWN
            idempotent int getpos() throws BaseException;

            // same as getpos but also returns position names
            idempotent int getposn(out string sysname, out string visname) throws BaseException;

            // abort moving, stop at unknown position
            idempotent void stop() throws BaseException;
        };
    };
};

#endif
