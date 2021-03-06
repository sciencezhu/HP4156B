#!/var/run/python
# Agilent Parameter Analyser Sweep function script.


# Import the HP4156C class

# The HP4156C class includes the metaclass visa

# This allows the HP4156C to wrap the visa class
# When wrapped the HP4156C class takes care of all the visa syntax
# and translates parameter analyser settings into visa commands
import sys,visa,os, time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class hp4156c(object):
    def __init__(self,device_id=''):
        self.deviceName = "HEWLETT-PACKARD,4156B,0,02.10:03.06:01.00"
        print ("test")
        self.device_id = device_id
        self._initialise()

    def _initialise(self, address='GPIB0::17::INSTR'):
        """Iterates through all devices on the GPIB bus until it finds the
        parameter analyser with ID _self.deviceName. If no parameter analyser found
        the initiation is aborted and a sys.exit is called"""
        print("HP4156C Initialisation")
        rm = visa.ResourceManager("C:/Windows/SysWOW64/visa32.dll")
        self.pa = rm.open_resource(address)
        self.pa.read_termination = '\n'
        self.pa.write_termination = '\n'
        self.pa.timeout = 800000
        self.pa.write("*rst")
        print(self.pa.query('*IDN?'))
        
#		_devices = rm.list_resources()
#		print(_devices)
#		for _x in _devices:
#			print("Here is devices found in resources: " + _x)
#			try:
#				self.pa = rm.open_resource(_x)
#				self.device_id = self.pa.query("*IDN?\n").encode().rstrip()
#				print ("*IDN? found such device id: " + self.device_id)
#				if(self.device_id == self.deviceName):
#					print("Found device from *IDN? command %s"%self.device_id)
#					break
#			except:
#				print("Could not connect to device " + _x)
#		if(self.device_id != self.deviceName):
#			print("Could not find the parameter analyser.")
#			print("Exiting.")
#			sys.exit()
#		else:
#			self.pa.write("*rst")
#		print("Connected to device " + _x)
    def reset(self):
        """ Calls a reset command on the parameter analyser"""
        self.pa.write("*rst")

    def measurementMode(self, mode, intTime):
        """ Sets the parameter analyser operation mode and integration time"""
        if(mode == "SWEEP" or mode == "SAMPLE" or mode == "QSCV") and (intTime == "SHORT" or intTime == "MEDIUM" or intTime == "LONG"):
            self.pa.write(":PAGE:CHAN:MODE " + mode)
            self.pa.write(":PAGE:MEAS:MSET:ITIM " + intTime)
        else:
            print("Invalid measurement mode or integration time. Exiting.")
            sys.exit()

    def _stringSmuMod(self,arg):
        """ Formats the smu argument2 into SCPI ASCII text """
        arg[0] = "'" + arg[0] + "'"
        arg[2] = "'" + arg[2] + "'"
        return arg

    def smu(self, arg1, arg2):
        """Sets up the SMU specified in arg1 with the parameters specified in
        arg2 """
        self.arg2 = self._stringSmuMod(arg2)
        self.smuSetup = [":PAGE:CHAN:"+arg1+":VNAME %s",":PAGE:CHAN:"+arg1+":FUNC %s",":PAGE:CHAN:"+arg1+":INAME %s",":PAGE:CHAN:"+arg1+":MODE %s",":PAGE:MEAS:CONS:"+arg1+" %s",":PAGE:MEAS:CONS:"+arg1+":COMP %s"]
        self.pa.write(self.smuSetup[0] %self.arg2[0])
        self.pa.write(self.smuSetup[1] %self.arg2[1])
        self.pa.write(self.smuSetup[2] %self.arg2[2])
        self.pa.write(":PAGE:DISP:LIST %s" % self.arg2[2])
        self.pa.write(self.smuSetup[3] %self.arg2[3])
