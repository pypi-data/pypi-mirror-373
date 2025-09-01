#ifndef _TELESCOPE_ICE
#define _TELESCOPE_ICE

#include <focuser.ice>

[["python:pkgdir:TcdIce_gen"]]
module TcdIce {
    exception FocuserUnsupportedException extends UnsupportedException {
	};

    exception KeyNotFoundException extends UnsupportedException {
    };

module Telescopes {

    // Mapping dictionary of string keys to untyped Ice-proxies
    dictionary<string, Object *> proxy_map_t;

    // Interface of an abstract telescope
    interface Telescope {
        // Get map of all Ice proxies supplied by this telescope
        // Proxies are mapped to unique string keys which have the following naming concept: key_name = [<parent_proxy_node>.]<Proxy_name>
        // Tip: proxies with the SAME name should have the SAME type
        idempotent proxy_map_t get_all_ice_proxies ();

        // Get proxy with specified key from the proxy map (returns NULL if proxy server is currently unavailable)
        idempotent Object *get_ice_proxy ( string key_name ) throws KeyNotFoundException;

        // Get proxy for primary telescope focuser device (returns NULL if focuser server is currently unavailable)
        // Equivalent proxy map key: "telescope.imagers.primary.Focuser"
        TcdIce::Devices::Focuser *get_focuser () throws FocuserUnsupportedException;
    };

};
};

#endif
