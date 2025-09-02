# coding: utf-8
## @package <Package name>
# Script: <Description>  
#
# Script template by ANDi
#
#
## @author <Author>
## @version 0.1
## @date <Date>


# --- Imports
#from time import sleep
#This import is necessary to have access from the modules to the global elements like timers, messages, etc.
from project import * 


# --- Constants

## Maximum time (seconds) for listening packets
#TIMEOUT = 3

# --- Global variables


# --- Functions


def init_script():
    ##
    # Add your routine code here (create messages, set the parameters, etc...)
    ##
    return


def tc_start():
    ##
    # Add your routine code here (capture messages, etc...)
    ##
    return


def tc_stop():
    ##
    # Add your routine code here (stop captures, stop running threads, generate report, etc...)
    # Do not forget to set the test case result (in case) by calling tc_return_success() or tc_return_failure()
    ##
    return


#----------------------------#
#            MAIN            #
#----------------------------#

# Init the elements used in the script
init_script()

# Call the start routine
tc_start()

# Wait some time to capture messages
#sleep(TIMEOUT)

##
# Add your script main implementation here
##

# Call the stop routine
tc_stop()

#----------------------------#
#      END OF THE SCRIPT     #
#----------------------------#