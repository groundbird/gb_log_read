#!/usr/bin/env python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
import glob
import matplotlib.cm as cm

DIF_DAY_TS = 86400.0
DIF_HOUR_TS = 3600.0
STR_FMT = '%Y-%m-%dT%H:%M:%S'
TEMP_DIR = '/data/gb/logdata/thermo/'

header_he10 = ['Localtime', 'Unixtime', ':HD:', 'He3U_HEAD[K]', 'He3I_HEAD[K]', 'He4_HEAD[K]', ':PU:', 'He4_FilmBurner[K]', 'He4_Pump[K]', 'He3I_Pump[K]', 'He3U_Pump[K]', 'He4_SW[K]', 'He3I_SW[K]', 'He3U_SW[K]']

header_detector = ['Localtime', 'Unixtime', 'detector[K]', '250mK-stage[K]', '350mK-stage[K]']

header_shield = ['Localtime', 'Unixtime', '4K_stage[K]', '4K_he10[K]', '4K_bottom[K]', '4K_mirror[K]', '40K_top[K]', '40K_bottom[K]', 'PTC_40K[K]', 'PTC_4K[K]']

label_he10 = ['He3U_HEAD[K]', 'He3I_HEAD[K]', 'He4_HEAD[K]', 'He4_FilmBurner[K]', 'He4_Pump[K]', 'He3I_Pump[K]', 'He3U_Pump[K]', 'He4_SW[K]', 'He3I_SW[K]', 'He3U_SW[K]']

label_detector = ['detector[K]', '250mK-stage[K]', '350mK-stage[K]']

label_shield = ['4K_stage[K]', '4K_he10[K]', '4K_bottom[K]', '4K_mirror[K]', '40K_top[K]', '40K_bottom[K]', 'PTC_40K[K]', 'PTC_4K[K]']

def get_eachpaths(month_dires, dates_sp):
    he10_paths = []
    detector_paths = []
    shield_paths = []
    for imonth_dire, idate in zip(month_dires, dates_sp):
        try:
            he10_paths.append(glob.glob(imonth_dire + '/' + idate[0] + idate[1] + idate[2] + '_he10.cal')[0])
            detector_paths.append(glob.glob(imonth_dire + '/' + idate[0] + idate[1] + idate[2] + '_detector.cal')[0])
            shield_paths.append(glob.glob(imonth_dire + '/' + idate[0] + idate[1] + idate[2] + '_shield.cal')[0])
        except:
            pass
    return np.array(he10_paths), np.array(detector_paths), np.array(shield_paths)

def get_time(temp):
    """_summary_

    Args:
        temp (read_temp class): class of read_temp

    Returns:
        datetime: datetime when PTC_40K is 270mK
    """
    ind = np.where(np.min(np.abs(temp.temp_shield['PTC_40K[K]'] - 270)) == np.abs(temp.temp_shield['PTC_40K[K]'] - 270))[0][0]
    time290K = temp.datetime_st + datetime.timedelta(hours = temp.elapsed_time_shield[ind])
    time290K
    return time290K

def read_tdata(paths, header):
    datas = [pd.read_table(ipath, sep = '\s+|,', header = None, comment='#', names = header, engine='python') for ipath in paths]
    data = pd.concat(datas)
    return data

