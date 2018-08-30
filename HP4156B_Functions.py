import visa,time, sys, io, os, math
from hp4156b_class import hp4156c
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as sm
import numpy as np

#import parameter_analyser_hp4156b as pa

def Two_Terminal_IV_Plot(df_data, fig_name, Y_Str="VF", X_Str="IF", fit="NO"):
    YY = Y_Str
    XX = X_Str
    
    X= np.array(df_data[XX].tolist())
    Y= np.array(df_data[YY].tolist())
    
    if fit == "YES":
        Fit_String = YY + ' ~ ' + XX
        result = sm.ols(formula=Fit_String, data=df_data).fit()
    
        constval, slope = result.params    
        rsquare= result.rsquared
        Resistance = slope

    
    fig, ax = plt.subplots()    
    ax.set_title('Two-Terminal resistance results')
    ax.set_xlabel('Current (A)')
    ax.set_ylabel('Voltage (V)')
#    ax.margins(0.3)
    if fit =="YES":
        TextString = ('Linear Fit Results of V vs. I: \n' + 'Y=' + str(round(slope,4)) + '*X + ' + str(round(constval,4))+ \
                      '\n' + 'R-Square= ' + str(round(rsquare,4)) + '\n' + 'Resistance=' + str(round(Resistance,4))+ ' Ohms')
                                             
        ax.text(0.38, 0.05, TextString, bbox={'facecolor':'red', 'alpha':0.1, 'pad':10}, size=13, transform=ax.transAxes)    
    
    ax.plot(X, slope * X + constval, color='red')    
    ax.scatter(X, Y, marker='o', s=20)
    
    fig.savefig(fig_name)
    plt.close()
    



def Four_Point_Plot(df_data, fig_name):
    df_data['V_delta']= df_data['VSH'] - df_data['VSL']
    YY = 'V_delta'
    XX = "IFH"
    
    Fit_String = YY + ' ~ ' + XX
    result = sm.ols(formula=Fit_String, data=df_data).fit()    
    
    constval, slope = result.params    
    rsquare= result.rsquared
    Resistance = slope
    
    X= np.array(df_data[XX].tolist())
    Y= np.array(df_data[YY].tolist())
    
    fig, ax = plt.subplots()    
    ax.set_title('4-point resistance results')
    ax.set_xlabel('Force Current (A)')
    ax.set_ylabel('Sense Voltage Delta (V)')
#    ax.margins(0.3)
    
    TextString = ('Linear Fit Results of V_delta vs. I_Force: \n' + 'Y=' + str(round(slope,4)) + '*X + ' + str(round(constval,4))+ \
    '\n' + 'R-Square= ' + str(round(rsquare,4)) + '\n' + 'Resistance=' + str(round(Resistance,4))+  \
    ' Ohms' + ' \n' + 'Rsheet=' + str(round(Resistance*3.14/math.log(2),4)) + ' Ohms Per square')
                                             
    ax.text(0.38, 0.05, TextString, bbox={'facecolor':'red', 'alpha':0.1, 'pad':10}, size=13, transform=ax.transAxes)    
    
    ax.plot(X, slope * X + constval, color='red')    
    ax.scatter(X, Y, marker='o', s=20)
    
    fig.savefig(fig_name)
    plt.close()
    


def Define_Measure_Four_Point_IV(device,If_start, If_stop, If_step,  V_compl=1, fname="", SMU_fh="SMU3", SMU_sh="SMU4", SMU_fl="SMU2", SMU_sl="SMU1"):
    device.measurementMode("SWEEP","MEDIUM")
#    device.get_error()    
    device.disableSmu(["VSU1", "VSU2"])
    
    device.smu(SMU_fh,["VFH","VAR1","IFH","I"])
#    device.get_error()    
    device.smu(SMU_fl,["VFL","CONS","IFL","COMM"])
#    device.get_error()    
    device.smu(SMU_sh,["VSH","CONS","ISH","I"])
#    device.get_error()    
    device.smu(SMU_sl,["VSL","CONS","ISL","I"])
#    device.get_error()    
    time.sleep(1)
    
    device.Const_Output(SMU=SMU_sh, Value="0", Compl=str(V_compl))
#    device.get_error()    
    device.Const_Output(SMU=SMU_sl, Value="0", Compl="1")
