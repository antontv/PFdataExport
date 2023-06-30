# -*- coding: utf-8 -*-
'''
Created on Wed Dec  1 08:31:42 2021

@author: anton
'''
import numpy as np

Kundur_elements = {
    'G' : ['s:pt','s:phi','s:speed','t:xds','t:xqs','t:h','m:P:bus1','m:i1i:bus1','m:i1r:bus1','m:u1r:bus1','m:u1i:bus1'],
    'C' : ['m:ur:bus1','m:ui:bus1','m:ir:bus1','m:ii:bus1','m:phiu1:bus1','m:phii:bus1','n:fehz:bus1'],
    'T' : ['m:u1','m:phiu','m:fehz'],
    }

csv_to_PFformat= {
'u1, Magnitude in p.u.' : 'm:u1'
,'U, Angle in deg' : 'm:phiu'
,'Electrical Frequency in Hz' : 'm:fehz'
,'Speed in p.u.' : 's:speed'
,'phi in rad' : 's:phi'
,"xd' in p.u." : 't:xds'
,"xq' in p.u." : 't:xqs'
,'H[Sgn] in s' : 't:h'
,'Turbine Power in p.u.' : 's:pt'
,'Active Power in MW' : 'm:P:bus1'
,'Positive-Sequence Current, Imaginary Part in p.u.' : 'm:i1i:bus1'
,'Positive-Sequence Current, Real Part in p.u.' :  'm:i1r:bus1'
,'Positive-Sequence-Voltage, Real Part in p.u.' : 'm:u1r:bus1'
,'Positive-Sequence-Voltage, Imaginary Part in p.u.' : 'm:u1i:bus1'
,'Voltage, Real Part/Terminal i in p.u.' : 'm:ur:bus1'
,'Voltage, Imaginary Part/Terminal i in p.u.' : 'm:ui:bus1'
,'Current, Real Part/Terminal i in p.u.' : 'm:ir:bus1'
,'Current, Imaginary Part/Terminal i in p.u.' : 'm:ii:bus1'
,'Positive-Sequence-Voltage, Angle/Terminal i in deg' : 'm:phiu1:bus1'
,'Current, Angle/Terminal i in deg' : 'm:phii:bus1'
,'Electrical Frequency/Terminal i in Hz' : 'n:fehz:bus1'
    }

#Classical Architechture
Kundur = { 
    "S_base" : 900,
    'Generators' : [['G1', 0.55, 1, 20, 900, 0.8], ['G2', 0.55, 1, 20, 900, 0.8], ['G3', 0.55, 1, 20, 900, 0.8], ['G4', 0.55, 1, 20, 900, 0.8]],
    'Lines' : [ ['L1-5', 20, 0,	0, 0],
               ['L2-6', 20, 0, 0, 0],
               ['L3-11', 20, 0, 0, 0],
               ['L4-10', 20, 0, 0, 0],
               ['L5-6', 230, 0.146925, 1.469425 , 25*59.54631*1e-6],
               ['L6-7', 230, 0.05877, 0.58777, 10*59.54631*1e-6],
               ['L7-8', 230, 0.64647, 6.46547, 110*59.54631*1e-6],
               ['L7-8(1)', 230, 0.64647, 6.46547, 110*59.54631*1e-6],
               ['L8-9', 230, 0.64647, 6.46547, 110*59.54631*1e-6],
               ['L8-9(1)', 230, 0.64647, 6.46547, 110*59.54631*1e-6],
              ['L9-10', 230, 0.05877, 0.58777, 10*59.54631*1e-6],
              ['L10-11', 230, 0.146925, 1.469425, 25*59.54631*1e-6],],
    'Buses' : ['T1 Terminal', 'T2 Terminal', 'T3 Terminal', 'T4 Terminal', 'T5 Terminal', 'T6 Terminal', 'T7 Terminal', 'T8 Terminal', 'T9 Terminal', 'T10 Terminal', 'T11 Terminal'],
    'Loads' : [['L7', 230, 967, 100],
               ['C7', 230, 12.0344*1e-6],#-200],
               ['L9', 230, 1767, 100],
               ['C9', 230, 21.0602*1e-6]],#-350]],
    'Transformers' : [['T1-5', 900, 0.15, 0],
                      ['T2-6', 900, 0.15, 0],
                      ['T3-11', 900, 0.15, 0],
                      ['T4-10', 900, 0.15, 0]],
    }

files = ['Kundur','9-bus','New England','Nordic44']


