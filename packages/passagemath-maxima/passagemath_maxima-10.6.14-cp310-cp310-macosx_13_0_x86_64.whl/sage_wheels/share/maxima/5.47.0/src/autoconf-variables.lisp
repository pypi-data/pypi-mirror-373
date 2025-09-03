; -*- Lisp -*-
(in-package :maxima)

(defparameter *autoconf-prefix* "/Users/runner/sage-local")
(defparameter *autoconf-exec_prefix* "/Users/runner/sage-local")
(defparameter *autoconf-package* "maxima")
(defparameter *autoconf-version* "5.47.0")
(defparameter *autoconf-libdir* "/Users/runner/sage-local/lib")
(defparameter *autoconf-libexecdir* "/Users/runner/sage-local/libexec")
(defparameter *autoconf-datadir* "/Users/runner/sage-local/share")
(defparameter *autoconf-infodir* "/Users/runner/sage-local/share/info")
(defparameter *autoconf-host* "x86_64-apple-darwin22.6.0")
;; This variable is kept for backwards compatibility reasons:
;; We seem to be in the fortunate position that we sometimes need to check for windows.
;; But at least until dec 2015 we didn't need to check for a specific windows flavour.
(defparameter *autoconf-win32* "false")
(defparameter *autoconf-windows* "false")
(defparameter *autoconf-ld-flags* "")

;; This will be T if this was a lisp-only build
(defparameter *autoconf-lisp-only-build* (eq t 'nil))
 
(defparameter *maxima-source-root* "/Users/runner/sage-local/var/tmp/sage/build/maxima-5.47.0/src")
(defparameter *maxima-default-layout-autotools* "true")