#    device.get_error()    
    device.var("VAR1",["LIN","SING",str(If_start),str(If_step),str(If_stop), str(V_compl)])
#    device.get_error()    
    time.sleep(1)
    device.OutputSequence(str_arg= (SMU_fl+"," + SMU_fh + "," + SMU_sh +"," + SMU_sl))
#    device.get_error()
    print("=>SMU's assigned")    
    time.sleep(1)
#    device.var("VAR2",["LIN","SING",str(vg_start),str(vg_step),str(vg_num),"1e-3"])
#    device.get_error()
    device.visualiseTwoYs(["IFH","LIN",str(If_start),str(If_stop)], ["VSH","LIN","0",str(V_compl)], ["VSL","LIN","0","1"])
#    device.get_error()
    print("=>Sweep Parameters set")
    
    device.single()
#    device.get_error()
    device.collect_data(['IFH','VSH', 'VSL','VFH', 'ISH', 'ISL'],fname,savedir="")
    device.get_error()
    print("=>Data Finished Collecting")
    
    return device.df_data



def diodesweep(device, SMUF="SMU1", SMUG="SMU3", V_start=-1, V_step=0.1, V_stop=1, Icompl=100E-3, fname="IV_Sweep.csv"):
    # Initialise the device
    device = hp4156c()
    device.get_error()
    device.reset()
    device.get_error()
    ## Setup the device for a Diode Measurement
    device.measurementMode("SWEEP","MEDIUM")
    device.get_error()
    device.smu(SMUF,["VF","VAR1","IF","V"])
    device.get_error()
    device.smu(SMUG,["V","CONS","I","COMM"])
    device.get_error()
    SMUWorkList = [SMUF, SMUG]
    SMUList = ["SMU1", "SMU2", "SMU3", "SMU4"]
    SMUDisableList = [x for x in SMUList if x not in SMUWorkList]
    device.disableSmu(SMUDisableList)
    device.get_error()
    device.var("VAR1",["LIN","SING", str(V_start), str(V_step), str(V_stop), str(Icompl)])
    device.get_error()
    device.visualise(["Voltage","1",str(V_start),str(V_stop)], ["Current","1",str(-Icompl),str(Icompl)])
    device.get_error()
    device.single()
    device.get_error()
    dataReturned = device.daq(["VF","IF"])
    device.get_error()
#    print(device.data)
#    device.get_error()
    #for saving
    device.save_data(fname=fname, savedir="")
    return device.df_data
    

def IDSS_Plot(df_data, plotname, separate=True, Id_limit=[1E-8, 1E-3], Ig_limit=[1E-8, 1E-3]):
    df_data.sort_values('VG', inplace=True)
    grouped = df_data.groupby('VG')

    if separate != False:
        fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=2)
        ax1.margins(0.1)
        ax2.margins(0.1)
        ax1.legend(loc=0)
        ax1.set_xlabel('VDS(V)', **{"size":'x-large'})
        ax1.set_ylabel('ID(A)', **{"size":'x-large'})
        ax1.set_yscale('log')
        ax1.grid(b=None, which='major', axis='both')
        ax1.set_ylim(Id_limit)
        
        ax2.legend(loc=0)
        ax2.set_xlabel('VDS(V)', **{"size":'x-large'})
        ax2.set_ylabel('abs (IG(A))', **{"size":'x-large'})
        ax2.yaxis.set_label_position("right")
        ax2.set_yscale('log')
        ax2.grid(b=None, which='major', axis='both')
        ax2.set_ylim(Ig_limit)
        
        fig.suptitle('ID & IG vs. VDS', fontsize=20)

        for key, group in grouped:
            ax1.plot(group.VDS, group.ID, marker='o', linestyle='None', ms=8, label=key)
            ax2.plot(group.VDS, abs(group.IG), marker='^', linestyle='None', ms=8, label=key)             
            fig.savefig(plotname + '_Separated.png') 
    
    else:
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel('VDS(V)', **{"size":'x-large'})
        ax1.set_ylabel('ID(A)', **{"size":'x-large'})
        ax1.set_yscale('log')
        ax1.legend(loc=0)
        ax1.grid(b=None, which='major', axis='both')
        ax1.set_ylim(Id_limit)

        ax2=ax1.twinx()
        ax2.legend(loc=0) 
        ax2.set_ylabel('Abs(IG(A))', **{"size":'x-large'})
        ax2.set_yscale('log')
        ax2.grid(b=None, which='major', axis='both')
        ax2.set_ylim(Ig_limit)

        ax1.margins(0.2)
        ax2.margins(0.2)
        
        fig.suptitle('Idss sweep \n Red: $I_{D}$  Blue: Abs($I_{G})$', fontsize=15)
    
        for key, group in grouped:
