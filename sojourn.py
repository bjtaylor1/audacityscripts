#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests the audacity pipe.

Keep pipe_test.py short!!
You can make more complicated longer tests to test other functionality
or to generate screenshots etc in other scripts.

Make sure Audacity is running first and that mod-script-pipe is enabled
before running this script.

Requires Python 2.7 or later. Python 3 is strongly recommended.

"""

import os
import sys


if sys.platform == 'win32':
    print("pipe-test.py, running on windows")
    TONAME = '\\\\.\\pipe\\ToSrvPipe'
    FROMNAME = '\\\\.\\pipe\\FromSrvPipe'
    EOL = '\r\n\0'
else:
    print("pipe-test.py, running on linux or mac")
    TONAME = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
    FROMNAME = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
    EOL = '\n'

print("Write to  \"" + TONAME +"\"")
if not os.path.exists(TONAME):
    print(" ..does not exist.  Ensure Audacity is running with mod-script-pipe.")
    sys.exit()

print("Read from \"" + FROMNAME +"\"")
if not os.path.exists(FROMNAME):
    print(" ..does not exist.  Ensure Audacity is running with mod-script-pipe.")
    sys.exit()

print("-- Both pipes exist.  Good.")

TOFILE = open(TONAME, 'w')
print("-- File to write to has been opened")
FROMFILE = open(FROMNAME, 'rt')
print("-- File to read from has now been opened too\r\n")


def send_command(command):
    """Send a single command."""
    print("Send: >>> \n"+command)
    TOFILE.write(command + EOL)
    TOFILE.flush()

def get_response():
    """Return the command response."""
    result = ''
    line = ''
    while line != '\n':
        result += line
        line = FROMFILE.readline()
        #print(" I read line:["+line+"]")
    return result

def do_command(command):
    """Send one command, and return the response."""
    send_command(command)
    response = get_response()
    print("Rcvd: <<< \n" + response)
    return response

def quick_test():
    """Example list of commands."""
    do_command('Help: Command=Help')
    do_command('Help: Command="GetInfo"')
    #do_command('SetPreference: Name=GUI/Theme Value=classic Reload=1')

def get_tremolo_command():
    return '''$nyquist plug-in
$version 3
$type process
$preview linear
$name (_ "TremoloSpecific")
$manpage "Tremolo"
$debugbutton disabled
$action (_ "Applying TremoloSpecific...")
$release 2.3.0

(setq wave 0)
(setq lfo 1.0) 
(setq wet 80)
(setq phase 0)
(setq wet (/ wet 200.0))
(setq waveform (abs-env *sine-table*))
(defun mod-wave (level)
  (setq phase (- phase 90))
  (sum (- 1 level) 
    (mult level 
      (osc (hz-to-step lfo) 1.0 waveform phase))))

(mult s (mod-wave wet))


'''

def do_custom_nyquist(command):
    f = open('C:\Program Files (x86)\Audacity\Plug-Ins\customnyquist.py', 'w+')
    f.write(command)
    f.close()
    do_command('CustomNyquist:')

current_pos = 0
def create_standard_segment(length, carrierFrequency, tempoFrequency, wetness):
    new_pos = current_pos + length;
    do_command('Select: Track=0 TrackCount=1 Start=' + str(current_pos) + ' End=' + str(new_pos))
    do_command('Tone: Frequency=' + str(carrierFrequency) + ' Amplitude=0.8')
    
    do_custom_nyquist(get_tremolo_command())
    

def create_sojourn():
    do_command('NewMonoTrack')
    #do_command('NewMonoTrack')
    create_standard_segment(180, 3000, 1, 0.2)
    
create_sojourn()