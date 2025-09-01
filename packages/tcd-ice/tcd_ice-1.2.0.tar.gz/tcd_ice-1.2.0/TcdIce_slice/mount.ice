#ifndef _MOUNT_ICE
#define _MOUNT_ICE

#include <tcd_ice_base.ice>

[["python:pkgdir:TcdIce_gen"]]
module TcdIce {

    // Telescope's mount and dome control

    module Mount {

        enum error_t {
            E_SUCCESS,
            E_STDEXC,     // std::exception
            E_UNKEXC,     // unknown exception
            E_BADARG,     // bad argument
            E_BADTARGET,  // unknown target or parsing target string error
            E_HARDWARE,   // telescope/dome hardware error
            E_RUNLEVEL,   // current runlevel is unsuitable for this command
            E_TRACKING,   // telescope/dome's tracking mode is unsuitable for this command
        };

	exception MountError extends BaseException {
            error_t code;
	};

        enum runlevel_t { RL_IDLE, RL_READONLY, RL_MONITOR, RL_NORMAL };

        enum dome_track_mode_t {
            DOME_TRACK_TARGET, DOME_TRACK_SCOPE, DOME_TRACK_AUTO, DOME_TRACK_POS
        };

        enum refsys_t {
            MEAN_RA_DE,  // Mean (ICRS) RA, Dec
            APPA_HA_DE,  // Apparent HA, Dec
            OBS_AZ_EL,   // Observed Azimuth, Elevation
            INST_HA_DE,  // Instrumental HA, Dec
        };

        struct vec2 {
            double x0;   // e.g. RA (ICRS), H.A. (apparent), Azimuth, etc
            double x1;   // e.g. DEC (ICRS), DEC (apparent), Elevation, etc
        };

        struct tracker_state_t {
            runlevel_t runlevel;    // running level

            bool tracking;          // tracking state
            bool pointing_phase;    // pointing phase of the tracking
            double track_precision;

            bool dome_tracking;     // dome tracking state and mode
            dome_track_mode_t dome_track_mode;
            double dome_track_pos;  // dome tracking position (only for DOME_TRACK_POS mode)

            int target_cnt;         // target counter (to detect target changing)
        };

        struct dome_predict_t {
            double dome_az;  // dome azimuth, horizontal (0..2pi), 0 at south
            double dome_el;  // dome elevation
        };

        enum find_target_timeshift_status_t {
            FT_SUCCESS,
            FT_NODATA,   // Target has no ephemeris data.
            FT_MAXITER,  // Max. number of iterations reached.
            FT_NOROOT,   // "No root" condition detected. Possible reasons:
                         //  - too big ang. shift requested,
                         //  - static (star-like) target (no ang. shift),
                         //  - multiple roots because of non-monotonous 'timeshift -> ang_shift'
                         //    function (polinomial approximation of ephemeris?)
        };

        struct find_target_timeshift_t {
            double ang_shift;    // [radians] input (desired) angular shift, positive or negative
                                 // (on success, found timeshift will have the same sign)
            double ang_epsilon;  // [radians] acceptable ang_shift precision (iteration stop condition)
            double epoch;        // [mjd] epoch of calculations
            int iterations;      // number of iterations performed
            double ang_residual; // [radians] ang_shift final residual
            double ts_residual;  // [seconds] timeshift final residual
            find_target_timeshift_status_t status;
            double timeshift;    // [seconds] found timeshift (if status == FT_SUCCESS)
        };

        struct target_timeshift_t {
            double timeshift;  // [seconds]
            double ang_shift;  // [radians] has the same sign as the timeshift
        };

        struct target_state_t {
            bool data_valid;
            vec2 cel;       // celestial coordinates
            vec2 hor;       // horizontal coordinates
            vec2 ins;       // instrumental coordinates
            vec2 crates;    // celestial rates
            vec2 hrates;    // horizontal rates
            vec2 irates;    // instrumental rates
            vec2 adj_pos;   // celestial adjustments - coordinates
            vec2 adj_rate;  // celestial adjustments - rates
            string name;    // name
            dome_predict_t dpp;  // dome prediction data
            target_timeshift_t tshift;  // target timeshift data
        };

        struct scope_state_t {
            bool data_valid;
            vec2 cel;       // celestial coordinates
            vec2 hor;       // horizontal coordinates
            vec2 ins;       // instrumental coordinates
            vec2 crates;    // celestial rates
            vec2 hrates;    // horizontal rates
            vec2 irates;    // instrumental rates
            dome_predict_t dpp;  // dome prediction data
        };

