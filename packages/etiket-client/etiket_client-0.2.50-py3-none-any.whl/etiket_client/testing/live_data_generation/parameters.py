from qcodes.parameters import ArrayParameter, ManualParameter, MultiParameter, Parameter, ParameterWithSetpoints
from qcodes.tests.instrument_mocks import DummyInstrument
from qcodes import Instrument
from qcodes.validators import Arrays, Numbers

import numpy as np

dac = DummyInstrument('dac', gates=['ch1', 'ch2', 'ch3', 'ch4'])

rng = np.random.default_rng(seed=42)
import time
def norm(x, mu, sigma):
    return 1/sigma/np.sqrt(2*np.pi)*np.exp(-1/2*((x-mu)/sigma)**2)

def norm2D(x, mu_x, sigma_x, y, mu_y, sigma_y):
    return 1/np.sqrt((sigma_x + sigma_y)**2)/np.sqrt(2*np.pi)*np.exp(-1/2*((x-mu_x)/sigma_x)**2 -1/2*((y-mu_y)/sigma_y)**2)

def norm3D(x, mu_x, sigma_x, y, mu_y, sigma_y, z, mu_z, sigma_z):
    return (1/np.sqrt((sigma_x + sigma_y + sigma_z)**2)/np.sqrt(2*np.pi)*
                np.exp(-1/2*((x-mu_x)/sigma_x)**2
                       -1/2*((y-mu_y)/sigma_y)**2
                       -1/2*((z-mu_z)/sigma_z)**2)
            )
    

def oneD_func(n_th_point, n_points):
    x = n_th_point/n_points
    return norm(x, -0.1, 0.1) + norm(x, 0.4, 0.2) + norm(x, 0.1, 0.05) + norm(x, 0.7, 0.8) + rng.random()*0.25

def twoD_func(x, y):
    return norm2D(x, 0.1, 0.2, y, 0.3, 0.1) + norm2D(x, 0.6, 0.05, y, 0.4, 0.06) + rng.random()*0.05


def threeD_func(x, y, z):
    return norm3D(x, 0.1, 0.2, y, 0.3, 0.1, z, 0.2, 0.1) + norm3D(x, 0.6, 0.05, y, 0.4, 0.06, z, 0.1, 0.6) + rng.random()*0.05
    

class TEST_0D_counter(Parameter):
    def __init__(self, name, label='Current 1', unit='nA',  **kwargs):
        super().__init__(name, instrument=None, label=label, unit=unit)
        self._value = -1
    
    def get_raw(self):
        self._value += 1
        return self._value

class TEST_0D_graph_alike_param(Parameter):
    def __init__(self, n_vals, name="name", label='Current 2', unit='nA',  **kwargs):
        super().__init__(name, instrument=None, label=label, unit=unit)
        self._value = -1
        self.n_vals = n_vals
    
    def get_raw(self):
        self._value += 1
        return oneD_func(self._value, self.n_vals)

class TEST_0D_2D_graph_alike_param(Parameter):
    def __init__(self, n_x_vals, n_y_vals, name='name', label='Current 3', unit='nA',  **kwargs):
        super().__init__(name, instrument=None, label=label, unit=unit)
        self._value = -1
        self.n_x_vals = n_x_vals
        self.n_y_vals = n_y_vals
    
    def get_raw(self):
        self._value += 1
        x = self._value % self.n_y_vals
        y = self._value // self.n_y_vals
        return twoD_func(x/self.n_x_vals, y/self.n_y_vals)