#		if arg2[1] != "VAR1" and arg2[1] != "VAR2" and arg2[3] != "COMM" and arg2[1] != "VAR1\'":
#			self.pa.write(self.smuSetup[4] % arg2[4])
#			self.pa.write(self.smuSetup[5] % arg2[5])


    def OutputSequence(self, str_arg="SMU1,SMU2,SMU3"):
        """format conversion for variable arguments to parameter analyser
        ascii"""
        self.pa.write(":PAGE:MEASure:OSEQuence:MODE SEQuential")
        self.pa.write(":PAGE:MEAS:OSEQ:OSEQ " + str_arg )
        time.sleep(3)

    def disableSmu(self,arg):
        """Disables all SMUs specified in arg"""
        for i in arg:
            self.pa.write(":PAGE:CHAN:" + i + ":DIS")

    def _varStringMod(self, arg):
        """format conversion for variable arguments to parameter analyser
        ascii"""
        arg[0] = "'" + arg[0] + "'"
        return arg

    def Const_Output(self, SMU="SMU1_name", Value="0", Compl="2"):
        String = ":PAGE:MEAS:CONS:" + SMU
        self.pa.write(String + " " + Value)
        self.pa.write(String + ":COMP " + Compl)
        time.sleep(1)


    ## arg1 is the smu number
    ## arg2 is the parameters for a sweep. [LIN:LOG SING:DOUB STAR STEP STOP COMP]
    def var(self, arg1, arg2):
        """Variable parameters, allowing step changes to be implemented"""
        string = ":PAGE:MEAS:" + arg1 + ":"
        if arg1 == "VAR1":
            self.pa.write(string + "SPAC %s" % arg2[0])
            self.pa.write(string + "MODE %s" % arg2[1])
            self.pa.write(string + "STAR %s" % arg2[2])
            self.pa.write(string + "STEP %s" % arg2[3])
            self.pa.write(string + "STOP %s" % arg2[4])
            self.pa.write(string + "COMP %s" % arg2[5])
        elif arg1 == "VAR2":
            self.pa.write(string + "MODE %s" % arg2[1])
            self.pa.write(string + "STAR %s" % arg2[2])
            self.pa.write(string + "POIN %s" % arg2[4])
            self.pa.write(string + "STEP %s" % arg2[3])
            self.pa.write(string + "COMP %s" % arg2[5])

    def _daqStringMod(self,arg):
        """Format conversion for obtained data"""
        self.stuff = []
        for i in arg:
            self.stuff.append("\'"+i+"\'")
        return self.stuff

    def daq(self, values):
        """ Obtain stored data from the parameter analyser. Includes code for
        the case when the stored data length exceeds the maximum data length of
        a retrieve command"""
        #self.data = self._daqStringMod(arg)
        self.values=values #necessary for saving data
        self.data =[[]]*len(values)
        self.pa.timeout=120000
        for x in range(0,len(values)):
            try:
                print("Obtaining %s data values" % values[x])
                self.pa.write(":DATA? %s"%values[x])
            except:
                print("Command Timeout!")
#			read = self.pa.read() # returns unicode string of values
            time.sleep(3)
            if True:
                read = self.pa.read_raw()
#				print (read)
                self.data[x] = [float(a) for a in read.decode("utf-8").rstrip().split(",")]
            if False:
                read = self.pa.read_bytes(500)
#				print (read)
                self.data[x] = [float(a) for a in read.decode("utf-8").rstrip().split(",")]
			#decodes string and adds to data array
#			print (read)
#			print (type(read))

#			self.data[x] = [float(a) for a in read.split(",")]
            print("Obtained %d data values for %s" % (len(self.data[x]),values[x]))
        self.pa.timeout=300000
        self.data=np.transpose(np.array(self.data))
        print ("data in an {} array".format(self.data.shape))
        self.df_data = pd.DataFrame(self.data, columns = values)
        self.df_data.to_csv("test_pandas.csv", index=False)


    def IGSS_Plot(self, plotname):
        self.df_data.sort_values('VDS', inplace=True)
        grouped = self.df_data.groupby('VDS')

        fig, ax1 = plt.subplots(nrows=1, ncols=1)
#        ax1.margins(0.2)
        ax1.legend()
        ax1.set_xlabel('VG(V)', **{"size":'x-large'})
        ax1.set_ylabel('Abs(IG(A))', **{"size":'x-large'})
        ax1.set_yscale('log')

        fig.suptitle('IGSS vs. VG', fontsize=20)

        for key, group in grouped:
            ax1.plot(group.VG, abs(group.IG), marker='o', linestyle='-', ms=8, label=key)
        fig.savefig(plotname + '.png') 
        plt.close()


    def TransferCuve_Plot(self, plotname, separate = True):
        self.df_data.sort_values('VDS', inplace=True)
        grouped = self.df_data.groupby('VDS')
        
        if separate != False:
            fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=2)
            ax1.margins(0.2)
            ax2.margins(0.2)
            ax1.legend()
            ax1.set_xlabel('VG(V)', **{"size":'x-large'})
            ax1.set_ylabel('ID(A)', **{"size":'x-large'})

            ax2.legend()
            ax2.set_xlabel('VG(V)', **{"size":'x-large'})
            ax2.set_ylabel('abs (IG(A))', **{"size":'x-large'})
            ax2.yaxis.set_label_position("right")

            fig.suptitle('Transfer Curve', fontsize=20)
            
            for key, group in grouped:
                ax1.plot(group.VG, group.ID, marker='o', linestyle='-', ms=8, label=key)
                ax2.plot(group.VG, abs(group.IG), marker='^', linestyle='--', ms=8, label=key)             
            fig.savefig(plotname + '_Separated.png') 
            
        else:
            fig = plt.figure()
            ax1 = fig.add_subplot(111)
            ax1.set_xlabel('VG(V)', **{"size":'x-large'})
            ax1.set_ylabel('ID(A)', **{"size":'x-large'})
            ax1.legend()            

            ax2=ax1.twinx()
            ax2.set_ylabel('Abs(IG)', **{"size":'x-large'})
            ax2.set_yscale('log')

            ax1.margins(0.2)
            ax2.margins(0.2)
            fig.suptitle('Transfer Curve \n Solid: $I_{D}$  Dash: Abs($I_{G})$', fontsize=15)
            
            for key, group in grouped:
                ax1.plot(group.VG, group.ID, marker='o', linestyle='-', ms=8, label=key)
                ax2.plot(group.VG, abs(group.IG), marker='^', linestyle='--', ms=8, label=key)
            
            fig.savefig(plotname + '_TrasferCurve_Combined.png')            
        
        plt.close()


    def save_data(self,fname,savedir):
        header=""
        for val in self.values:
            header=header+val+","
        np.savetxt(os.path.join(savedir,fname), self.data, delimiter=',', header=header[:-1], comments="")


    def collect_data(self,values,fname,savedir):
        """combines data acquisition and saving in a single function"""
        self.daq(values)
        self.save_data(fname, savedir)

    def single(self):
        """Initiate a single measurement using entered parameters"""
        self.pa.write(":PAGE:SCON:SING")
        self.pa.write("*WAI")
        self.pa.timeout=1E6 #if you need more than 11.6 days you're fucked
