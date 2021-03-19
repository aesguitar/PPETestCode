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
# Checks if the config file directory exists
def checkConfigLocExists():
    return path.exists(configloc)
# Check if the config file exists
def checkConfigFileExists():
    return path.exists(configloc+configfile)

# writes a config file with default values
# will create any necessary directories
def writeNewConfig():
    if not checkConfigLocExists():
        os.makedirs(configloc)
        
    f = open(configloc+configfile, 'w')
    def_config.write(f)
 
# reads an existing config file
# returns the default config if the file does not exist
def readConfigFile():
    try:
        f = open(configloc+configfile,'x')
        r_config.read_file(f)
        return r_config
    except OSError:
        print("Config file does not exist at %s" % configloc+configfile)
        setDefaultConfigValues()
        return def_config
        

def main():
    setDefaultConfigValues()
    
    
    c = readConfigFile()
    sections = c.sections()
    for section in sections:
        print("Section: [%s]" % str(section))
        for key in c[section]:
            print("\t%s : %s" % (key,c[section][key]))


if __name__ == '__main__':
    main()
