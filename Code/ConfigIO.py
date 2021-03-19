import os
from os import path
import configparser

#Handles config file
#Format of config file is generic .ini file
#configparser handles parsing

#routines should support cli modification and
#programmatic modification

def_config = configparser.ConfigParser() #default config
r_config = configparser.ConfigParser()

configloc = './'
configfile = 'config.ini'

def setDefaultConfigValues():
    def_config['TempMonitor'] = {'TLogDirectory':'../TestLogs/', #default location of temperature logs
                             'TLowFailLimit':'18.0', #default temperature low fail limit
                             'TLowWarnLimit':'19.0', #default temperature low warn limit
                             'THighFailLimit':'22.0', #default temperature high fail
                             'DefaultRuntime':'30.0', #default run time in seconds
                             'DefaultUpdateRate':'1', #default update rate in hertz
                             'RunningAverageOn':'1', #enable running average in data collection; 1 = on; 0 = off
                             'RunningAverageInterval':'5'} #default samples per running average collection
                             
def checkConfigLocExists():
    return path.exists(configloc)
     
def checkConfigFileExists():
    return path.exists(configloc+configfile)

def writeNewConfig():
    f = open(configloc+configfile, 'w')
    def_config.write(f)
    
def readConfigFile():
    r_config.read(configloc+configfile)

def main():
    setDefaultConfigValues()
    
    if not checkConfigLocExists():
        print("Writing config directory.")
        try:
            os.makedirs(configloc)
        except OSError:
            print("Creation of directory %s failed." % configloc)
        
        print("Writing config file.")
        writeNewConfig()
    else:
        print("Config directory exists.")
        if not checkConfigFileExists():
            print("Writing config file.")
            writeNewConfig()
        else:
            print("Config file exists.")
            print("Reading...")
            readConfigFile()
            sections = r_config.sections()
            for section in sections:
                print("Section: %s" % str(section))
                for key in r_config[section]:
                    print("%s : %s" % (key,r_config[section][key]))


if __name__ == '__main__':
    main()
