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
import json
import random

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

def get_tremolo_command(tempoFrequency, wetness, phase):
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
(setq lfo {tempoFrequency}) 
(setq wet {wetness})
(setq phase {phase})
(setq wet (/ wet 200.0))
(setq waveform (abs-env *sine-table*))
(defun mod-wave (level)
  (setq phase (- phase 90))
  (sum (- 1 level) 
    (mult level 
      (osc (hz-to-step lfo) 1.0 waveform phase))))

(mult s (mod-wave wet))
'''.format(tempoFrequency=tempoFrequency, wetness=wetness, phase=phase)

def get_variable_tremolo_command(tempoFrequencyStart, tempoFrequencyEnd, wetnessStart, wetnessEnd, phase):
    print('get_variable_tremolo_command: tempoFrequencyStart={tempoFrequencyStart}, tempoFrequencyEnd={tempoFrequencyEnd}, wetnessStart={wetnessStart}, wetnessEnd={wetnessEnd}, phase={phase}'
        .format(tempoFrequencyStart=tempoFrequencyStart, tempoFrequencyEnd=tempoFrequencyEnd, wetnessStart=wetnessStart, wetnessEnd=wetnessEnd, phase=phase))
    return '''(setq wave 0)
(setq phase {phase})
(setq startf {tempoFrequencyStart})
(setq endf {tempoFrequencyEnd})
(setq starta {wetnessStart})
(setq enda {wetnessEnd})

; set tremolo *waveform* 
(setq *waveform* (cond
   ((= wave 0) ; sine
   *sine-table*)
   ((= wave 1) ; triangle
   *tri-table*)
   ((= wave 2) ; sawtooth
   (abs-env (list (pwl 0 -1 .995  1 1 -1 1) (hz-to-step 1.0) t)))
   ((= wave 3) ; inverse sawtooth
   (abs-env (list (pwl 0 1 .995  -1 1 1 1) (hz-to-step 1.0) t)))
   (t ; square
   (abs-env (list (pwl 0 1 .495 1 .5 -1 .995 -1 1 1 1) (hz-to-step 1.0) t)))))

;; Function to generate sweep tone
(defun sweep (sf ef wf ph)
     (mult 0.5 (sum 1.0 (fmlfo (pwlv sf 1.0 ef) *waveform* phase))))

(let* ((starta (/ starta 100.0))
   (enda (/ enda 100.0))
   (wet (pwlv starta 1 enda))
   (dry (sum 1 (mult wet -1))))
   (mult s (sum dry (mult wet (sweep startf endf *waveform* phase)))))