class read_temp():
    def __init__(self, st, en = None, temp_dir = TEMP_DIR):
        self.dif_day_ts = DIF_DAY_TS
        self.dif_hour_ts = DIF_HOUR_TS
        self.label_he10 = label_he10
        self.label_detector = label_detector
        self.label_shield = label_shield
        if type(st) == datetime.datetime:
            self.datetime_st = st
        elif type(st) == str:
            self.datetime_st = datetime.datetime.strptime(st, STR_FMT)
        else:
            raise Exception("error : input type is not matched")

        if type(en) == datetime.datetime:
            self.datetime_en = en
        elif type(en) == str:
            self.datetime_en = datetime.datetime.strptime(en, STR_FMT)
        elif en == None:
            self.datetime_en = datetime.datetime.now(tz = datetime.timezone.utc)
        else:
            raise Exception("error : input type is not matched")

        num_dates = int(np.ceil((self.datetime_en.timestamp() - self.datetime_st.timestamp()) / self.dif_day_ts))
        dates = []
        for i in range(num_dates + 1):
            tm_sp = self.datetime_st.timestamp() + i*self.dif_day_ts
            dates.append(datetime.datetime.fromtimestamp(tm_sp).strftime('%Y-%m-%d'))
        dates_sp = [idate.split('T')[0].split('-') for idate in dates]
        month_dires = [os.path.join(temp_dir, idate[0], idate[1]) for idate in dates_sp]
        
        self.he10_paths, self.detector_paths, self.shield_paths = get_eachpaths(month_dires, dates_sp)

        tmp_data_he10 = read_tdata(self.he10_paths, header_he10)
        self.temp_he10 = tmp_data_he10[(tmp_data_he10['Unixtime'] > self.datetime_st.timestamp()) & (tmp_data_he10['Unixtime'] < self.datetime_en.timestamp())].reset_index(drop=True)
        
        tmp_data_detector = read_tdata(self.detector_paths, header_detector)
        self.temp_detector = tmp_data_detector[(tmp_data_detector['Unixtime'] > self.datetime_st.timestamp()) & (tmp_data_detector['Unixtime'] < self.datetime_en.timestamp())].reset_index(drop=True)
        
        tmp_data_shield = read_tdata(self.shield_paths, header_shield)
        self.temp_shield = tmp_data_shield[(tmp_data_shield['Unixtime'] > self.datetime_st.timestamp()) & (tmp_data_shield['Unixtime'] < self.datetime_en.timestamp())].reset_index(drop=True)
        
        # calc elapsed time from start datetime
        self.elapsed_time_he10 = (self.temp_he10['Unixtime'].values - self.temp_he10['Unixtime'].values[0])/self.dif_hour_ts
        self.elapsed_time_detector = (self.temp_detector['Unixtime'].values - self.temp_detector['Unixtime'].values[0])/self.dif_hour_ts
        self.elapsed_time_shield = (self.temp_shield['Unixtime'].values - self.temp_shield['Unixtime'].values[0])/self.dif_hour_ts
        
        # calc elapsed time from PTC_40K of 270K
        datetime_PTC40K_270K = get_time(self)
        self.elapsed_time_PTC_he10 = (self.temp_he10['Unixtime'].values - datetime_PTC40K_270K.timestamp()) /self.dif_hour_ts
        self.elapsed_time_PTC_detector = (self.temp_detector['Unixtime'].values - datetime_PTC40K_270K.timestamp())/self.dif_hour_ts
        self.elapsed_time_PTC_shield = (self.temp_shield['Unixtime'].values - datetime_PTC40K_270K.timestamp())/self.dif_hour_ts
        


class comp_temp(read_temp):
    def __init__(self, runs, run_labels):
        self.temps = [read_temp(irun[0], irun[1]) for irun in runs]
        self.run_labels = run_labels

    def plot_comp_he10(self, log = False, ylim = False, xlim = False):
        self.ylims_he10 = [[0.2,0.40], # He3U_HEAD
                           [0.28,0.40], # He3I_HEAD
                           [0.75,0.85], # He4_HEAD
                           [0.7,6.0], # He4_FilmBurner
                           [1.0,60.0], # He4_Pump
                           [1.0,60.0], # He3I_Pump
                           [1.0,60.0], # He3U_Pump
                           [1.0,30.0], # He4_SW
                           [1.0,30.0], # He3I_SW
                           [1.0,30.0]  # He3U_SW
                           ]
        plt.figure(figsize = (30,20))
        for i, (ilabel, iylim) in enumerate(zip(self.temps[0].label_he10, self.ylims_he10)):
            plt.subplot(3, 4, i+1)
            #plt.plot(self.temp.elapsed_time_he10, self.temp.temp_he10[ilabel], label = self.run_label)
            #plt.plot(self.temp1.elapsed_time_he10, self.temp1.temp_he10[ilabel],'--', label = self.run_label1)
            #plt.plot(self.temp2.elapsed_time_he10, self.temp2.temp_he10[ilabel], '--',label = self.run_label2)
            for j, (itemp, irunlabel) in enumerate(zip(self.temps, self.run_labels)):
                plt.plot(itemp.elapsed_time_PTC_he10, itemp.temp_he10[ilabel], label = irunlabel, c = cm.jet(j/len(self.temps)))
            plt.title(ilabel.split('[')[0])
            plt.ylabel('temperature [K]')
            plt.xlabel('elapsed time [h]')
            plt.legend()
            plt.grid(True)
            if log is True:
                plt.yscale('log')
            if ylim is True:
                plt.ylim(iylim)
            if xlim is not False:
                plt.xlim(xlim)
        plt.tight_layout()
        os.makedirs('fig/', exist_ok=True)
        ntime = datetime.datetime.strftime(datetime.datetime.now(tz = datetime.timezone.utc), STR_FMT)
        ntime = 'he10_'+ ntime + '.jpg'
        save_path = os.path.join('/data/ysueno/home/workspace/script/gb_log_read/fig/', ntime)
        plt.savefig(save_path)
        plt.clf()
        plt.close()

    def plot_comp_det_shield(self, log = False, ylim = False, xlim = False):
        self.ylims_detector = [[0.2, 0.35], # detector
                               [0.2, 0.35], # 250mK_stage
                               [0.3, 0.4] # 350mK_stage
                              ]

        self.ylims_shield = [[3.0, 8.0], # 4K_stage
                             [3.0, 8.0], # 4K_he10
                             [3.0, 8.0], # 4K_bottom
                             [3.0, 8.0], # 4K_mirror
                             [50.0, 70.0], # 40K_top                               
                             [50.0, 70.0], # 40K_bottom
                             [30.0, 50.0], # PTC_40K
                             [2.0, 5.0]  # PTC_4K
                            ]

        plt.figure(figsize = (30,20))
        for i, (ilabel, iylim) in enumerate(zip(self.temps[0].label_detector, self.ylims_detector)):
            plt.subplot(3, 4, i+1)
            #plt.plot(self.temp.elapsed_time_detector, self.temp.temp_detector[ilabel], label = self.run_label)
            #plt.plot(self.temp1.elapsed_time_detector, self.temp1.temp_detector[ilabel], '--',label = self.run_label1)
            #plt.plot(self.temp2.elapsed_time_detector, self.temp2.temp_detector[ilabel], '--',label = self.run_label2)
            for j, (itemp, irun_label) in enumerate(zip(self.temps, self.run_labels)):
                plt.plot(itemp.elapsed_time_PTC_detector, itemp.temp_detector[ilabel], label = irun_label, c = cm.jet(j/len(self.temps)))
            plt.title(ilabel.split('[')[0])
            plt.ylabel('temperature [K]')
            plt.xlabel('elapsed time [h]')
            plt.legend()
            plt.grid(True)
            if log is True:
                plt.yscale('log')
            if ylim is True:
                plt.ylim(iylim)
            if xlim is not False:
                plt.xlim(xlim)
                
                
        for i, (ilabel, iylim) in enumerate(zip(self.temps[0].label_shield, self.ylims_shield)):
            plt.subplot(3, 4, i+4)
            #plt.plot(self.temp.elapsed_time_shield, self.temp.temp_shield[ilabel],label = self.run_label)
            #plt.plot(self.temp1.elapsed_time_shield, self.temp1.temp_shield[ilabel], '--',label = self.run_label1)
            #plt.plot(self.temp2.elapsed_time_shield, self.temp2.temp_shield[ilabel], '--',label = self.run_label2)
            for j, (itemp, irun_label) in enumerate(zip(self.temps, self.run_labels)):
                plt.plot(itemp.elapsed_time_PTC_shield, itemp.temp_shield[ilabel],label = irun_label, c = cm.jet(j/len(self.temps)))
            plt.title(ilabel.split('[')[0])
            plt.ylabel('temperature [K]')
            plt.xlabel('elapsed time [h]')
            plt.legend()
            plt.grid(True)
            if log is True:
                plt.yscale('log')
            if ylim is True:
                plt.ylim(iylim)
            if xlim is not False:
                plt.xlim(xlim)
        plt.tight_layout()
        os.makedirs('fig/', exist_ok=True)
        ntime = datetime.datetime.strftime(datetime.datetime.now(tz = datetime.timezone.utc), STR_FMT)
        ntime = 'det_shield_' + ntime + '.jpg'
        save_path = os.path.join('/data/ysueno/home/workspace/script/gb_log_read/fig/', ntime)
        plt.savefig(save_path)
        plt.clf()
        plt.close()


