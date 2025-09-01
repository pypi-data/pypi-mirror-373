; -*- Lisp -*-
(in-package :maxima)

(defparameter *autoconf-prefix* "/host/sage-musllinux_1_2_aarch64")
(defparameter *autoconf-exec_prefix* "/host/sage-musllinux_1_2_aarch64")
(defparameter *autoconf-package* "maxima")
(defparameter *autoconf-version* "5.47.0")
(defparameter *autoconf-libdir* "/host/sage-musllinux_1_2_aarch64/lib")
(defparameter *autoconf-libexecdir* "/host/sage-musllinux_1_2_aarch64/libexec")
(defparameter *autoconf-datadir* "/host/sage-musllinux_1_2_aarch64/share")
(defparameter *autoconf-infodir* "/host/sage-musllinux_1_2_aarch64/share/info")
(defparameter *autoconf-host* "aarch64-unknown-linux-musl")
;; This variable is kept for backwards compatibility reasons:
;; We seem to be in the fortunate position that we sometimes need to check for windows.
;; But at least until dec 2015 we didn't need to check for a specific windows flavour.
(defparameter *autoconf-win32* "false")
(defparameter *autoconf-windows* "false")
(defparameter *autoconf-ld-flags* "")

;; This will be T if this was a lisp-only build
(defparameter *autoconf-lisp-only-build* (eq t 'nil))
 
(defparameter *maxima-source-root* "/host/sage-musllinux_1_2_aarch64/var/tmp/sage/build/maxima-5.47.0/src")
(defparameter *maxima-default-layout-autotools* "true")
