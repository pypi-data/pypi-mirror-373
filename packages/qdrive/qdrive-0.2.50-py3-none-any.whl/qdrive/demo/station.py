'''
Demo QCoDeS instruments and parameters for qdrive measurement examples.

This module exposes `get_station()` which registers mock instruments providing
parameters suitable for demonstrating the helpers in
`qdrive.measurement.sweeps` and the `Measurement` context manager in
`qdrive.measurement.measurement`.

Example:
    from qdrive.test.demo_station import get_station
    from qdrive.measurement.sweeps import do0D, do1D, do2D

    station = get_station()
    p_meas = station.one_D_graph_instr.m_param
    p_set = station.QH_dac.ch1

    # 0D (single shot)
    ds0 = do0D("demo-0D", p_meas)

    # 1D sweep
    ds1 = do1D("demo-1D", p_set, -1.0, 1.0, 51, 0.01, p_meas, reset_param=True)
'''

import numpy as np
import time

from qcodes.instrument import Instrument
from qcodes.parameters import Parameter, MultiParameter
from qcodes.instrument_drivers.mock_instruments import DummyInstrument
from qcodes.station import Station


rng = np.random.default_rng(12345)

def norm(x, mu, sigma):
    return 1/sigma/np.sqrt(2*np.pi)*np.exp(-1/2*((x-mu)/sigma)**2)

def norm2D(x, mu_x, sigma_x, y, mu_y, sigma_y):
    return 1/np.sqrt((sigma_x + sigma_y)**2)/np.sqrt(2*np.pi)*np.exp(-1/2*((x-mu_x)/sigma_x)**2 -1/2*((y-mu_y)/sigma_y)**2)

def oneD_func(n_th_point, n_points):
    x = n_th_point/n_points
    return norm(x, -0.1, 0.1) + norm(x, 0.4, 0.2) + norm(x, 0.1, 0.05) + norm(x, 0.7, 0.8) + rng.random()*0.25

def twoD_func(x, y):
    return norm2D(x, 0.1, 0.2, y, 0.3, 0.1) + norm2D(x, 0.6, 0.05, y, 0.4, 0.06) + rng.random()*0.05

class _0D_m_param(MultiParameter):
    def __init__(self, name, instrument, npt = 500, **kwargs):
        self.npt = npt
        setpt = np.linspace(1, self.npt, self.npt)
        super().__init__(name=name, instrument=instrument, names=('x',), shapes=((self.npt,), ),
                            labels=('x',), units=('V', ),
                            setpoints=((setpt,), ),
                            setpoint_names=(('Frequency',),),
                            setpoint_labels=(('Frequency',),),
                            setpoint_units=(('Hz',),), **kwargs)

    def get_raw(self):
        time.sleep(0.5)
        out = np.linspace(0, 1, self.npt)
        return (oneD_func(out, 1), )

class _1D_m_param(Parameter):
    def __init__(self, name, instrument, label='Current 2', unit='nA',  **kwargs):
        super().__init__(name, instrument=instrument, label=label, unit=unit, **kwargs)
        self._value = -1
        self.n_vals = 500
    
    def get_raw(self):
        self._value += 1
        return oneD_func(self._value, self.n_vals)
    
    def set_shape(self, n_points):
        self.n_vals = n_points
        self._value = -1

class _2D_m_param(Parameter):
    def __init__(self, name, instrument, label='Current 3', unit='nA',  **kwargs):
        super().__init__(name, instrument=instrument, label=label, unit=unit, **kwargs)
        self._value = -1
        self.n_y_vals = 100
        self.n_x_vals = 150
    
    def get_raw(self):
        self._value += 1
        x = self._value % self.n_x_vals
        y = self._value // self.n_x_vals
        return twoD_func(x/self.n_y_vals, y/self.n_x_vals)

    def set_shape(self, n_x_vals, n_y_vals):
        self.n_x_vals = n_x_vals
        self.n_y_vals = n_y_vals
        self._value = -1

class _0D_graph_instr(Instrument):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.add_parameter("_1D_graph_for_0D", parameter_class=_0D_m_param)
        self.m_param = self._1D_graph_for_0D
        
    def get_idn(self):
        return {"model": "_0D_graph_instr",}

class _1D_graph_instr(Instrument):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.add_parameter("_1D_graph_for_1D", parameter_class=_1D_m_param)
        self.m_param = self._1D_graph_for_1D
    
    def set_shape(self, n_points):
        self.m_param.set_shape(n_points)
    
    def get_idn(self):
        return {"model": "_1D_graph_instr",}

class _2D_graph_instr(Instrument):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.add_parameter("_2D_graph_for_2D", parameter_class=_2D_m_param)
        self.m_param = self._2D_graph_for_2D
    
    def set_shape(self, n_points_x, n_points_y):
        self.m_param.set_shape(n_points_x, n_points_y)

    def get_idn(self):
        return {"model": "_2D_graph_instr",}

def get_station():
    station = Station()
    try:
        station.add_component(_0D_graph_instr("zero_D_graph_instr"))
        station.add_component(_1D_graph_instr("one_D_graph_instr"))
        station.add_component(_2D_graph_instr("two_D_graph_instr"))
        station.add_component(DummyInstrument('QH_dac', gates=['ch1', 'ch2', 'ch3', 'ch4']))
    except: pass
    
    return station