#            print (key)
            ax1.plot(group.VDS, group.ID, marker='o', linestyle='None', color='red',ms=8, label=key)
            ax2.plot(group.VDS, abs(group.IG), marker='^', linestyle='None', color='blue', ms=8, label=key)
    
        fig.savefig(plotname + '_Combined.png')            

    plt.close()



def IDSS_Measure(device, fname, savedir="", SMU_S1="SMU2", SMU_D="SMU4", SMU_G="SMU1", SMU_S2="SMU3",
                 vds_start=0, vds_stop=50, vds_step=0.5,vgs=-8, Id_comp=1E-3, Ig_comp=1E-3):

    define_output_smu(device,SMU_S1=SMU_S1, SMU_D=SMU_D, SMU_G=SMU_G, SMU_S2=SMU_S2)
    DF = measure_output(device, fname=fname, savedir="", vds_start=vds_start, vds_stop=vds_stop, vds_step=vds_step, 
                   vg_start=vgs, vg_step=1, vg_num=1,  Id_comp=Id_comp, Ig_comp=Ig_comp)    
#    IDSS_Plot(device.df_data, plotname=fname, separate=True, Id_limit=Id_lim, Ig_limit=Ig_lim)
    return DF
    


def IGSS_Plot(df_data, plotname):
    df_data.sort_values('VDS', inplace=True)
    grouped = df_data.groupby('VDS')

    fig, ax1 = plt.subplots(nrows=1, ncols=1)
#        ax1.margins(0.2)
    ax1.legend()
    ax1.set_xlabel('VG(V)', **{"size":'x-large'})
    ax1.set_ylabel('Abs(IG(A))', **{"size":'x-large'})
    ax1.set_yscale('log')
    ax1.grid(b=None, which='major', axis='both')

    fig.suptitle('IGSS vs. VG', fontsize=20)

    for key, group in grouped:
        ax1.plot(group.VG, abs(group.IG), marker='o', linestyle='None', ms=8, label=key)
    fig.savefig(plotname) 
    plt.close()




def measure_IGSS(device, fname, savedir, vg_start, vg_stop, vg_step):
    device.var("VAR1",["LIN","SING",str(vg_start),str(vg_step),str(vg_stop),"1e-3"])
    device.get_error()
    #note, VAR2 is always linear
#    device.var("VAR2",["LIN","SING",str(vds_start),str(vds_step),str(vds_num),"1e-3"])
#    device.get_error()
    device.visualise(["VG","LIN",str(vg_start),str(vg_stop)], ["IG","LOG","1e-10","1e-1"])
#    device.visualiseTwoYs(["VG","LIN",str(vg_start),str(vg_stop)], ["ID","LOG","1e-11","1e-6"], ["IG","LIN","-1e-8","1e-8"])
    device.get_error()
    print("=>Sweep Parameters set")
    device.single()
    device.get_error()
#    if "[INFO]"in fname:
#        if vds_step==0:
#            fname = fname.replace("[INFO]", "transferVG" + str(abs(vg_start)) + "VDS" + str(abs(vds_start)))
#        else:
#            fname = fname.replace("[INFO]", "transferVG" + str(abs(vg_start)) + "VDS" + str(abs(vds_start)) + "+" + str(vds_num) + "x" + str(abs(vds_step)))
    device.collect_data(['VG', 'VDS', 'ID', 'IG'],fname,savedir)
    device.get_error()
        
    print("=>Data Finished Collecting")
    
#    IGSS_Plot(device.df_data, plotname=fname+'.png')
#    print("=>IGSS Plotting finished!")
    return device.df_data
    