def main(log, ylim, xlen, xlim):
    st_202103 = datetime.datetime(2021, 3, 19, 21, 33, 00)
    en_202103 = st_202103 + datetime.timedelta(hours = xlen)
    st_202107 = datetime.datetime(2021, 7, 6, 20, 27, 00)
    en_202107 = st_202107 + datetime.timedelta(hours = xlen)
    st_202112 = datetime.datetime(2021, 12, 23, 19, 45, 00)
    en_202112 = st_202112 + datetime.timedelta(hours = xlen)
    st_202208 = datetime.datetime(2022, 8, 26, 21, 00, 00)
    en_202208 = st_202208 + datetime.timedelta(hours = xlen)
    st_202301 = datetime.datetime(2023, 1, 13, 7, 00, 00)
    en_202301 = st_202301 + datetime.timedelta(hours = xlen)
    st_202305 = datetime.datetime(2023, 5, 31, 7, 00, 00)
    en_202305 = st_202305 + datetime.timedelta(hours = xlen)


    run_202103 = [st_202103, en_202103]
    run_202107 = [st_202107, en_202107]
    run_202112 = [st_202112, en_202112]
    run_202208 = [st_202208, en_202208]
    run_202301 = [st_202301, en_202301]    
    run_202305 = [st_202305, en_202305]    
    run_labels = ['202103', '202107', '202112', '202208', '202301', '202305']  
    runs = [run_202103, run_202107, run_202112, run_202208, run_202301, run_202305]  
    comp_data = comp_temp(runs, run_labels = run_labels)    
    comp_data.plot_comp_he10(log = log, ylim = ylim, xlim = xlim)
    comp_data.plot_comp_det_shield(log = log, ylim = ylim, xlim = xlim)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-log', type=bool, default = False,
                        help='plot with log scale. Default = False')
    parser.add_argument('-ylim', type = bool, default = False,
                        help='plot with the limited scale. Default = False')
    parser.add_argument('-xlen', type = int, default = 120,
                    help='length of the xscale [h]. Default = 120 [h]')
    parser.add_argument('-xlim', type=float, nargs='+', default = False,
                        help='limit of the xscale [h]. Default = [0,120] [h]')
    args = parser.parse_args()
    print(args.xlim)
    main(log = args.log, ylim = args.ylim, xlen = args.xlen, xlim = args.xlim)
