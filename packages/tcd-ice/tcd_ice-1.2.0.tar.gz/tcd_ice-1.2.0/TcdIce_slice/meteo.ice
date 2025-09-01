#ifndef _METEO_ICE
#define _METEO_ICE


#include <tcd_ice_base.ice>


[["python:pkgdir:TcdIce_gen"]]
module TcdIce {

    module Meteo {

        exception DataError {
        };

        struct meteoinfo_t {
            int year;              // full year, e.g. 2019
            int month;             // 1..12
            int day;               // 1..31
            double hour;           // 0.0...24.0, UTC
            double temperature;    // C
            double pressure;       // mm Hg
            double rel_humidity;   // 0..100
            double wind_speed;     // meters per second
            double wind_direction; // degrees, N=0, E=90
        };

        sequence<meteoinfo_t> meteoinfo_seq;

        interface MeteoServ {
            idempotent meteoinfo_seq getlastinfo() throws DataError;

	    idempotent meteoinfo_seq gethistory(double period_hours) throws DataError;
        };
    };
};


#endif
