from core_tools.data.ds.data_set import load_by_id
from core_tools.data.SQL.connect import SQL_conn_info_local
from core_tools.data.ds.ds2xarray import ds2xarray
from etiket_client.sync.backends.core_tools.real_time_sync.measurement_sync import live_measurement_synchronizer

from etiket_client.sync.backends.core_tools.core_tools_sync_class import CoreToolsConfigData

credentials = CoreToolsConfigData(dbname="core_tools", user="stephan", password="", host="localhost",port= 5432)
SQL_conn_info_local(credentials.host, credentials.port, credentials.user,
                        credentials.password, credentials.dbname, True)

ds_core_tools = load_by_id(6)
print(ds_core_tools.exp_uuid)

lms = live_measurement_synchronizer(ds_core_tools)
if lms.__ready():
    lms.generate_meas_params()
    
    while lms.is_complete() != True:
        lms.sync()
else:
    print("not ready ... :/")

ds_xarray = ds2xarray(ds_core_tools)
lms.ds['Measurement_ct'] = ds_xarray

print("ds creation succesful!")
print(lms.ds['Measurement'].path)
print(lms.ds['Measurement_ct'].path)


print(lms.ds['Measurement_ct'].xarray)
print("\n\n\n\n native \n\n")
print(lms.ds['Measurement'].xarray)
