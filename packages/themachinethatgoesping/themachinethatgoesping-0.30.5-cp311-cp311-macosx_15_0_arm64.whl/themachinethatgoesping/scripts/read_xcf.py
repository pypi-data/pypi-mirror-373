# SPDX-FileCopyrightText: 2022 Peter Urban, Sven Schorge, GEOMAR Helmholtz Centre for Ocean
# Research Kiel SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
#
# SPDX-License-Identifier: MPL-2.0

import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import math
from numba import njit
from numba.experimental import jitclass
from time import time
import functools

#from joblib import Parallel, delayed
#import multiprocessing
from multiprocessing import Pool

class nctools:
    @staticmethod
    def walk(top):
        yield top, top.groups, top.__dict__, top.variables
        if top.groups:
            for v in top.groups.values():
                for children in nctools.walk(v):
                    yield children

    @staticmethod
    def ncdispl(file_path):
        with nc.Dataset(file_path) as dataset:
            print(dataset.data_model)


            for root, groups, atributs, variables in nctools.walk(dataset):

                tabs=""
                for t in root.path.split("/"):
                    tabs += "\t"

                print(tabs,root.path)

                if atributs:
                    print(tabs,"\tAtributs")
                    for k,v in atributs.items():
                        print(tabs,"\t\t","{}:\t{}".format(k,v))
                    print()


                if groups:
                    print(tabs,"\tGroups (Sumary)")
                    for g in groups.values():
                        print(tabs,"\t\t",g.path)
                    print()

                if variables:
                    print(tabs,"\tVariables")
                    for k,v in variables.items():

                        print(tabs,"\t\t",k)

                        #print(tabs,"\t\t\tSize:",len(v))
                        #print(tabs,"\t\t\tDatatype:",v.datatype)

                        print(tabs,"\t\t\t\tSize:      \t",len(v),end="")
                        for i,d in enumerate(v.dimensions):
                            if i > 0:
                                r = root
                                while True:
                                    try:
                                        print("x{}".format(r.dimensions[d].size),end="")
                                        break
                                    except:
                                        if r.parent:
                                            r = r.parent
                                        else:
                                            raise RuntimeError("ERROR: Could not find dimension for {}!".format(d))
                        print()



                        print(tabs,"\t\t\t\tDimensions:\t",end="")
                        for i,d in enumerate(v.dimensions):
                            if i > 0: print(end=",")

                            r = root
                            while not d in r.dimensions.keys():
                                if r.parent:
                                    r = r.parent
                                else:
                                    raise RuntimeError("ERROR: Could not find dimension for {}!".format(d))

                            print("", r.path + "/" + d, end="")

                        print()


                        print(tabs,"\t\t\t\tDatatype:  \t",v.datatype)
                    print()




class XFCTools:


    @staticmethod
    @njit
    def sum_beams(ping,
                  reflectivity_count_ping,
                  reflectivity_count_ping_max):

        #print(pingNr)
        pingstack = np.zeros(reflectivity_count_ping_max)
        pingstack.fill(float(np.nan))
        for bnr in range(len(ping)):
            beam = ping[bnr][:reflectivity_count_ping[bnr]]

            #add all samples of the beam to the pingstack
            for snr, s in enumerate(beam):
                if np.isnan(pingstack[snr]):
                    pingstack[snr] = 10 ** (s / 5)
                else:
                    pingstack[snr] += 10 ** (s / 5)

        return pingstack


    @staticmethod
    @njit
    def fill_ping_with_data(ping,pingNr,sample_amplitude,reflectivity_offset,reflectivity_count):
        for bnr in range(len(reflectivity_count[pingNr])):
            ping[bnr][:reflectivity_count[pingNr][bnr]] = sample_amplitude[reflectivity_offset[pingNr][bnr]:
                                                                           reflectivity_offset[pingNr][bnr] + reflectivity_count[pingNr][bnr]]


    @staticmethod
    @njit
    def to_db(rangestack):

        for bnr in range(len(rangestack)):
            for snr in range(len(rangestack[bnr])):
                rangestack[bnr][snr] = 10 * math.log10(rangestack[bnr][snr])

        return rangestack


#@jitclass(spec)
class XFCPingReader(object):
    def __init__(self,file_path):
        with nc.Dataset(file_path) as dataset:
            self.reflectivity_count  = np.array(dataset['/sounder/water_column/rx_info/reflectivity_count'][:])
            self.reflectivity_offset = np.array(dataset['/sounder/water_column/rx_info/reflectivity_offset'][:])
            self.sample_amplitude    = np.array(dataset['/sounder/water_column/rx_info/sample_amplitude'][:])
            # self.reflectivity_count  = dataset['/sounder/water_column/rx_info/reflectivity_count'][:]
            # self.reflectivity_offset = dataset['/sounder/water_column/rx_info/reflectivity_offset'][:]
            # self.sample_amplitude    = dataset['/sounder/water_column/rx_info/sample_amplitude'][:]

            self.numOfPings = int(dataset["/sounder"].dimensions["swath_dim"].size)
            self.numOfBeams = int(dataset["/sounder/water_column"].dimensions["beam_dim"].size)




    def get_ping(self,pingNr):

        max_samples = max(self.reflectivity_count[pingNr])
        max_beams = len(self.reflectivity_count[pingNr])
        ping = np.zeros((max_beams, max_samples))
        ping.fill(float(np.nan))

        XFCTools.fill_ping_with_data(ping, pingNr,
                                          self.sample_amplitude,self.reflectivity_offset,self.reflectivity_count)

        return ping




if __name__ == "__main__":
    time_start = time()

    base_path = "/home/ssd/data/xsf/"
    filename = "0100_20180707_142144.xsf"
    rangestack_name="rangestack.np"

    file_path = base_path + filename

    num_cores = 7

    if True:
        nctools.ncdispl(file_path)

    if False:
        plt.figure()
        with nc.Dataset(file_path) as dataset:
            depth    = dataset['/sounder/bathy/rx_info/depth']

            plt.imshow(depth)

    if False:
        plt.figure()

        xfcreader = XFCPingReader(file_path)

        pingNr = 500

        ping = xfcreader.get_ping(pingNr)

        plt.imshow(ping.transpose())


    if True:
        plt.figure()

        xfcreader = XFCPingReader(file_path)

        max_samples = max([max(samples) for samples in xfcreader.reflectivity_count])
        max_pings   = xfcreader.numOfPings



        rangestack = np.zeros((max_pings, max_samples))
        rangestack.fill(float(np.nan))





        def get_stacked_ping(pingNr : int):
            reflectivity_count_ping = xfcreader.reflectivity_count[pingNr]

            ping = xfcreader.get_ping(pingNr)

            return pingNr, XFCTools.sum_beams(ping, reflectivity_count_ping, max(reflectivity_count_ping))


        multiprocessing = False
        if not multiprocessing:
            for pingNr in tqdm(range(max_pings)):
                _,pingstack = get_stacked_ping(pingNr)
                rangestack[pingNr][:len(pingstack)] = pingstack


        if multiprocessing:
            with Pool(num_cores) as pool:
                for pnr,pingstack in tqdm(pool.imap(get_stacked_ping,range(max_pings))):
                    rangestack[pnr][:len(pingstack)] = pingstack






        rangestack = XFCTools.to_db(rangestack)

        rangestack.dump(base_path + "/" + rangestack_name)
        plt.imshow(rangestack.transpose())




    if False:
        plt.figure()

        rangestack = np.load(base_path + "/" + rangestack_name)
        plt.imshow(rangestack.transpose())



    print("Time: {}s".format(round(time()-time_start)),3)
    plt.show()
