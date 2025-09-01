#ifndef _CAMHOST_ICE_
#define _CAMHOST_ICE_


#include <tcd_ice_base.ice>


[["python:pkgdir:TcdIce_gen"]]
module TcdIce {

    // Camera control

    module Cam {

        sequence<double> double_seq;

        enum error_t {
            CAM_LOGICERR,  // logic error
            CAM_EXCEPTION, // std::exception or unknown exception
            CAM_BADARG,    // bad argument in function call
            CAM_DENIED,    // access denied
            CAM_NOTIMPLEM, // this functionality is not implemented yet
            CAM_EXPOSURE,  // exposure is in progress (settemp, setconf, startexposure)
            CAM_SYSTEM,    // operating system error
            CAM_NODATA,    // no data to read (readframe)
            CAM_HARDWARE,  // hardware error
            CAM_EXTRNSYNC, // external synchronization error
        };

        exception CamError extends BaseException {
            error_t errcode;
        };

        struct caminfo_t
        {
            string description;

            int xsize_total;  // total sensor size (pixels)
            int ysize_total;

            int x0_visib;     // visible region bottom-left pixel position
            int y0_visib;

            int xsize_visib;  // visible region size (pixels)
            int ysize_visib;

            double pixelsz_x;  // pixel size (microns)
            double pixelsz_y;

            int pixeldepth;    // number of bits per pixel

            double_seq pixelrates;  // available pixel rates [Hz]

            int xbin_max;      // maximum binning
            int ybin_max;

            bool shutter_open;   // true, if shutter supports 'OPENED' mode
            bool shutter_close;  // true, if shutter supports 'CLOSED' mode
            bool extern_sync;    // true, if external synchronization is supported
        };

        // shutter states
        enum shutter_t { SHUTTER_AUTO, SHUTTER_OPENED, SHUTTER_CLOSED };

        // frame synchronization modes
        enum synctype_t { SYNC_NONE, SYNC_EXTERN };

        struct frameconf_t
        {
            shutter_t shutter; // shutter state
            double exptime;    // exposure time (seconds)
            int xbin;          // horizontal binning, >= 1
            int ybin;          // vertical binning, >= 1
            int pixelrate;  // pixel rate index
            double gain;       // e- to ADU factor
            synctype_t synctype; // frame synchronization mode

            int frame_x0;   // frame bottom-left pixel position (relative to total sensor)
            int frame_y0;

            int framesz_x;  // horizontal frame size (binned pixels)
            int framesz_y;  // vertical frame size (binned pixels)
        };

        struct tempconf_t
        {
            bool stabflag;       // true, if temperature stabilization is enabled
            double cold_target;	 // target sensor temperature, C (valid if stabflag is true)
            double cold_current; // current sensor temperature, C
            double hot_current;	 // hot finger temperature, C
            double coolerpower;	 // fraction of cooling system power in use, 0..1 (1 = max. power)
        };

        enum camevent_t
        {
            CE_CANCELWAIT,  // getstate call was cancelled
            CE_CANCELEXP,   // exposure was cancelled
            CE_FRAMECONF,   // frame configuration was changed
            CE_EXPOSTATE,   // exposure state was changed
            CE_FRAMEREADY,  // new frame is ready for clients
            CE_TEMPERAT,    // temperature parameters were changed
            CE_ASYNCERROR,  // asynchronous error occured
            CE_CROSSHAIR,   // crosshair parameters were changed
        };

        enum expostate_t
        {
            ES_IDLE,
            ES_EXPOSURE, // exposure is in progress
            ES_TRANSFER, // data reading is in progress
            ES_INTERVAL, // interval between frames is in progress
        };

        struct adjusttarget_t {
            // reset: if true, use proposed values as new tracking offset parameters,
            // otherwise add proposed values to current tracking offset parameters
            bool reset;
            double ra; // additional offset/rate along ra-axis
            double de; // additional offset/rate along dec-axis
        };

        struct pointtarget_t
        {
            string target;  // target name
            string source;  // target source
            double mjd;     // MJD (UTC)
            double ra;
            double dec;
        };

