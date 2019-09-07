$nyquist plug-in
$version 3
$type process
$preview linear
$name (_ "TremoloSpecific")
$manpage "Tremolo"
$debugbutton disabled
$action (_ "Applying TremoloSpecific...")
$release 2.3.0

(setq wave 0) ; sine
(setq lfo 1.0) 
(setq wet 80)
(setq phase 0)

; Convert % to linear
(setq wet (/ wet 200.0))

; set tremolo waveform 
(setq waveform (abs-env *sine-table*))

;;; Generate modulation wave
(defun mod-wave (level)
  (setq phase (- phase 90))
  (sum (- 1 level) 
    (mult level 
      (osc (hz-to-step lfo) 1.0 waveform phase))))

(mult s (mod-wave wet))
