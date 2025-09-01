from core_tools.sweeps.sweeps import do2D, do1D, do0D, sweep_info, scan_generic

from etiket_client.testing.live_data_generation.parameters import *
from core_tools.data.SQL.connect import set_up_local_storage

t_exp = 10

def setupCoreTools(db_name, username, password):
    set_up_local_storage(username,
                        password, db_name,
                        'test', 'XLD', 'SQ12-1235-205')

def _1D_Sweep_0D_param_test():
    n_x_vals = 100
    param = TEST_0D_graph_alike_param(n_x_vals)

    do1D(dac.ch1, 40, 80, n_x_vals, t_exp/n_x_vals, 
         param, name='1D_Sweep_0D_param_test_core_tools').run()

def _2D_Sweep_0D_param_test():
    n_x_vals = 100
    n_y_vals = 150
    param = TEST_0D_2D_graph_alike_param(n_x_vals, n_y_vals)
    
    do2D(
         dac.ch2, 20, 45, n_y_vals, 0,
         dac.ch1, 40, 80, n_x_vals, t_exp/(n_x_vals * n_y_vals),
         param,  name='2D_Sweep_0D_param_test_core_tools').run()

def _3D_Sweep_0D_param_test():
    n_x_vals = 20
    n_y_vals = 50
    n_z_vals = 30
    
    param = TEST_0D_3D_graph_alike_param(n_x_vals, n_y_vals, n_z_vals)

    sweep_1 = sweep_info(dac.ch1, 40, 80, n_x_vals, 0,)
    sweep_2 = sweep_info(dac.ch2, 20, 45, n_y_vals, 0,)
    sweep_3 = sweep_info( dac.ch3, 10, 30, n_z_vals, t_exp/(n_x_vals * n_y_vals * n_z_vals),)

    scan_generic(sweep_1, sweep_2, sweep_3, param , name='3D_Sweep_0D_param_test_qcodes').run()

def _1D_Sweep_1D_array_param_test():
    n_x_vals = 100
    param = TEST_1D_array_parameter_1D(n_x_vals)
    
    do1D(dac.ch1, 40, 80, n_x_vals, t_exp/n_x_vals,
         param, name='1D_Sweep_1D_array_param_test_core_tools').run()

def _0D_sweep_1D_multiparameter_test():
    param = TEST_1D_multi_parameter_4_0D()
    do0D(param, name='0D_sweep_1D_multiparameter_test_core_tools' ).run()

def _0D_sweep_2D_multiparameter_test():
    param = TEST_2D_multi_parameter_4_0D()

    do0D(param, name='0D_sweep_2D_multiparameter_test_core_tools').run()
    
def _1D_sweep_0D_0D_multiparameter_test():
    n_x_vals = 100
    param1 = TEST_0D_0D_multi_parameter_4_1D(n_x_vals)
    
    do1D(dac.ch1, 40, 80, n_x_vals, t_exp/n_x_vals,
         param1, name='1D_sweep_0D_0D_multiparameter_test_core_tools').run()

def _1D_sweep_0D_1D_multiparameter_test():
    n_x_vals = 100
    param1 = TEST_0D_1D_multi_parameter_4_1D(n_x_vals)
    
    do1D(dac.ch1, 40, 80, n_x_vals, t_exp/n_x_vals, 
         param1, name='1D_sweep_0D_1D_multiparameter_test_core_tools').run()

def _1D_sweep_2D_multiparameter_test():
    n_x_vals = 100
    param1 = TEST_2D_multi_parameter_4_1D(n_x_vals)
    
    do1D(dac.ch1, 40, 80, n_x_vals, t_exp/n_x_vals, 
         param1, name='1D_sweep_2D_multiparameter_test_core_tools').run()

def _2D_sweep_0D_0D_multiparameter_test():
    n_x_vals = 100
    n_y_vals = 150
    param1 = TEST_0D_0D_multi_parameter_4_2D(n_x_vals, n_y_vals)
    
    do2D(dac.ch1, 40, 45, n_y_vals, 0,
         dac.ch2, 20, 80, n_x_vals, t_exp/(n_x_vals * n_y_vals),
         param1, name='2D_sweep_0D_0D_multiparameter_test_core_tools').run()

def _2D_sweep_0D_1D_multiparameter_test():
    n_x_vals = 100
    n_y_vals = 150
    param1 = TEST_0D_1D_multi_parameter_4_2D(n_x_vals, n_y_vals)
    
    do2D(dac.ch2, 20, 45, n_y_vals, 0,
         dac.ch1, 40, 80, n_x_vals, t_exp/(n_x_vals * n_y_vals),
         param1, name='2D_sweep_0D_1D_multiparameter_test_core_tools').run()


def _1D_sweep_1D_parameter_with_setpoints_test():
    n_x_vals = 100
    param = dummySpectrumAnalyzer.spectrum
    
    do1D(dac.ch1, 40, 80, n_x_vals, t_exp/n_x_vals, param,
         name='1D_Sweep_1D_array_param_test_core_tools',).run()


def run_tests():
    db_name = 'core_tools'
    username = 'stephan'
    password = ''
    setupCoreTools(db_name, username, password)

    print(f"running _1D_Sweep_0D_param_test")
    _1D_Sweep_0D_param_test()
    # print(f'running _2D_Sweep_0D_param_test')
    # _2D_Sweep_0D_param_test()
    # print(f'running _3D_Sweep_0D_param_test')
    # _3D_Sweep_0D_param_test()
    # # print(f'running _1D_Sweep_1D_array_param_test')
    # # _0D_sweep_1D_multiparameter_test()
    # print(f'running _0D_sweep_2D_multiparameter_test')
    # _0D_sweep_2D_multiparameter_test()
    # print(f'running _1D_sweep_0D_0D_multiparameter_test')
    # _1D_sweep_0D_0D_multiparameter_test()
    # print(f'running _1D_sweep_0D_1D_multiparameter_test')
    # _1D_sweep_0D_1D_multiparameter_test()
    # print(f'running _1D_sweep_2D_multiparameter_test')
    # _1D_sweep_2D_multiparameter_test()
    # print(f'running _2D_sweep_0D_0D_multiparameter_test')
    # _2D_sweep_0D_0D_multiparameter_test()
    # print(f'running _2D_sweep_0D_1D_multiparameter_test')
    # _2D_sweep_0D_1D_multiparameter_test()
    # # print(f'running _1D_sweep_1D_parameter_with_setpoints_test')
    # # _1D_sweep_1D_parameter_with_setpoints_test()
    print(f'All tests ran successfully!')

if __name__ == '__main__':
    run_tests() 