        sequence<camevent_t> camevent_seq;

        struct getstate_t
        {
            camevent_seq events;       // camera events
            int last_frame_id;         // id of the last frame among ready frames
            expostate_t expostate;     // current expostate
            double expostate_elapsed;  // how long does the current expostate last
            tempconf_t tempconf;       // temperature parameters
        };

        struct crosshair_t
        {
            double x;
            double y;
            double rot;
        };

        interface Camhost {
            // Open camera, return descriptor for other operations.
            //   camera_name: идентификатор камеры,
            //   client_name: идентификатор клиента (для логов),
            //   alive_timeout_s: таймаут контроля активности клиента (секунды).
            // Диспетчер камер ожидает, что каждая программа-клиент после успешного открытия камеры (и
            // получения дескриптора) будет периодически вызывать какие-то функции для работы с камерой
            // (например, getstate() для запроса состояния камеры). Если некоторый клиент не делает
            // никаких вызовов в течение времени 'alive_timeout_s', диспетчер камер объявляет данного
            // клиента не поддерживающим соединение и выполняет принудительное отключение клиента от
            // камеры (т.н. "forced disconnect"). После этого все вызовы с данным дескриптором
            // возвращают ошибку (для продолжения работы клиент должен заново вызвать функцию open() и
            // получить новый дескриптор).
            // Вызов любой функции камеры перезапускает отсчет таймаута 'alive_timeout_s' для данного
            // клиента. Таким образом, чтобы избежать принудительного отключения, клиент должен вызывать
            // функции камеры с интервалом менее 'alive_timeout_s' (например, alive_timeout_s * 0.5). В
            // ситуации, когда никакие активные операции с камерой клиенту не нужны, он может вызвать
            // функцию getstate() с параметром timeout < 0 (timeout < 0 означает, что накопленные
            // события камеры не будут возвращены клиенту и останутся в очереди данного клиента на
            // стороне диспетчера).
            // Пример:
            // При вызове функции open() клиент указал 'alive_timeout_s = 10', после чего он вызывает
            // какие-то функции работы с камерой не реже чем через 5 секунд.
            int open(string camera_name, string client_name, double alive_timeout_s) throws CamError;

            // Close camera (makes descriptor invalid).
            idempotent void close(int descr) throws CamError;

            // Get general camera information.
            idempotent caminfo_t caminfo(int descr) throws CamError;

            // Get/set frame configuration.
            idempotent frameconf_t getconf(int descr) throws CamError;
            idempotent void setconf(int descr, frameconf_t fc) throws CamError;

            // Get current camera state. Wait for camera events if timeout >= 0.
            // Return empty events list if no events (timeout/cancel).
            // Use timeout < 0 to get current camera state without events.
            getstate_t getstate(int descr, double timeout) throws CamError;

            // Abort running getstate function call.
            idempotent void cancel_getstate(int descr);

            // Start exposure. Return next frame_id.
            int start_exposure(int descr, int nframes, double interval) throws CamError;

            // Cancel exposure.
            idempotent void cancel_exposure(int descr) throws CamError;

            // Set cooling system parameters.
            idempotent void set_temp(int descr,
                bool enable_stab, double target_temperature) throws CamError;

            // Get/set crosshair parameters.
            idempotent void set_crosshair(int descr, crosshair_t ch) throws CamError;
            idempotent crosshair_t get_crosshair(int descr) throws CamError;

            // Save arbitrary key-value pair into camhost storage (for given camera).
            idempotent void set_str(int descr, string key, string value) throws CamError;

            // Get saved value for given key from camhost storage (for given camera).
            idempotent string get_str(int descr, string key) throws CamError;

            // Adjust target tracking (send correction to telescope).
            void adjust_target(int descr, adjusttarget_t ofs, adjusttarget_t rates) throws CamError;

            // Mark target position (send data to targetserv).
            idempotent void point_target(int descr, pointtarget_t pt) throws CamError;
        };
    };
};


#endif
