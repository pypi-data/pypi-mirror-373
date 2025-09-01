from qdrive.measurement.data_collector import data_collector, from_QCoDeS_parameter
from qdrive.dataset.dataset import dataset

from etiket_client.testing.live_data_generation.parameters import *
import time
import numpy as np

t_exp = 10

def _1D_Sweep_0D_param_test():
    n_x_vals = 100
    param = TEST_0D_graph_alike_param(n_x_vals)
    
    ds = dataset.create("1D_Sweep_0D_param_test",)
    dc = data_collector(ds)
    dc += from_QCoDeS_parameter(param, [dac.ch1], dc)
    
    ch1_values = np.linspace(400, 800, n_x_vals)
    
    for i in ch1_values:
        dc.add_data({param : param.get(), dac.ch1 : i})
        time.sleep(t_exp/n_x_vals)
    
    dc.complete()
    
def _2D_Sweep_0D_param_test():
    n_x_vals = 100
    n_y_vals = 150
    param = TEST_0D_2D_graph_alike_param(n_x_vals, n_y_vals)
    
    ds = dataset.create("2D_Sweep_0D_param_test")
    dc = data_collector(ds)
    dc += from_QCoDeS_parameter(param, [dac.ch1, dac.ch2], dc)
    
    ch1_values = np.linspace(400, 800, n_x_vals)
    ch2_values = np.linspace(200, 450, n_y_vals)
    
    for i in ch1_values:
        for j in ch2_values:
            dc.add_data({param : param.get(), dac.ch1 : i, dac.ch2 : j})
            time.sleep(t_exp/(n_x_vals*n_y_vals))
    
    dc.complete()

def _3D_Sweep_0D_param_test():
    n_x_vals = 20
    n_y_vals = 50
    n_z_vals = 30
    
    param = TEST_0D_3D_graph_alike_param(n_x_vals, n_y_vals, n_z_vals)
    ds = dataset.create("3D_Sweep_0D_param_test_qdrive")
    dc = data_collector(ds)
    dc += from_QCoDeS_parameter(param, [dac.ch1, dac.ch2, dac.ch3], dc)
    
    ch1_values = np.linspace(400, 800, n_x_vals)
    ch2_values = np.linspace(200, 450, n_y_vals)
    ch3_values = np.linspace(100, 300, n_z_vals)
    
    for i in ch1_values:
        for j in ch2_values:
            for k in ch3_values:
                dc.add_data({param : param.get(), dac.ch1 : i, dac.ch2 : j, dac.ch3 : k})
                time.sleep(t_exp/(n_x_vals*n_y_vals*n_z_vals))

    dc.complete()

def _1D_Sweep_1D_array_param_test():
    n_x_vals = 100
    param = TEST_1D_array_parameter_1D(n_x_vals)
    
    ds = dataset.create("1D_Sweep_1D_array_param_test")
    dc = data_collector(ds)
    dc += from_QCoDeS_parameter(param, [dac.ch1], dc)
    
    ch1_values = np.linspace(400, 800, n_x_vals)
    
    for i in ch1_values:
        dc.add_data({param : param.get(), dac.ch1 : i})
        time.sleep(t_exp/n_x_vals)
    
    dc.complete()

def _0D_sweep_1D_multiparameter_test():
    param = TEST_1D_multi_parameter_4_0D()
    
    ds = dataset.create("0D_sweep_1D_multiparameter_test_qdrive")
    dc = data_collector(ds)
    dc += from_QCoDeS_parameter(param, [], dc)
    
    dc.add_data({param : param.get()})
    dc.complete()
    
def _0D_sweep_2D_multiparameter_test():
    param = TEST_2D_multi_parameter_4_0D()
    
    ds = dataset.create("0D_sweep_2D_multiparameter_test_qdrive")
    dc = data_collector(ds)
    dc += from_QCoDeS_parameter(param, [], dc)
    
    dc.add_data({param : param.get()})
    dc.complete()

def _1D_sweep_0D_0D_multiparameter_test():
    n_x_vals = 100
    param = TEST_0D_0D_multi_parameter_4_1D(n_x_vals)
    
    ds = dataset.create("1D_sweep_0D_0D_multiparameter_test")
    dc = data_collector(ds)
    dc += from_QCoDeS_parameter(param, [dac.ch1], dc)
    
    ch1_values = np.linspace(400, 800, n_x_vals)
    
    for i in ch1_values:
        dc.add_data({param : param.get(), dac.ch1 : i})
        time.sleep(t_exp/n_x_vals)
    
    dc.complete()