def define_IGSS_smu(device, SMU_S1="SMU2", SMU_D="SMU4", SMU_G="SMU1", SMU_S2="SMU3"):
    device.measurementMode("SWEEP","MEDIUM")
    device.get_error()
    device.smu(SMU_S1,["VS","CONS","IS","COMM"])
    device.get_error()
    device.smu(SMU_D,["VDS","CONS","ID","COMM"])
    device.get_error()
    device.smu(SMU_G,["VG","VAR1","IG","V"])
    device.get_error()
    device.smu(SMU_S2,["VGND","CONS","IGND","COMM"])
    device.get_error()
    device.OutputSequence(str_arg=(SMU_S1 + "," + SMU_S2 + ","+ SMU_D + "," + SMU_G ))
    device.get_error()
    print("=>SMU's assigned")


def Output_Plot(df_data, plotname):
    df_data.sort_values('VG', inplace=True)
    grouped = df_data.groupby('VG')
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.margins(0.1)
    ax.grid(b=None, which='major', axis='both')

    for key, group in grouped:
        ax.plot(group.VDS, group.ID, marker='o', linestyle='None', ms=8, label=key)
        ax.legend(loc=0)
        ax.set_xlabel('Vds(V)', **{"size":'x-large'})
        ax.set_ylabel('Ids(V)', **{"size":'x-large'})
        plt.title("output curve", y=1.05)
        fig.savefig(plotname + '_output_Ids.png')
        plt.close()

def measure_output(device, fname, savedir, vds_start, vds_stop, vds_step, vg_start, vg_step=1, vg_num=1, Id_comp=1E-3, Ig_comp=1E-3, plottype="Output"):
#    device.var("VAR1",["LIN","DOUB",str(vds_start),str(vds_step),str(vds_stop),"1e-3"])
    device.var("VAR1",["LIN","SING",str(vds_start),str(vds_step),str(vds_stop),str(Id_comp)])
    device.get_error()
    device.var("VAR2",["LIN","SING",str(vg_start),str(vg_step),str(vg_num),str(Ig_comp)])
    device.get_error()
    device.visualiseTwoYs(["VDS","LIN",str(vds_start),str(vds_stop)], ["ID","LIN","-1e-6","1e-6"], ["IG","LIN","-1e-8","1e-8"])
    device.get_error()
    print("=>Sweep Parameters set")
    device.single()
    device.get_error()
    if "[INFO]"in fname:
        if vds_step==0:
            fname = fname.replace("[INFO]", "outputVDS" + str(abs(vds_start)) + "VG" + str(abs(vg_start)))
        else:
            fname = fname.replace("[INFO]", "outputVDS" + str(abs(vds_start)) + "VG" + str(abs(vg_start)) + "+" + str(vg_num) + "x" + str(abs(vg_step)))
    device.collect_data(['VG', 'VDS', 'ID', 'IG'],fname,savedir)
    device.get_error()
    print("=>Data Finished Collecting")
    
#    device.Output_Plot(plotname=fname, plot_type =plottype, separate=True)
    
#    if plottype=="Output":
#        Output_Plot(device.df_data, plotname=fname+'.png')
#    if plottype=="IDSS":
#        IDSS_Plot(device.df_data, plotname=fname+'.png', separate=True, Id_limit=[1E-8, 1E-3], Ig_limit=[1E-8, 1E-3])
#        
    return device.df_data

def define_output_smu(device, SMU_S1="SMU2", SMU_D="SMU4", SMU_G="SMU1", SMU_S2="SMU3"):
    device.measurementMode("SWEEP","MEDIUM")
    device.get_error()
    device.smu(SMU_S1,["VS","CONS","IS","COMM"])
    device.get_error()
    device.smu(SMU_D,["VDS","VAR1","ID","V"])
    device.get_error()
    device.smu(SMU_G,["VG","VAR2","IG","V"])
    device.get_error()
    device.smu(SMU_S2,["VGND","CONS","IGND","COMM"])
    device.get_error()
    device.OutputSequence(str_arg= (SMU_S1 + "," + SMU_S2 + "," + SMU_G + ","+ SMU_D))
    device.get_error()
    print("=>SMU's assigned")
    

