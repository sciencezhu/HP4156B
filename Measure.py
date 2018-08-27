import visa,time, sys, io, os
from hp4156b import hp4156c
#import parameter_analyser_hp4156b as pa


def main():
    address = 'GPIB0::17::INSTR'
    
    file_address="test_"

#######################################
#### IGSS Measurement
#######################################    
    
#    abc = initialize_device()
#    define_IGSS_smu(abc)
#    measure_IGSS(abc, fname=(file_address+"_IGSS.csv"), savedir="", vg_start=-10, vg_stop=2, vg_step=0.2)
#    

#######################################
#### Transfer Curve Measurement
#######################################    
#    
#    abc = initialize_device()
#    define_transfer_smu(abc)    
#    measure_transfer(abc, (file_address+"_Transfer Curve.csv"), savedir="", vg_start=-5, vg_stop=1, vg_step=0.4, 
#                     vds_start=0.5, vds_step=9.5, vds_num=1, Id_comp=1E-1)
##    
    
#######################################
###### I-V family or output curve Measurement
#######################################    
#    SMU1:VG;   SMU4:VDS;   SMU2 & SMU3 ::Vs
    
#    abc = initialize_device()
#    define_output_smu(abc)
#    measure_output(abc, (file_address+"_I-V_Family.csv"), savedir="", vds_start=0, vds_stop=5, vds_step=0.5, 
#                   vg_start=0, vg_step=1, vg_num=3, Id_comp=1E-3, Ig_comp=1E-3)
#    


#########################################
####  IDSS Measurement
#########################################

#    abc = initialize_device()
#    IDSS_Measure(abc, fname=(file_address+"_IDSS.csv"), savedir="", vds_start=0, vds_stop=50, vds_step=0.5, 
#                 vgs=-8,Id_comp=1E-3, Ig_comp=1E-3)
    
    
    
#########################################
####  Two Terminal I-V Sweep
#########################################    
#    abc = initialize_device()
#    diodesweep(abc, SMUF="SMU1", SMUG="SMU3", V_start=-1, V_step=0.02, V_stop=1, Icompl=100E-3, 
#               fname=(file_address + "4_IV_Sweep.csv"))

#########################################
####  Four Terminal Resistance Measurement
#########################################    
    abc = initialize_device()
    Define_Measure_Four_Point_IV(abc, If_start=5.0E-4, If_stop=5.0E-3, If_step=5.0E-4, fname=(file_address + "_4-point_resistance.csv"),
                                 SMU_fh="SMU3", SMU_sh="SMU4", SMU_fl="SMU2", SMU_sl="SMU1")
#    
    
    
    


def Define_Measure_Four_Point_IV(device, If_start, If_stop, If_step,  V_compl=20, fname="", SMU_fh="SMU3", SMU_sh="SMU4", SMU_fl="SMU2", SMU_sl="SMU1"):
    device.measurementMode("SWEEP","MEDIUM")
    device.get_error()
    
    device.disableSmu(["VSU1", "VSU2"])
    
    device.smu(SMU_fh,["VFH","VAR1","IFH","I"])
    device.get_error()
    
    device.smu(SMU_fl,["VFL","CONS","IFL","COMM"])
    device.get_error()
    
    device.smu(SMU_sh,["VSH","CONS","ISH","I"])
    device.get_error()
    
    device.smu(SMU_sl,["VSL","CONS","ISL","I"])
    device.get_error()
    
    time.sleep(10)
    
    device.Const_Output(SMU=SMU_sh, Value="0", Compl=str(V_compl))
    device.get_error()
    
    device.Const_Output(SMU=SMU_sl, Value="0", Compl="1")
    device.get_error()
    
    device.var("VAR1",["LIN","SING",str(If_start),str(If_step),str(If_stop), str(V_compl)])
    device.get_error()    
    
    time.sleep(15)

    device.OutputSequence(str_arg= (SMU_fl+"," + SMU_fh + "," + SMU_sh +"," + SMU_sl))
    device.get_error()
    print("=>SMU's assigned")    
    
    
    time.sleep(10)


#    device.var("VAR2",["LIN","SING",str(vg_start),str(vg_step),str(vg_num),"1e-3"])
#    device.get_error()
    device.visualiseTwoYs(["IFH","LIN",str(If_start),str(If_stop)], ["VSH","LIN","0",str(V_compl)], ["VSL","LIN","0","0.1"])
    device.get_error()
    print("=>Sweep Parameters set")
    
    device.single()
    device.get_error()