#		time.sleep(5)
        self.pa.ask("*OPC?")
        self.pa.timeout=30000


    def continuous(self):
        """Initiate continuous measurements using entered parameters"""
        self.pa.write(":PAGE:SCON:CONT")
        self.pa.write("*WAI")

    def visualiseTwoYs(self, x, y1, y2):
        """Displays results on the parameter analysers display. This is
        superfluous to requirements as the gui handles this"""
        self.x = self._varStringMod(x)
        self.y1 = self._varStringMod(y1)
        self.y2 = self._varStringMod(y2)
        self.pa.write(":PAGE:DISP:GRAP:GRID ON")
        self.pa.write(":PAGE:DISP:GRAP:X:NAME %s" % self.x[0])
        self.pa.write(":PAGE:DISP:GRAP:Y1:NAME %s" % self.y1[0])
        self.pa.write(":PAGE:DISP:GRAP:Y2:NAME %s" % self.y2[0])
        self.pa.write(":PAGE:DISP:GRAP:X:SCAL %s" % self.x[1])
        self.pa.write(":PAGE:DISP:GRAP:Y1:SCAL %s" % self.y1[1])
        self.pa.write(":PAGE:DISP:GRAP:Y2:SCAL %s" % self.y2[1])
        self.pa.write(":PAGE:DISP:GRAP:X:MIN %s" % self.x[2])
        self.pa.write(":PAGE:DISP:GRAP:Y1:MIN %s" % self.y1[2])
        self.pa.write(":PAGE:DISP:GRAP:Y2:MIN %s" % self.y2[2])
        self.pa.write(":PAGE:DISP:GRAP:X:MAX %s" % self.x[3])
        self.pa.write(":PAGE:DISP:GRAP:Y1:MAX %s" % self.y1[3])
        self.pa.write(":PAGE:DISP:GRAP:Y2:MAX %s" % self.y2[3])

    def visualise(self, x ,y1):
        """Displays results on the parameter analysers display. This is
        superfluous to requirements as gui will handle this"""
        self.x = self._varStringMod(x)
        self.y1 = self._varStringMod(y1)
        self.pa.write(":PAGE:DISP:GRAP:GRID ON")
        self.pa.write(":PAGE:DISP:GRAP:X:NAME %s" % self.x[0])
        self.pa.write(":PAGE:DISP:GRAP:Y1:NAME %s" % self.y1[0])
        self.pa.write(":PAGE:DISP:GRAP:X:SCAL %s" % self.x[1])
        self.pa.write(":PAGE:DISP:GRAP:Y1:SCAL %s" % self.y1[1])
        self.pa.write(":PAGE:DISP:GRAP:X:MIN %s" % self.x[2])
        self.pa.write(":PAGE:DISP:GRAP:Y1:MIN %s" % self.y1[2])
        self.pa.write(":PAGE:DISP:GRAP:X:MAX %s" % self.x[3])
        self.pa.write(":PAGE:DISP:GRAP:Y1:MAX %s" % self.y1[3])

    def abort(self):
        """Does not do anything currently. This function could be useful if we
        implement continuous reading mode"""
        self.pa.write(":PAGE:SCON:STOP")
        pass

    def stress(self, term, func, mode, name, value=0.0, duration=0):
        """
        Sets up the stress conditions for the 4156.
        Default duration is free-run, no time limit to applied stress.
        """
        self.name=self._varStringMod(name)
        self.pa.write(":PAGE:STR:SET:DUR %s" % duration)
        self.pa.write(":PAGE:STR:%s:NAME %s" % (term,self.name))
        self.pa.write(":PAGE:STR:%s:FUNC %s" % (term,func))
        self.pa.write(":PAGE:STR:%s:MODE %s" % (term,mode))
        self.pa.write(":PAGE:STR:SET:CONS:%s %s" % (term,value))
        pass

    def merger(self, *lists):
        """Combines any number of lists of equal length."""
        self.merged=[]
        for i in range(len(lists[0][0])):
            self.temp=[]
            for j in range(len(lists[0])):
                self.temp.append(lists[0][j][i])
            self.merged.append(self.temp)
        return self.merged

    def get_error(self, v=True):
        """Returns the first value in the error register"""
        print ("Error occured")
        err=self.pa.ask(":SYST:ERR?")
        if v:
            print("Error is: " + err)
        return err
