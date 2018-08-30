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
    abc = func.initialize_device(GPIB_address=address)
    
    file_address="EVB06C_"
    
#    SMU_S1, SMU_D, SMU_G, SMU_S2
    FET_SMU_SET= ["SMU3", "SMU4", "SMU2", "SMU1"]
    
#######################################
#### IGSS Measurement
#######################################    
#
#    func.define_IGSS_smu(abc, SMU_S1=FET_SMU_SET[0], SMU_D=FET_SMU_SET[1], SMU_G=FET_SMU_SET[2], SMU_S2=FET_SMU_SET[3])
#    IGSS_DF = func.measure_IGSS(abc, fname=(file_address+"_IGSS.csv"), savedir="", vg_start=-10, vg_stop=2, vg_step=0.2)
#    func.IGSS_Plot(IGSS_DF, plotname=(file_address + '_IGSS.png'))

#######################################
#### Transfer Curve Measurement
#######################################    
##
#    func.define_transfer_smu(abc, SMU_S1=FET_SMU_SET[0], SMU_D=FET_SMU_SET[1], SMU_G=FET_SMU_SET[2], SMU_S2=FET_SMU_SET[3])    
#    Transfer_DF = func.measure_transfer(abc, (file_address+"_Transfer Curve.csv"), savedir="", vg_start=-15, vg_stop=1, vg_step=0.1, 
#                     vds_start=5, vds_step=9.5, vds_num=1, Id_comp=1E-1)
#    func.TransferCurve_Plot(Transfer_DF, plotname=(file_address+"_Transfer Curve.png"), separate=True)
##    
########################################
####### I-V family or output curve Measurement
########################################    
###
#    func.define_output_smu(abc, SMU_S1=FET_SMU_SET[0], SMU_D=FET_SMU_SET[1], SMU_G=FET_SMU_SET[2], SMU_S2=FET_SMU_SET[3])
#    Output_DF = func.measure_output(abc, (file_address+"_I-V_Family.csv"), savedir="", vds_start=0, vds_stop=10, vds_step=0.2, 
#                   vg_start=-6, vg_step=1, vg_num=8, Id_comp=1E-1, Ig_comp=1E-3)
#    func.Output_Plot(Output_DF, plotname= (file_address+"_I-V_Family.png") )
###    
##########################################
######  IDSS Measurement
###########################################
#    IDSS_DF = func.IDSS_Measure(abc, fname=(file_address+"_IDSS.csv"), savedir="", SMU_S1=FET_SMU_SET[0], SMU_D=FET_SMU_SET[1], SMU_G=FET_SMU_SET[2], SMU_S2=FET_SMU_SET[3],
#                 vds_start=0, vds_stop=50, vds_step=0.5, vgs=-10, Id_comp=1E-2, Ig_comp=1E-2)
#    func.IDSS_Plot(IDSS_DF, plotname=(file_address+"_IDSS.png"), separate=True, Id_limit=[1E-8, 1E-2], Ig_limit=[1E-8, 1E-2])
    
#########################################
####  Two Terminal I-V Sweep
#########################################    
#    Two_Terminal_DF = func.diodesweep(abc, SMUF="SMU1", SMUG="SMU3", V_start=-1, V_step=0.02, V_stop=1, Icompl=100E-3, 
#               fname=(file_address + "4_IV_Sweep.csv"))
#    func.Two_Terminal_IV_Plot(df_data = Two_Terminal_DF, fig_name = (file_address + "4_IV_Sweep.png"), Y_Str="VF", X_Str="IF", fit="NO")

#########################################
####  Four Terminal Resistance Measurement for VDP
#########################################    
#    Four_DF = func.Define_Measure_Four_Point_IV(abc, If_start=5.0E-4, If_stop=1.0E-2, If_step=2.5E-4,V_compl=1, fname=(file_address + "_4-point_resistance.csv"), 
#                                SMU_fh="SMU1", SMU_fl="SMU2",  SMU_sh="SMU3", SMU_sl="SMU4")
#    func.Four_Point_Plot(Four_DF, fig_name = (file_address + "_4-point_resistance_VDP.png"))
##    


#########################################
####  Four Terminal Resistance Measurement
#########################################    
#    Four_DF = func.Define_Measure_Four_Point_IV(abc, If_start=5.0E-4, If_stop=5.0E-3, If_step=2.5E-4,V_compl=1, fname=(file_address + "_4-point_resistance.csv"), 
#                                 SMU_fh="SMU1", SMU_fl="SMU2",  SMU_sh="SMU4", SMU_sl="SMU3")
#    func.Four_Point_Plot(Four_DF, fig_name = (file_address + "_4-point_resistance.png"))
###    




if __name__ == '__main__':
    main()
