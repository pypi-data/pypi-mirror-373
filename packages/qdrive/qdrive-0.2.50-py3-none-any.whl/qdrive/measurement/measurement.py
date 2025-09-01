'''
Measurement orchestration utilities.

This module provides the `Measurement` context manager which wraps qdrive data
collection into a simple, explicit workflow compatible with QCoDeS
`Parameter`/`MultiParameter` objects. It is intended to be used by the sweep
helpers in `qdrive.measurement.sweeps` and can also be used directly for custom
acquisition loops.

See `qdrive.test.demo_station.get_station()` for mock instruments that can be
used to experiment with the API.
'''
import logging, json

from contextlib import contextmanager

from qdrive.measurement.data_collector import data_collector, from_QCoDeS_parameter
from qdrive import dataset

logger = logging.getLogger(__name__)

class Measurement:
    def __init__(self, name, scope_name = None, silent=False, add_qcodes_snapshot = False):
        '''
        Create a new measurement and its backing dataset.

        Args:
            name (str): Name of the dataset to create.
            scope_name (str): Optional scope name to create the dataset in.
            silent (bool): If True, suppress the start banner and progress bars.
            add_qcodes_snapshot (bool): If True, store the QCoDeS station snapshot
                on the dataset under attribute key 'snapshot'.
        '''
        self.silent = silent

        self.dataset = dataset.create(name, scope_name=scope_name)
        self.add_qcodes_snapshot = add_qcodes_snapshot
        self.m_params = []
    
    def register_m_param(self, m_param, *setpoints):
        '''
        Register a measured parameter and its setpoint parameters.

        Args:
            m_param (qcodes.Parameter): Parameter to be measured (supports
                `Parameter`, `MultiParameter`, `ArrayParameter`, etc.).
            *setpoints (qcodes.Parameter): One or more setpoint parameters that
                define the sweep axes for this measured parameter.
        '''
        self.m_params.append((m_param, setpoints))
    
    @contextmanager
    def measure(self):
        '''
        Context manager that prepares collection and ensures completion.

        Usage:
            with Measurement(...).measure() as collector:
                collector.add_data({...})

        The collector is configured with any previously registered parameters
        via `register_m_param` and will finalize the dataset on exit.
        '''
        if not self.silent:
            print(f'\nStarting measurement with uuid : {self.dataset.uuid} - {self.dataset.name}', flush=True)
        
        if len(self.m_params) == 0:
            raise ValueError("No parameters registered for measurement")
        
        collector = data_collector(self.dataset)
        
        for m_param, setpoints in self.m_params:
            collector += from_QCoDeS_parameter(m_param, setpoints, collector)
        
        if self.add_qcodes_snapshot:
            from qcodes.station import Station
            from qcodes.utils.json_utils import NumpyJSONEncoder

            station = Station()
            collector.set_attr('snapshot', json.dumps(station.snapshot(), cls=NumpyJSONEncoder))

        try:
            yield collector
        except KeyboardInterrupt:
            print('\nMeasurement aborted with keyboard interrupt. Data has been saved.')
        finally:
            collector.complete()
    