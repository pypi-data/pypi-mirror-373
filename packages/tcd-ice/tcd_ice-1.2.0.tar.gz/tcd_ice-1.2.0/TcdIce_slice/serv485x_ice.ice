#ifndef _SELECTOR_ICE
#define _SELECTOR_ICE

#include <tcd_ice_base.ice>

[["python:pkgdir:TcdIce_gen"]]
module TcdIce {

    // Serv485 - to access devices on RS-485 bus

    module Serv485 {

        sequence<byte> byteseq_t;

        exception Serv485Exception extends BaseException {
            int code;
        };

        interface Bus485 {
            // check the module presense
            idempotent void check(byte addr) throws Serv485Exception;

            // request data methods
            idempotent void request(byte addr, out byteseq_t data) throws Serv485Exception;
            idempotent void request_red(byte addr, out byteseq_t data) throws Serv485Exception;
            idempotent void xrequest(byte addr, byte xreq, out byteseq_t data) throws Serv485Exception;

            // send data methods
            idempotent void send(byte addr, byteseq_t data) throws Serv485Exception;
        };
    };
};

#endif
