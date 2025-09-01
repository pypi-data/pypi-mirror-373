"""
Sweep helpers built on top of `qdrive.measurement.measurement.Measurement`.

This module provides convenience functions to perform common 0D/1D/2D scans
with QCoDeS `Parameter` objects and record results into a qdrive `dataset`.

See `qdrive.test.demo_station.get_station()` for mock instruments you can use
to try these functions interactively.
"""

import logging, time, tqdm
import numpy as np

from qdrive.measurement.measurement import Measurement
from qdrive.dataset.dataset import dataset
from qcodes.instrument.parameter import Parameter

logger = logging.getLogger(__name__)

def do0D(name : str, *m_instr, silent=False, add_qcodes_snapshot=False) -> dataset:
    '''
    Perform a 0D measurement (single acquisition) and save to a dataset.

    Args:
        name (str): Name of the dataset to create.
        m_instr (*qcodes.Parameter): One or more measured parameters to read.
        silent (bool): If True, suppress banners and progress bars.
        add_qcodes_snapshot (bool): If True, attach the QCoDeS station snapshot
            to the dataset attributes under key 'snapshot'.

    Returns:
        qdrive.dataset.dataset: The created dataset containing one record.
    '''
    m = Measurement(name, silent=silent, add_qcodes_snapshot=add_qcodes_snapshot)
    for instr in m_instr:
        m.register_m_param(instr)
    with m.measure() as collector:
        for instr in m_instr:
            collector.add_data({instr: instr.get()})
    return m.dataset 

def do1D(name : str, param: Parameter, start, stop, n_points, delay, *m_instr,
            reset_param=False, silent=False, add_qcodes_snapshot=False) -> dataset:
    '''
    Perform a 1D sweep over a single setpoint parameter.

    Args:
        name (str): Name of the dataset to create.
        param (qcodes.Parameter): Setpoint parameter to sweep.
        start (float): Start value (inclusive).
        stop (float): Stop value (inclusive).
        n_points (int): Number of points in the sweep.
        delay (float): Seconds to wait after setting the parameter, before readout.
        m_instr (*qcodes.Parameter): Measured parameters to read per point.
        reset_param (bool): If True, restore `param` to its original value
            after completion.
        silent (bool): If True, suppress banners and progress bars.
        add_qcodes_snapshot (bool): If True, attach the QCoDeS station snapshot.

    Returns:
        qdrive.dataset.dataset: The created dataset containing the full 1D scan.
    '''
    m = Measurement(name, silent=silent, add_qcodes_snapshot=add_qcodes_snapshot)
    for instr in m_instr:
        m.register_m_param(instr, param)

    sweep_values = np.linspace(start, stop, n_points)

    initial_value_param = param.get()
    
    try:
        with m.measure() as collector:
            pbar = tqdm.tqdm(total=n_points, desc="Measurement Progress", disable=silent)
            for value in sweep_values:
                param.set(value)
                
                if delay and delay > 0:
                    time.sleep(delay)
                
                m_instr_values = {}
                for instr in m_instr:
                    m_instr_values[instr] = instr.get()
                collector.add_data({param: value, **m_instr_values})
                pbar.update(1)
                
    finally:
        if reset_param:
            param.set(initial_value_param)

    return m.dataset

def do2D(name : str, param_1: Parameter, start_1 : float, stop_1 : float, n_points_1 : int, delay_1 : float,
            param_2: Parameter, start_2 : float, stop_2 : float, n_points_2 : int, delay_2 : float, *m_instr,
            reset_param=False, silent=False, add_qcodes_snapshot=False) -> dataset:
    '''
    Perform a 2D sweep over two setpoint parameters (nested loop).

    Args:
        name (str): Name of the dataset to create.
        param_1 (qcodes.Parameter): Outer-loop setpoint parameter.
        start_1 (float): Start value for `param_1` (inclusive).
        stop_1 (float): Stop value for `param_1` (inclusive).
        n_points_1 (int): Number of points for `param_1`.
        delay_1 (float): Seconds to wait after setting `param_1`.
        param_2 (qcodes.Parameter): Inner-loop setpoint parameter.
        start_2 (float): Start value for `param_2` (inclusive).
        stop_2 (float): Stop value for `param_2` (inclusive).
        n_points_2 (int): Number of points for `param_2`.
        delay_2 (float): Seconds to wait after setting `param_2`.
        m_instr (*qcodes.Parameter): Measured parameters to read per point.
        reset_param (bool): If True, restore both setpoint parameters to their
            original values after completion.
        silent (bool): If True, suppress banners and progress bars.
        add_qcodes_snapshot (bool): If True, attach the QCoDeS station snapshot.

    Returns:
        qdrive.dataset.dataset: The created dataset containing the full 2D scan.
    '''
    m = Measurement(name, silent=silent, add_qcodes_snapshot=add_qcodes_snapshot)
    for instr in m_instr:
        m.register_m_param(instr, param_1, param_2)

    sweep_outer = np.linspace(start_1, stop_1, n_points_1)
    sweep_inner = np.linspace(start_2, stop_2, n_points_2)

    initial_value_param_1 = param_1.get()
    initial_value_param_2 = param_2.get()

    try:
        with m.measure() as collector:
            pbar = tqdm.tqdm(total=n_points_1 * n_points_2, desc="Measurement Progress", disable=silent)
            for s_outer in sweep_outer:
                param_1.set(s_outer)
                if delay_1 > 0:
                    time.sleep(delay_1)
                for s_inner in sweep_inner:
                    param_2.set(s_inner)
                    if delay_2 > 0:
                        time.sleep(delay_2)
                    m_instr_values = {}
                    for instr in m_instr:
                        m_instr_values[instr] = instr.get()
                    collector.add_data({param_1: s_outer, param_2: s_inner, **m_instr_values})
                    pbar.update(1)
    finally:
        if reset_param:
            param_1.set(initial_value_param_1)
            param_2.set(initial_value_param_2)

    return m.dataset