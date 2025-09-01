#ifndef _TCD_ICE_BASE_ICE
#define _TCD_ICE_BASE_ICE

[["python:pkgdir:TcdIce_gen"]]
module TcdIce {

    exception BaseException {
        string text;
    };

    exception HardwareException extends BaseException {
    };

    exception StdException extends BaseException {  // class of std::exception
    };

    exception UnknownException extends BaseException {  // class of unknown exceptions
    };

    exception BadArgException extends BaseException {  // class of bad argument exceptions
    };

    exception UnsupportedException extends BaseException { // class of exceptions which take place when requested operation is not supported by the server
    };

    exception TopicUnsupportedException extends UnsupportedException {
    };

    struct kepler_orbit_t {
        double t0;         // [mjd] epoch of elements, UTC
        double a;          // [km] semi-major axis
        double ecc;        // eccentricity
        double incl;       // [radians] inclination
        double raan;       // [radians] right ascension of ascending node
        double argp;       // [radians] argument of perigee
        double anmean;     // [radians] mean anomaly
        string system;     // type of orbital elements ('TEME', 'TOD')
        string propagator; // orbit propagator ('kepler', 'sgp4', ...)
    };
};

#endif
