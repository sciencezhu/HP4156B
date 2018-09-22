import visa,time, sys, io, os, math
from hp4156b_class import hp4156c
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as sm
import numpy as np
import HP4156B_Functions as func

#import parameter_analyser_hp4156b as pa


def main():
    address = 'GPIB0::17::INSTR'
#    abc = func.initialize_device(GPIB_address=address)
    
    file_address="GV10073.1B_W17_(1,3)_P005A"
    
#    SMU_S1, SMU_D, SMU_G, SMU_S2
    FET_SMU_SET= ["SMU3", "SMU4", "SMU1", "SMU2"]
    Gate_Width=0.1  ## Unit in mm.
    
#    Test = ["Transfer","IGSS",  "Family", "IDSS"]
    FET_Test = []   # Put the test here which you want to measure. Leave it empty if you don't 

    


    if not FET_Test:
        print (0)
    ###########################################
    ###  Two Terminal I-V Sweep
    ###########################################
        
#        file_address="GV10073.1B_W17_(1,3)_P052A"
#        Two_Terminal_DF = func.diodesweep(abc, SMUF="SMU1", SMUG="SMU4", V_start=-5, V_step=0.05, V_stop=5, Icompl=100E-3, fname=file_address)
#        func.Two_Terminal_IV_Plot(df_data = Two_Terminal_DF, fig_name = file_address, fit=True, I_as_X=True, Normalize=False, Wg=0.075)
#    
#    #########################################
#    ###  Four Terminal Resistance Measurement for VDP
#    ########################################    
#        
#        file_address="Test"
#        Four_DF = func.Define_Measure_Four_Point_IV(abc, If_start=5.0E-4, If_stop=1.0E-2, If_step=2.5E-4,V_compl=100, fname=file_address, 
#                                     SMU_fh="SMU1", SMU_fl="SMU2",  SMU_sh="SMU3", SMU_sl="SMU4")
#        func.Four_Point_Plot(Four_DF, fig_name = file_address)
#    ##
#    
#    ########################################
#    ###  Four Terminal Resistance Measurement
#    ########################################    
#        file_address="GV10030.7_P053A_5,4_Post-M2"
#        Four_DF = func.Define_Measure_Four_Point_IV(abc, If_start=5.0E-4, If_stop=5.0E-3, If_step=2.5E-4,V_compl=100, fname=file_address, 
#                                     SMU_fh="SMU3", SMU_fl="SMU2",  SMU_sh="SMU4", SMU_sl="SMU1")
#        func.Four_Point_Plot(Four_DF, fig_name = file_address)
#    ###    



#######################################
#### IGSS Measurement
#######################################    
    if ("IGSS" in FET_Test) or ("Igss" in FET_Test):
        func.define_IGSS_smu(abc, SMU_S1=FET_SMU_SET[0], SMU_D=FET_SMU_SET[1], SMU_G=FET_SMU_SET[2], SMU_S2=FET_SMU_SET[3])
        IGSS_DF = func.measure_IGSS(abc, fname=file_address, savedir="", vg_start=-10, vg_stop=1, vg_step=0.1)
        func.IGSS_Plot(IGSS_DF, plotname=file_address, Wg=Gate_Width )

#######################################
##### Transfer Curve Measurement
#########################################    
    if ("Transfer" in FET_Test) or ("transfer" in FET_Test):
        func.define_transfer_smu(abc, SMU_S1=FET_SMU_SET[0], SMU_D=FET_SMU_SET[1], SMU_G=FET_SMU_SET[2], SMU_S2=FET_SMU_SET[3])    
        Transfer_DF = func.measure_transfer(abc, file_address, savedir="", vg_start=-10, vg_stop=1, vg_step=0.1, 
                     vds_start=10, vds_step=9.5, vds_num=1, Id_comp=1E-1)
        func.TransferCurve_Plot(Transfer_DF, plotname=file_address, separate=True, ylog=True, Wg=Gate_Width)
        func.TransferCurve_Plot(Transfer_DF, plotname=file_address, separate=True, ylog=False, Wg=Gate_Width)
##    
##########################################
######### I-V family or output curve Measurement
##########################################    
    if ("Family" in FET_Test) or ("family" in FET_Test):
        func.define_output_smu(abc, SMU_S1=FET_SMU_SET[0], SMU_D=FET_SMU_SET[1], SMU_G=FET_SMU_SET[2], SMU_S2=FET_SMU_SET[3])
        Output_DF = func.measure_output(abc, file_address, savedir="", vds_start=0, vds_stop=10, vds_step=0.2, 
                   vg_start=-3, vg_step=1, vg_num=5, Id_comp=1E-1, Ig_comp=5E-3)
        func.Output_Plot(Output_DF, plotname= file_address, Wg=Gate_Width)
###    
###############################################
###########  IDSS Measurement
################################################
    if ("IDSS" in FET_Test) or ("Idss" in FET_Test):
        IDSS_DF = func.IDSS_Measure(abc, fname= file_address, savedir="", SMU_S1=FET_SMU_SET[0], SMU_D=FET_SMU_SET[1], SMU_G=FET_SMU_SET[2], SMU_S2=FET_SMU_SET[3],
                 vds_start=0, vds_stop=50, vds_step=0.5, vgs=-8, Id_comp=1E-2, Ig_comp=1E-2)
        func.IDSS_Plot(IDSS_DF, plotname=file_address, separate=True, Id_limit=[1E-4, 1E0], Ig_limit=[1E-4, 1E0], Wg=Gate_Width)
    
if __name__ == '__main__':
    main()
