import dataclasses
import numpy as np

from typing import List, Any

# TODO, add support for different data types int64, cdouble, bool, ..
# TODO, qcodes does not force the user to define names, labels, units -- add checks // commit bug report.
# TODO add proper support for irregular shaped setvars (local)

@dataclasses.dataclass
class set_var_dynamic:
    name : str
    label : str
    unit : str
    npt : int
    parameter : Any

    @staticmethod
    def from_parameter(param):
        npt = 1
        val = param.get()

        if isinstance(val , (list, tuple)):
            val = np.ndarray(val)
        
        if isinstance(val, np.ndarray):
            if len(val.shape) > 1:
                raise ValueError("Multimensional variable not expected here.")
            npt = val.shape[0]

        return set_var_dynamic(param.name, param.label, param.unit, npt, param)

@dataclasses.dataclass
class set_var_static:
    name : str
    label : str
    unit : str
    data : Any

    def __post_init__(self):
        # TODO add methods that can automatically reduce if appropriate
        # (in old qcodes style this could be multidimensional)
        self.data = np.asarray(self.data)
        if self.data.ndim > 1:
            raise Exception(f"Parameter Error, the setpoints, named {self.name} are expected to be 1 dimensional")
    
    @property
    def npt(self):
        return self.data.size

@dataclasses.dataclass
class get_var:
    name : str
    label : str
    unit : str 
    parameter : Any
    set_vars_dynamic : List[set_var_dynamic]
    # static are supposed to be inner dimension (i.e. related to the dimension of the setvar itselves)
    # Can this be done cleaner? Don't like it.
    set_vars_static : List[set_var_static] = dataclasses.field(default_factory=lambda: [])

    @property
    def result_shape(self):
        return [_set_var.npt for _set_var in self.set_vars_static]

    @property
    def ndim(self):
        return len(self.set_vars_dynamic)