def _1D_sweep_0D_1D_multiparameter_test():
    n_x_vals = 100
    param = TEST_0D_1D_multi_parameter_4_1D(n_x_vals)
    
    ds  = dataset.create("1D_sweep_0D_1D_multiparameter_test")
    dc = data_collector(ds)
    dc += from_QCoDeS_parameter(param, [dac.ch1], dc)
    
    ch1_values = np.linspace(400, 800, n_x_vals)
    
    for i in ch1_values:
        dc.add_data({param : param.get(), dac.ch1 : i})
        time.sleep(t_exp/n_x_vals)
    
    dc.complete()

def _1D_sweep_2D_multiparameter_test():
    n_x_vals = 100
    param = TEST_2D_multi_parameter_4_1D(n_x_vals)
    
    ds = dataset.create("1D_sweep_2D_multiparameter_test_qdrive")
    dc = data_collector(ds)
    dc += from_QCoDeS_parameter(param, [dac.ch1], dc)
    
    ch1_values = np.linspace(400, 800, n_x_vals)
    
    for i in ch1_values:
        dc.add_data({param : param.get(), dac.ch1 : i})
        time.sleep(t_exp/n_x_vals)
    
    dc.complete()

def _2D_sweep_0D_0D_multiparameter_test():
    n_x_vals = 100
    n_y_vals = 150
    param = TEST_0D_0D_multi_parameter_4_2D(n_x_vals, n_y_vals)
    
    ds = dataset.create("2D_sweep_0D_0D_multiparameter_test_qdrive")
    dc = data_collector(ds)
    dc += from_QCoDeS_parameter(param, [dac.ch1, dac.ch2], dc)
    
    ch1_values = np.linspace(400, 800, n_x_vals)
    ch2_values = np.linspace(200, 450, n_y_vals)
    
    for i in ch1_values:
        for j in ch2_values:
            dc.add_data({param : param.get(), dac.ch1 : i, dac.ch2 : j})
            time.sleep(t_exp/(n_x_vals*n_y_vals))
    
    dc.complete()

def _2D_sweep_0D_1D_multiparameter_test():
    n_x_vals = 100
    n_y_vals = 150
    param = TEST_0D_1D_multi_parameter_4_2D(n_x_vals, n_y_vals)
    
    ds = dataset.create("2D_sweep_0D_1D_multiparameter_test")
    dc = data_collector(ds)
    dc += from_QCoDeS_parameter(param, [dac.ch1, dac.ch2], dc)
    
    ch1_values = np.linspace(400, 800, n_x_vals)
    ch2_values = np.linspace(200, 450, n_y_vals)
    
    for i in ch1_values:
        for j in ch2_values:
            dc.add_data({param : param.get(), dac.ch1 : i, dac.ch2 : j})
            time.sleep(t_exp/(n_x_vals*n_y_vals))
    
    dc.complete()


def _1D_sweep_1D_parameter_with_setpoints_test():
    n_x_vals = 100
    param = dummySpectrumAnalyzer.spectrum
    
    ds = dataset.create("1D_Sweep_1D_array_param_test_qdrive")
    dc = data_collector(ds)
    dc += from_QCoDeS_parameter(param, [dac.ch1], dc)
    
    ch1_values = np.linspace(400, 800, n_x_vals)
    
    for i in ch1_values:
        dc.add_data({param : param.get(), dac.ch1 : i})
        time.sleep(t_exp/n_x_vals)
    
    dc.complete()

def run_tests():
    _1D_Sweep_0D_param_test()
    _2D_Sweep_0D_param_test()
    _3D_Sweep_0D_param_test()
    _1D_Sweep_1D_array_param_test()
    _0D_sweep_1D_multiparameter_test()
    _0D_sweep_2D_multiparameter_test()
    _1D_sweep_0D_0D_multiparameter_test()
    _1D_sweep_0D_1D_multiparameter_test()
    _1D_sweep_2D_multiparameter_test()
    _2D_sweep_0D_0D_multiparameter_test()
    _2D_sweep_0D_1D_multiparameter_test()
    _1D_sweep_1D_parameter_with_setpoints_test()