class TEST_0D_3D_graph_alike_param(Parameter):
    def __init__(self, n_x_vals, n_y_vals, n_z_vals, name ='name', label='Current 4', unit='nA',  **kwargs):
        super().__init__(name, instrument=None, label=label, unit=unit)
        self._value = -1
        self.n_x_vals = n_x_vals
        self.n_y_vals = n_y_vals
        self.n_z_vals = n_z_vals
    
    def get_raw(self):
        self._value += 1
        x = self._value % self.n_z_vals
        y = (self._value // self.n_z_vals) % self.n_y_vals
        z = self._value // (self.n_z_vals*self.n_y_vals)
        return threeD_func(x/self.n_x_vals, y/self.n_y_vals, z/self.n_z_vals)
    
class TEST_1D_array_parameter_1D(ArrayParameter):
    def __init__(self, n_x_vals):
        self.n_x_vals = n_x_vals
        self.N = 7
        self._value = -1
        setpoints = (np.linspace(0, 1, self.N),)

        super().__init__(name='name',
                         instrument=None,
                         setpoints=setpoints,
                         shape=(self.N,),
                         label='Noisy spectrum',
                         unit='V/sqrt(Hz)',
                         setpoint_names=('Frequency',),
                         setpoint_labels=('Frequency',),
                         setpoint_units=('Hz',))

    def get_raw(self):
        self._value += 1
        v= np.linspace(0, 1, self.N)
        return v*oneD_func(self._value, self.n_x_vals)

class TEST_1D_multi_parameter_4_0D(MultiParameter):
    def __init__(self, npt = 50):
        self.npt = npt
        setpt = np.linspace(1, self.npt, self.npt)
        super().__init__(name='name', names=('x',), shapes=((self.npt,), ),
                         labels=('x',), units=('V', ),
                            setpoints=((setpt,), ),
                            setpoint_names=(('Frequency',),),
                            setpoint_labels=(('Frequency',),),
                            setpoint_units=(('Hz',),))

    def get_raw(self):
        time.sleep(0.5)
        out = np.linspace(0, 1, self.npt)
        return (oneD_func(out, 1), )

class TEST_2D_multi_parameter_4_0D(MultiParameter):
    def __init__(self, n_x = 15, n_y = 20):
        self.npt_x = n_x
        self.npt_y = n_y
        setpt_x = np.linspace(1, self.npt_x, self.npt_x)
        setpt_y = np.linspace(1+10, self.npt_y+10, self.npt_y)
        super().__init__(name='name',
                         names=('x_name',), shapes=((self.npt_x, self.npt_y), ),
                         labels=('x_label', ), units=('V',),
                         setpoints=((setpt_x, tuple(setpt_y),), ),
                         setpoint_names=(('setpoint_1_name', 'setpoint_2_name'),),
                         setpoint_labels=(('setpoint_1', 'setpoint_2'),),
                         setpoint_units=(('unit_1', 'unit_2'),))
    
    def get_raw(self):
        x_mat = np.repeat(np.linspace(0, 1, self.npt_x), self.npt_y).reshape(self.npt_x, self.npt_y)
        y_mat = np.repeat(np.linspace(0, 1, self.npt_y), self.npt_x).reshape(self.npt_y, self.npt_x).T

        return (twoD_func(x_mat, y_mat), )

class TEST_0D_0D_multi_parameter_4_1D(MultiParameter):
    def __init__(self, npt):
        self._value = -1
        self.npt = npt
        super().__init__(name='name', names=('x', 'y'), shapes=((), () ),
                         labels=('x', 'y'), units=('V', 'V'), 
                         setpoints=((), ()),)

    def get_raw(self):
        self._value += 1
        return (oneD_func(self._value, self.npt), -oneD_func(self._value, self.npt),)
    
class TEST_0D_1D_multi_parameter_4_1D(MultiParameter):
    def __init__(self, npt):
        self._value = -1
        self.npt = npt
        self.N = 7
        
        super().__init__(name='name', names=('x', 'y'), shapes=((), (self.N,)),
                         labels=('x', 'y'), units=('V', 'V'),
                         setpoints=((), (np.linspace(0, 1, self.N),)),
                         setpoint_names=((), ('Frequency',)),
                         setpoint_labels=((), ('Frequency',)),   
                         setpoint_units=((), ('Hz',)))

    def get_raw(self):
        self._value += 1
        k = np.arange(0.1, 1, 1/self.N)
        return (oneD_func(self._value, self.npt),
                k*oneD_func(self._value, self.npt))

class TEST_2D_multi_parameter_4_1D(MultiParameter):
    def __init__(self, npt):
        self._value = -1
        self.npt = npt
        self.Nx = 7
        self.Ny = 5        
        super().__init__(name='name', names=('x', ), shapes=((self.Nx,self.Ny), ),
                         labels=('x',), units=('V', ),
                         setpoints=((np.linspace(0, 1, self.Nx),np.linspace(0, 1, self.Ny),), ),
                         setpoint_names=(('Frequency1', 'frequency2'),),
                         setpoint_labels=(('Frequency1', 'frequency2'),), 
                         setpoint_units=(('Hz', 'Hz'),))
    
    def get_raw(self):
        self._value += 1
        out = np.random.rand(self.Nx,self.Ny)/10
        out1 = self._value*np.arange(0, self.Nx*self.Ny).reshape(self.Nx, self.Ny)/self.Nx/self.Ny
        return (oneD_func(self._value, self.npt) + out + out1, )

class TEST_0D_0D_multi_parameter_4_2D(MultiParameter):
    def __init__(self, n_pts_x, n_pts_y):
        self._value = -1
        self.n_pts_y = n_pts_y
        self.n_pts_x = n_pts_x
        super().__init__(name='name', names=('x', 'y'), shapes=((), ()),
                         labels=('x', 'y'), units=('V', 'V'),
                         setpoints=((), ()),)

    def get_raw(self):
        self._value += 1
        current_x = self._value % self.n_pts_y
        current_y = self._value // self.n_pts_y
        
        return (twoD_func(current_x/self.n_pts_x, current_y/self.n_pts_y),
                - 0.5*twoD_func(current_x/self.n_pts_x, current_y/self.n_pts_y))


class TEST_0D_1D_multi_parameter_4_2D(MultiParameter):
    def __init__(self, n_pts_x, n_pts_y):
        self._value = -1
        self.n_pts_y = n_pts_y
        self.n_pts_x = n_pts_x
        self.N = 7
        
        super().__init__(name='name', names=('x', 'y'), shapes=((), (self.N,)),
                         labels=('x', 'y'), units=('V', 'V'),
                         setpoints=((), (np.linspace(0, 1, self.N),)),
                         setpoint_names=((), ('Frequency',)),
                         setpoint_labels=((), ('Frequency',)),   
                         setpoint_units=((), ('Hz',)))

    def get_raw(self):
        self._value += 1
        current_x = self._value % self.n_pts_y
        current_y = self._value // self.n_pts_y
        k = np.arange(0.1, 1, 1/self.N)
        return (twoD_func(current_x/self.n_pts_x, current_y/self.n_pts_y),
                k*twoD_func(current_x/self.n_pts_x, current_y/self.n_pts_y))


class DummySpectrumAnalyzer(Instrument):

    def __init__(self, name, **kwargs):

        super().__init__(name, **kwargs)

        self.add_parameter('freq_axis',
                           unit='Hz',
                           label='Freq Axis',
                           parameter_class=GeneratedSetPoints,
                           startparam=self.f_start,
                           stopparam=self.f_stop,
                           numpointsparam=self.n_points,
                           vals=Arrays(shape=(self.n_points.get_latest,)))

        self.add_parameter('spectrum',
                   unit='dBm',
                   setpoints=(self.freq_axis,),
                   label='Spectrum',
                   parameter_class=DummyArray,
                   vals=Arrays(shape=(self.n_points.get_latest,)))


class GeneratedSetPoints(Parameter):
    """
    A parameter that generates a setpoint array from start, stop and num points
    parameters.
    """

    def __init__(self, startparam, stopparam, numpointsparam, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._startparam = startparam
        self._stopparam = stopparam
        self._numpointsparam = numpointsparam

    def get_raw(self):
        return np.linspace(self._startparam(), self._stopparam(),
                              self._numpointsparam())


class DummyArray(ParameterWithSetpoints):

    def get_raw(self):
        npoints = self.root_instrument.n_points.get_latest()
        return np.random.rand(npoints)


class DummySpectrumAnalyzer(Instrument):
    def __init__(self, name, **kwargs):

        super().__init__(name, **kwargs)

        self.add_parameter('f_start',
                           initial_value=0,
                           unit='Hz',
                           label='f start',
                           vals=Numbers(0,1e3),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('f_stop',
                           unit='Hz',
                           label='f stop',
                           initial_value=1e3,
                           vals=Numbers(1,1e3),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('n_points',
                           unit='',
                           initial_value=10,
                           vals=Numbers(1,1e3),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('freq_axis',
                           unit='Hz',
                           label='Freq Axis',
                           parameter_class=GeneratedSetPoints,
                           startparam=self.f_start,
                           stopparam=self.f_stop,
                           numpointsparam=self.n_points,
                           vals=Arrays(shape=(self.n_points.get_latest,)))

        self.add_parameter('spectrum',
                   unit='dBm',
                   setpoints=(self.freq_axis,),
                   label='Spectrum',
                   parameter_class=DummyArray,
                   vals=Arrays(shape=(self.n_points.get_latest,)))
        
dummySpectrumAnalyzer = DummySpectrumAnalyzer('dummy_spectrum_analyzer')


# from qcodes.parameters import ArrayParameter, MultiParameter
# import numpy as np

# class TEST_1D_array_parameter_1D(ArrayParameter):
#     def __init__(self, n_x_vals):
#         self.n_x_vals = n_x_vals
#         self.N = 7
#         self._value = -1
#         setpoints = (np.linspace(0, 1, self.N),)

#         super().__init__(name='name',
#                          instrument=None,
#                          setpoints=setpoints,
#                          shape=(self.N,),
#                          label='Noisy spectrum',
#                          unit='V/sqrt(Hz)',
#                          setpoint_names=('Frequency',),
#                          setpoint_labels=('Frequency',),
#                          setpoint_units=('Hz',))

#     def get_raw(self):
#         self._value += 1
#         v= np.linspace(0, 1, self.N)
#         return v  + v/2 *1j

class AddPhaseAndMagnitude(MultiParameter):
    '''
    This parameter adds phase and magnitude to a reference parameter.
    
    Usage: reference_with_phase_and_magnitude = AddPhaseAndMagnitude(my_instrument.reference_parameter)
    There reference_with_phase_and_magnitude can be used in the typical do1D/do2D/other measurement functions.
    '''
    def __init__(self, reference_parameter : ArrayParameter):
        self.reference_parameter = reference_parameter
        super().__init__(name=reference_parameter.name + '_with_phase_and_magnitude',
                            names=(reference_parameter.name, 'phase', 'magnitude'),
                            shapes=(reference_parameter.shape, reference_parameter.shape, reference_parameter.shape),
                            labels=(reference_parameter.label, 'phase', 'magnitude'),
                            units=(reference_parameter.unit, 'rad', 'V'),
                            setpoints=(reference_parameter.setpoints, reference_parameter.setpoints, reference_parameter.setpoints),
                            setpoint_names=(reference_parameter.setpoint_names, reference_parameter.setpoint_names, reference_parameter.setpoint_names),
                            setpoint_labels=(reference_parameter.setpoint_labels, reference_parameter.setpoint_labels, reference_parameter.setpoint_labels),
                            setpoint_units=(reference_parameter.setpoint_units, reference_parameter.setpoint_units, reference_parameter.setpoint_units))

    def get_raw(self):
        return (self.reference_parameter(), np.angle(self.reference_parameter()), np.abs(self.reference_parameter()))