'''.format(tempoFrequencyStart=tempoFrequencyStart, tempoFrequencyEnd=tempoFrequencyEnd, wetnessStart=wetnessStart, wetnessEnd=wetnessEnd, phase=phase)

def do_custom_nyquist(command):
    f = open('C:\Program Files (x86)\Audacity\Plug-Ins\customnyquist.ny', 'w+')
    f.write(command)
    f.close()
    do_command('CustomNyquist:')

current_pos = 0
e=2.7182818284590452353602874713527
def create_standard_segment(length, carrierFrequency, tempoFrequency, wetness):
    global current_pos
    new_pos = current_pos + length
    do_command('Select: Track=0 TrackCount=1 Start=' + str(current_pos) + ' End=' + str(new_pos))
    do_command('Tone: Frequency=' + str(carrierFrequency) + ' Amplitude=1')
    do_custom_nyquist(get_tremolo_command(tempoFrequency, wetness, 0))
    
    do_command('Select: Track=1 TrackCount=1 Start=' + str(current_pos) + ' End=' + str(new_pos))
    do_command('Tone: Frequency=' + str(carrierFrequency) + ' Amplitude=1')
    do_custom_nyquist(get_tremolo_command(tempoFrequency, wetness, 180))
    current_pos = new_pos
    
def create_variable_tremolo_segment(length, carrierFrequency, tempoFrequencyStart, tempoFrequencyEnd, wetnessStart, wetnessEnd):
    global current_pos
    new_pos = current_pos + length
    do_command('Select: Track=0 TrackCount=1 Start=' + str(current_pos) + ' End=' + str(new_pos))
    do_command('Tone: Frequency=' + str(carrierFrequency) + ' Amplitude=1')
    do_custom_nyquist(get_variable_tremolo_command(tempoFrequencyStart, tempoFrequencyEnd, wetnessStart, wetnessEnd, 0))
    
    do_command('Select: Track=1 TrackCount=1 Start=' + str(current_pos) + ' End=' + str(new_pos))
    do_command('Tone: Frequency=' + str(carrierFrequency) + ' Amplitude=1')
    do_custom_nyquist(get_variable_tremolo_command(tempoFrequencyStart, tempoFrequencyEnd, wetnessStart, wetnessEnd, 180))
    current_pos = new_pos
    
def create_variable_carrier_segment(length, carrierFrequencyMain, carrierFrequencyStart, carrierFrequencyEnd, tempoFrequency, wetness):
    global current_pos
    new_pos = current_pos + length
    do_command('NewMonoTrack')
    do_command('Select: Start=0 Length={length}'.format(length=length))

    
    do_command('Select: Track=0 TrackCount=1 Start=' + str(current_pos) + ' End=' + str(new_pos))
    do_command('Chirp: StartFreq={carrierFrequencyStart} EndFreq={carrierFrequencyEnd} StartAmp=1 EndAmp=1'
        .format(carrierFrequencyStart=carrierFrequencyStart, carrierFrequencyEnd=carrierFrequencyEnd))
    do_custom_nyquist(get_tremolo_command(tempoFrequency, wetness, 0))
    
    do_command('Select: Track=1 TrackCount=1 Start=' + str(current_pos) + ' End=' + str(new_pos))
    do_command('Chirp: StartFreq={carrierFrequencyStart} EndFreq={carrierFrequencyEnd} StartAmp=1 EndAmp=1'
        .format(carrierFrequencyStart=carrierFrequencyStart, carrierFrequencyEnd=carrierFrequencyEnd))
    do_custom_nyquist(get_tremolo_command(tempoFrequency, wetness, 180))
    new_pos = current_pos
   


def create_sojourn():
    global sojourndata
    with open('sojourn.json', 'r') as f:
        sojourndata = json.load(f)
        
    do_command('NewMonoTrack')
    do_command('NewMonoTrack')
    current_pos = 0
    for segment in sojourndata['segments']:
        new_pos = current_pos + segment['Length']
        if 'Break' in segment: #fade out the PREVIOUS segment (don't put 'Break' on the first segment!)
            silenceAmount = random.randrange(segment['Break']['Silence'][0], segment['Break']['Silence'][-1])
            do_command('Select: Start={start} End={end} Track=0 TrackCount=2'
                .format(start=current_pos - segment['Break']['FadeOut'], end=current_pos))
            do_command('Fade Out:')
            do_command('Select: Start={start} End={end} Track=0 TrackCount=2'
                .format(start=current_pos, end=current_pos + silenceAmount))
            do_command('Silence:')
            current_pos = current_pos + silenceAmount
           
        do_command('Select: Start={current_pos} End={new_pos} Track=0 TrackCount=1'
            .format(current_pos=current_pos, new_pos=new_pos))
        do_command('Chirp: StartFreq={StartFreq} EndFreq={EndFreq} StartAmp=1 EndAmp=1'
            .format(StartFreq=segment['Carrier'][0], EndFreq=segment['Carrier'][-1]))
        do_custom_nyquist(get_variable_tremolo_command(
            segment['Tempo'][0], segment['Tempo'][-1], segment['Wetness'][0], segment['Wetness'][-1], 0))
            
        do_command('Select: Start={current_pos} End={new_pos} Track=1 TrackCount=1'
            .format(current_pos=current_pos, new_pos=new_pos))
        do_command('Chirp: StartFreq={StartFreq} EndFreq={EndFreq} StartAmp=1 EndAmp=1'
            .format(StartFreq=segment['Carrier'][0], EndFreq=segment['Carrier'][-1]))
        do_custom_nyquist(get_variable_tremolo_command(
            segment['Tempo'][0], segment['Tempo'][-1], segment['Wetness'][0], segment['Wetness'][-1], 180))
        
        if 'Break' in segment: #fade in the start (do this at the end as we've only now generated it)
            do_command('Select: Start={start} End={end} Track=0 TrackCount=2'
                .format(start=current_pos, end=current_pos + segment['Break']['FadeIn']))
            do_command('Fade In:')            
        
        current_pos = new_pos
    
    #do_command('MixAndRenderToNewTrack')
    
create_sojourn()