#    if "[INFO]"in fname:
#        if vds_step==0:
#            fname = fname.replace("[INFO]", "outputVDS" + str(abs(vds_start)) + "VG" + str(abs(vg_start)))
#        else:
#            fname = fname.replace("[INFO]", "outputVDS" + str(abs(vds_start)) + "VG" + str(abs(vg_start)) + "+" + str(vg_num) + "x" + str(abs(vg_step)))
    device.collect_data(['IFH','VSH', 'VSL','VFH', 'ISH', 'ISL'],fname,savedir="")
    device.get_error()
    print("=>Data Finished Collecting")



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
    device.visualise(["Voltage","1","-1","1"], ["Current","1","-0.1","0.1"])
    device.get_error()
    device.single()
    device.get_error()
    dataReturned = device.daq(["VF","IF"])
    device.get_error()
#    print(device.data)
#    device.get_error()
    #for saving
    device.save_data(fname=fname, savedir="")


def IDSS_Measure(device, fname, savedir="", vds_start=0, vds_stop=50, vds_step=0.5,vgs=-8, Id_comp=1E-3, Ig_comp=1E-3 ):

    define_output_smu(device)
    measure_output(device, fname=fname, savedir="", vds_start=vds_start, vds_stop=vds_stop, vds_step=vds_step, 
                   vg_start=vgs, vg_step=1, vg_num=1,  Id_comp=Id_comp, Ig_comp=Ig_comp)
    




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
    
    device.IGSS_Plot(plotname=fname)
    print("=>IGSS Plotting finished!")




def define_IGSS_smu(device):
    device.measurementMode("SWEEP","MEDIUM")
    device.get_error()
    device.smu("SMU2",["VS","CONS","IS","COMM"])
    device.get_error()
    device.smu("SMU4",["VDS","CONS","ID","COMM"])
    device.get_error()
    device.smu("SMU1",["VG","VAR1","IG","V"])
    device.get_error()
    device.smu("SMU3",["VGND","CONS","IGND","COMM"])
    device.get_error()
    device.OutputSequence(str_arg="SMU2,SMU3,SMU4, SMU1")
    device.get_error()
    print("=>SMU's assigned")



def measure_output(device, fname, savedir, vds_start, vds_stop, vds_step, vg_start, vg_step=1, vg_num=1, Id_comp=1E-3, Ig_comp=1E-3):
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



def define_output_smu(device):
    device.measurementMode("SWEEP","MEDIUM")
    device.get_error()
    device.smu("SMU2",["VS","CONS","IS","COMM"])
    device.get_error()
    device.smu("SMU4",["VDS","VAR1","ID","V"])
    device.get_error()
    device.smu("SMU1",["VG","VAR2","IG","V"])
    device.get_error()
    device.smu("SMU3",["VGND","CONS","IGND","COMM"])
    device.get_error()
    device.OutputSequence(str_arg="SMU2,SMU3,SMU1, SMU4")
    device.get_error()
    print("=>SMU's assigned")
    

def measure_transfer(device, fname, savedir, vg_start, vg_stop, vg_step, vds_start, vds_step, vds_num, Id_comp=1E-1):
    device.var("VAR1",["LIN","DOUB",str(vg_start),str(vg_step),str(vg_stop),"1e-3"])
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
    
    device.TransferCuve_Plot(plotname=fname, separate = True)
    print ("=> Transfer curve plot finished")

def define_transfer_smu(device):
    device.measurementMode("SWEEP","MEDIUM")
    device.get_error()
    device.smu("SMU2",["VS","CONS","IS","COMM"])
    device.get_error()
    device.smu("SMU4",["VDS","VAR2","ID","V"])
    device.get_error()
    device.smu("SMU1",["VG","VAR1","IG","V"])
    device.get_error()
    device.smu("SMU3",["VGND","CONS","IGND","COMM"])    
    device.get_error()
    device.OutputSequence(str_arg="SMU2,SMU3,SMU1, SMU4")
    device.get_error()
    print("=>SMU's assigned")



def initialize_device():
    """Initialise the device and resets. returns the resetted device"""
    device = hp4156c()
    device.get_error()
    device.reset()
    device.get_error()
    print("=>Device Initialized")
    return device





if __name__ == '__main__':
	main()
