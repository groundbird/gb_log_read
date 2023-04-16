import numpy as np
import datetime
import pandas as pd

from .logreader.logreader_with_pandas import read_logdata

def read_temp_shield(dt_start, dt_end):
    """
    
    Function for making sheild temperatures.
    
    Parameters
    ----------
    dt_start : datetime.datetime
        start time with timezone
    dt_end   : datetime.datetime
        end time with timezone

    Returns
    -------
    pd.DataFrame
        Temperature dataframe for shield.
    """
    return read_logdata(dt_start, dt_end,
                        file_format = '/data/gb/logdata/thermo/%Y/%m/%Y%m%d_shield.cal')
    

def read_temp_detector(dt_start, dt_end):
    return read_logdata(dt_start, dt_end,
                        file_format = '/data/gb/logdata/thermo/%Y/%m/%Y%m%d_detector.cal')
    
def read_temp_he10(dt_start, dt_end):
    return read_logdata(dt_start, dt_end,
                        file_format = '/data/gb/logdata/thermo/%Y/%m/%Y%m%d_he10.cal')

def read_vacuum(dt_start, dt_end):
    return read_logdata(dt_start, dt_end,
                        file_format = '/data/gb/logdata/vacuum/%Y/%m/%Y%m%d.dat')
    
def read_dome(dt_start, dt_end):
    return read_logdata(dt_start, dt_end,
                        file_format = '/data/gb/logdata/dome/%Y/%m/%Y%m%d_dome.dat')
    
def read_ptc(dt_start, dt_end):
    return read_logdata(dt_start, dt_end,
                        file_format = '/data/gb/logdata/ptc/%Y/%m/%Y%m%d.dat')
    
def read_bme(dt_start, dt_end):
    return read_logdata(dt_start, dt_end,
                        file_format = '/data/gb/logdata/bme280/%Y/%m/%Y%m%d_bme280.raw')
    
def read_bmeenc(dt_start, dt_end):
    return read_logdata(dt_start, dt_end,
                        file_format = '/data/gb/logdata/bme280/%Y/%m/%Y%m%d_bme280enclosure.raw')
    
def read_stella(dt_start, dt_end):
    return read_logdata(dt_start, dt_end,
                        file_format = '/data/gb/logdata/weather/%Y/%m/%Y%m%d_stella.raw',
                        index_for_isotime = 'Unixtime',
                        column_names=['Unixtime', 'UpdateUT', 'Temperature[degC]', 'Humidity[%]','Pressure[hPa]','PeakWindSpeed[m/s]', 'WindSpeed[m/s]','WindDirection[deg]', 'SolarZ[deg]', 'Brightness[Lux]', 'Rain','Dust[m^{-3}]'],
                        utc = True)
    
def read_song(dt_start, dt_end):
    return read_logdata(dt_start, dt_end,
                        file_format = '/data/gb/logdata/weather/%Y/%m/%Y%m%d_song.raw',
                        utc = True)


def read_gaulli(dt_start, dt_end):
    return read_logdata(dt_start, dt_end,
                        file_format = '/data/gb/logdata/weather/%Y/%m/%Y%m%d_gaulli.raw', 
                        column_names=['Localtime', 'Unixtime', 'UpdateUT', 'PWV[mm]', 'PWVmedian(5d)[mm]', 'PWVmean(5d)[mm]', 'PWVstddev(5d)[mm]'])
    
def read_gaulli_final(dt_start, dt_end):
    return read_logdata(dt_start, dt_end,
                        file_format = '/data/gb/logdata/weather/%Y/%m/%Y%m%d_gaulli_final.raw', 
                        column_names=['Localtime', 'Unixtime', 'UpdateUT', 'PWV final[mm]', 'Error[mm]', 'TZD[mm]', 'Pressure[hPa]', 'Temperature[degC]', 'Model/sensor'],
                        utc = True)
    
    
def read_logs(dt_start, dt_end):
    bme = read_bme(dt_start, dt_end)
    bmeenc = read_bmeenc(dt_start, dt_end)
    det = read_temp_detector(dt_start, dt_end)
    he10 = read_temp_he10(dt_start, dt_end).drop([':PU:', ':HD:'], axis = 1)
    shield = read_temp_shield(dt_start, dt_end)
    stella = read_stella(dt_start, dt_end)
    ptc = read_ptc(dt_start, dt_end).drop(['ON/OFF', 'Error_No'], axis = 1)
    
    bmes = pd.merge(bme, bmeenc, on=['Localtime', 'Unixtime'], how='outer', suffixes=['_dome', '_enc'])
    dets = pd.merge(bmes, det, on = ['Localtime', 'Unixtime'], how = 'outer')
    he10s = pd.merge(dets, he10, on = ['Localtime', 'Unixtime'], how = 'outer')
    shields = pd.merge(he10s, shield, on = ['Localtime', 'Unixtime'], how = 'outer')
    stellas = pd.merge(shields, stella, on = ['Localtime', 'Unixtime'], how = 'outer')
    ptcs = pd.merge(stellas, ptc, on = ['Localtime', 'Unixtime'], how = 'outer')
    log = ptcs.sort_index().interpolate().dropna()
    return log
    
    
    
    