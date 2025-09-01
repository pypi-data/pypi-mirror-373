from qcodes.dataset import initialise_or_create_database_at, Measurement, do1d, do2d, dond, do0d, LinSweep
from qcodes import load_or_create_experiment    
import qcodes as qc

from etiket_client.testing.live_data_generation.parameters import *

t_exp = 10

def setupQCoDeS(database_path):
    initialise_or_create_database_at(database_path)
    exp = load_or_create_experiment(
        experiment_name="tutorial_exp",
        sample_name="synthetic data"
    )
    
def generateStation():
    station = qc.Station()
    station.add_component(dac)
    
def _1D_Sweep_0D_param_test():
    n_x_vals = 100
    param = TEST_0D_graph_alike_param(n_x_vals)

    do1d(dac.ch1, 40, 80, n_x_vals, t_exp/n_x_vals, param, measurement_name='1D_Sweep_0D_param_test', show_progress=True, write_period=0.1)

def _2D_Sweep_0D_param_test():
    n_x_vals = 100
    n_y_vals = 150
    param = TEST_0D_2D_graph_alike_param(n_x_vals, n_y_vals)
    
    do2d(dac.ch1, 40, 80, n_x_vals, 0,
         dac.ch2, 20, 45, n_y_vals, t_exp/(n_x_vals * n_y_vals),
         param, show_progress=True, measurement_name='2D_Sweep_0D_param_test', write_period=0.1)

def _3D_Sweep_0D_param_test():
    n_x_vals = 20
    n_y_vals = 50
    n_z_vals = 30
    
    param = TEST_0D_3D_graph_alike_param(n_x_vals, n_y_vals, n_z_vals)

    sweep_1 = LinSweep(dac.ch1, 40, 80, n_x_vals, 0,)
    sweep_2 = LinSweep(dac.ch2, 20, 45, n_y_vals, 0,)
    sweep_3 = LinSweep( dac.ch3, 10, 30, n_z_vals, t_exp/(n_x_vals * n_y_vals * n_z_vals),)

    dond(sweep_1, sweep_2, sweep_3, param ,show_progress=True, measurement_name='3D_Sweep_0D_param_test_qcodes', write_period=0.1)

def _1D_Sweep_1D_array_param_test():
    n_x_vals = 100
    param = TEST_1D_array_parameter_1D(n_x_vals)
    
    do1d(dac.ch1, 40, 80, n_x_vals, t_exp/n_x_vals, param, measurement_name='1D_Sweep_1D_array_param_test_qcodes', show_progress=True, write_period=0.1)

def _0D_sweep_1D_multiparameter_test():
    param = TEST_1D_multi_parameter_4_0D()
    do0d(param, measurement_name='0D_sweep_1D_multiparameter_test_qcodes', write_period=0.1 )

def _0D_sweep_2D_multiparameter_test():
    param = TEST_2D_multi_parameter_4_0D()

    do0d(param, measurement_name='0D_sweep_2D_multiparameter_test_qcodes', write_period=0.1)
    
def _1D_sweep_0D_0D_multiparameter_test():
    n_x_vals = 100
    param1 = TEST_0D_0D_multi_parameter_4_1D(n_x_vals)
    
    do1d(dac.ch1, 40, 80, n_x_vals, t_exp/n_x_vals, param1, show_progress=True, measurement_name='1D_sweep_0D_0D_multiparameter_tes_qcodest', write_period=0.1)

def _1D_sweep_0D_1D_multiparameter_test():
    n_x_vals = 100
    param1 = TEST_0D_1D_multi_parameter_4_1D(n_x_vals)
    
    do1d(dac.ch1, 40, 80, n_x_vals, t_exp/n_x_vals, param1, show_progress=True, measurement_name='1D_sweep_0D_1D_multiparameter_test_qcodes', write_period=0.1)

def _1D_sweep_2D_multiparameter_test():
    n_x_vals = 100
    param1 = TEST_2D_multi_parameter_4_1D(n_x_vals)
    
    do1d(dac.ch1, 40, 80, n_x_vals, t_exp/n_x_vals, param1, show_progress=True, measurement_name='1D_sweep_2D_multiparameter_test_qcodes', write_period=0.1)

def _2D_sweep_0D_0D_multiparameter_test():
    n_x_vals = 100
    n_y_vals = 150
    param1 = TEST_0D_0D_multi_parameter_4_2D(n_x_vals, n_y_vals)
    
    do2d(dac.ch1, 40, 80, n_x_vals, 0,
         dac.ch2, 20, 45, n_y_vals, t_exp/(n_x_vals * n_y_vals),
         param1, show_progress=True , write_period=0.1, measurement_name='2D_sweep_0D_0D_multiparameter_test_qcodes')

def _2D_sweep_0D_1D_multiparameter_test():
    n_x_vals = 100
    n_y_vals = 150
    param1 = TEST_0D_1D_multi_parameter_4_2D(n_x_vals, n_y_vals)
    
    do2d(dac.ch1, 40, 80, n_x_vals, 0,
         dac.ch2, 20, 45, n_y_vals, t_exp/(n_x_vals * n_y_vals),
         param1, show_progress=True, write_period=0.1, measurement_name='2D_sweep_0D_1D_multiparameter_test_qcodes')


def _1D_sweep_1D_parameter_with_setpoints_test():
    n_x_vals = 100
    param = dummySpectrumAnalyzer.spectrum
    
    do1d(dac.ch1, 40, 80, n_x_vals, t_exp/n_x_vals, param,
         measurement_name='1D_Sweep_1D_array_param_test_qcodes',
         show_progress=True, write_period=0.1)

def run_tests():
    database_path = r'QCoDeS_example.db'
    setupQCoDeS(database_path)
    generateStation()
    _1D_Sweep_0D_param_test()
    # _2D_Sweep_0D_param_test()
    # _3D_Sweep_0D_param_test()
    # _1D_Sweep_1D_array_param_test()
    # _0D_sweep_1D_multiparameter_test()
    # _0D_sweep_2D_multiparameter_test()
    # _1D_sweep_0D_0D_multiparameter_test()
    # _1D_sweep_0D_1D_multiparameter_test()
    # _1D_sweep_2D_multiparameter_test()
    # _2D_sweep_0D_0D_multiparameter_test()
    # _2D_sweep_0D_1D_multiparameter_test()
    # _1D_sweep_1D_parameter_with_setpoints_test()
    
if __name__ == '__main__':
    run_tests()