def TransferCurve_Plot(df_data, plotname, separate=True):
    df_data.sort_values('VDS', inplace=True)
    grouped = df_data.groupby('VDS')
    
    if separate != False:
        fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=2)
        ax1.margins(0.2)
        ax2.margins(0.2)
        ax1.legend(loc=0)
        ax1.set_xlabel('VG(V)', **{"size":'x-large'})
        ax1.set_ylabel('ID(A)', **{"size":'x-large'})
        ax1.set_yscale('log')
        ax1.grid(b=None, which='major', axis='both')

        ax2.legend(loc=0)
        ax2.set_xlabel('VG(V)', **{"size":'x-large'})
        ax2.set_ylabel('abs (IG(A))', **{"size":'x-large'})
        ax2.yaxis.set_label_position("right")
        ax2.set_yscale('log')
        ax2.grid(b=None, which='major', axis='both')
         

        fig.suptitle('Transfer Curve', fontsize=20)
        
        for key, group in grouped:
            ax1.plot(group.VG, group.ID, marker='o', linestyle='None', ms=8, label=key)
            ax2.plot(group.VG, abs(group.IG), marker='^', linestyle='None', ms=8, label=key)             
        fig.savefig(plotname + '_Separated.png') 
        
    else:
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel('VG(V)', **{"size":'x-large'})
        ax1.set_ylabel('ID(A)', **{"size":'x-large'})
        ax1.set_yscale('log')
        ax1.legend(loc=0)
        ax1.grid(b=None, which='major', axis='both')

        ax2=ax1.twinx()
        ax2.legend(loc=0)
        ax2.set_ylabel('Abs(IG(A))', **{"size":'x-large'})
        ax2.set_yscale('log')
        ax2.grid(b=None, which='major', axis='both')

        ax1.margins(0.2)
        ax2.margins(0.2)
        fig.suptitle('Transfer Curve \n Red: $I_{D}$  Blue: Abs($I_{G})$', fontsize=15)
        
        for key, group in grouped:
            ax1.plot(group.VG, group.ID, marker='o', linestyle='None', color='red' ,ms=8, label=key)
            ax2.plot(group.VG, abs(group.IG), marker='^', linestyle='None', color='blue', ms=8, label=key)
        
        fig.savefig(plotname + '_Combined.png')            
    
    plt.close()



def measure_transfer(device, fname, savedir, vg_start, vg_stop, vg_step, vds_start, vds_step, vds_num, Id_comp=1E-1):
    device.var("VAR1",["LIN","SING",str(vg_start),str(vg_step),str(vg_stop),"1e-3"])
    device.get_error()
    #note, VAR2 is always linear
    device.var("VAR2",["LIN","SING",str(vds_start),str(vds_step),str(vds_num),str(Id_comp)])
    device.get_error()
    device.visualiseTwoYs(["VG","LIN",str(vg_start),str(vg_stop)], ["ID","LOG","1e-11","1e-6"], ["IG","LIN","-1e-8","1e-8"])
    device.get_error()
    print("=>Sweep Parameters set")
    device.single()
    device.get_error()
    if "[INFO]"in fname:
        if vds_step==0:
            fname = fname.replace("[INFO]", "transferVG" + str(abs(vg_start)) + "VDS" + str(abs(vds_start)))
        else:
            fname = fname.replace("[INFO]", "transferVG" + str(abs(vg_start)) + "VDS" + str(abs(vds_start)) + "+" + str(vds_num) + "x" + str(abs(vds_step)))
    device.collect_data(['VG', 'VDS', 'ID', 'IG'],fname,savedir)
    device.get_error()
    print("=>Data Finished Collecting")
    
#    TransferCurve_Plot(device.df_data, plotname=fname+'.png', separate=True)
    print ("=> Transfer curve plot finished")
    return device.df_data

def define_transfer_smu(device, SMU_S1="SMU2", SMU_D="SMU4", SMU_G="SMU1", SMU_S2="SMU3"):
    device.measurementMode("SWEEP","MEDIUM")
    device.get_error()
    device.smu(SMU_S1,["VS","CONS","IS","COMM"])
    device.get_error()
    device.smu(SMU_D,["VDS","VAR2","ID","V"])
    device.get_error()
    device.smu(SMU_G,["VG","VAR1","IG","V"])
    device.get_error()
    device.smu(SMU_S2,["VGND","CONS","IGND","COMM"])    
    device.get_error()
    device.OutputSequence(str_arg=  (SMU_S1 + "," + SMU_S2 + "," + SMU_G + ","+ SMU_D))
    device.get_error()
    print("=>SMU's assigned")

def initialize_device(GPIB_address='GPIB0::17::INSTR'):
    """Initialise the device and resets. returns the resetted device"""
    device = hp4156c(device_address=GPIB_address)
    device.get_error()
    device.reset()
    device.get_error()
    print("=>Device Initialized")
    return device