        struct dome_state_t {
            bool data_valid;
            double hor;     // horizontal position
            double ins;     // instrumental position
            double irate;   // instrumental rate
        };

        struct mount_state_t {
            double mjd;     // epoch of state, UTC
            double last;    // Local Apparent Siderial Time, hours
            tracker_state_t track;
            target_state_t target;
            scope_state_t scope;
            dome_state_t dome;
        };

        struct mount_site_t {
            double latitude;
            double longitude;
            double altitude;
        };

        struct mount_limits_t {
            double inst_axis0_min;  // DEPRECATED: to be removed.
            double inst_axis0_max;  // DEPRECATED: to be removed.
            double inst_axis1_min;  // DEPRECATED: to be removed.
            double inst_axis1_max;  // DEPRECATED: to be removed.
            double elevation_min;
            double elevation_max;
        };

        struct mount_config_t {
            mount_site_t site;
            mount_limits_t limits;
        };

        // types for ephemerides and orbits

        struct EphemPoint {
            double mjd;  // UTC
            double x0;   // e.g. RA (ICRS), H.A. (apparent), Azimuth, etc
            double x1;   // e.g. DEC (ICRS), DEC (apparent), Elevation, etc
        };

        sequence<EphemPoint> EphemPointsSeq;

        struct adjust_target_t {
            bool reset_dr; // how to apply dr
            bool reset_dv; // how to apply dv
            // reset_*: if true, use proposed values as new tracking offset parameters,
            // otherwise add proposed values to current tracking offset parameters

            vec2 dr;   // coordinates offsets (ra, dec)
            vec2 dv;   // additional rates (ra, dec)
        };


        interface Tracker {
            // get current state
            idempotent mount_state_t getstate(double expiration_ms) throws MountError;

            // move instrumental axis (0 for stop with power-on)
            idempotent void move_axis(int axis, double rate) throws MountError;

            // stop instrumental axis (with power-off)
            idempotent void stop_axis(int axis) throws MountError;

            // stop all movings
            idempotent void full_stop() throws MountError;

            // get configuration
            idempotent mount_config_t get_config() throws MountError;

            // set target from string
            idempotent void set_target(string format) throws MountError;

            // set target as point
            idempotent void set_target_point(string target, refsys_t sys, double x0, double x1) throws MountError;

            // set/update ephemeride
            idempotent void set_target_ephem(string target, refsys_t sys, EphemPointsSeq eph) throws MountError;

            // set/update target orbit
            idempotent void set_target_orbit(string target, kepler_orbit_t orbit) throws MountError;

            // set target from targetserv
            idempotent void set_target_targetserv(string target) throws MountError;

            // enable mount (and dome) tracking
            idempotent void set_tracking(bool state) throws MountError;

            // synchronize mount position (e.g. write encoders)
            idempotent void sync_pos(refsys_t sys, double x0, double x1) throws MountError;

            // Find the timeshift that provides a given angular shift along the target ephemeris.
            // epoch: [mjd] epoch of calculations
            // ang_shift: [radians] input (desired) anglular shift, positive or negative
            //                      (on success, found timeshift will have the same sign)
            // ang_epsilon: [radians] acceptable ang_shift precision (iteration stop condition)
            idempotent find_target_timeshift_t find_target_timeshift(
                double epoch, double ang_shift, double ang_epsilon);

            // apply time shift when calculating the current target position
            idempotent void adjust_target_timeshift(double seconds) throws MountError;

            // Deprecated. Use adjust_target2.
            // Apply additional offset/rate when calculating the current target position/rate.
            void adjust_target(adjust_target_t ta) throws MountError;

            // Apply additional offset/rate when calculating the current target position/rate.
            void adjust_target2(adjust_target_t ta, bool add_scope_deviation) throws MountError;

            // change current runlevel
            idempotent void set_runlevel(runlevel_t runlevel) throws MountError;

            // update dome reference system
            // azimuth format: zero at south, positive to the west
            idempotent void dome_sync(double az) throws MountError;

            // synchronize dome position
            idempotent void dome_set_mode(dome_track_mode_t mode, double pos) throws MountError;

            // enable dome tracking
            idempotent void dome_set_tracking(bool state) throws MountError;

            // rotate dome (0 for stop)
            idempotent void dome_move(double rate) throws MountError;
        };
    };
};

#endif
