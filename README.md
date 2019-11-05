# chromeOS_Debugging_tools  
#Idealy to run any client server tests in chromeos, either we have to install paramiko/fabric like libraries or rely on autotest which needs cros_sdk environment    
#The idea of this tools project is to come up with easy to use tools with very little to none dependencies so that can be used by all in any environment.    
#e.g: the first tool named chromeDebugging.py has only 1 dependency named sshpass. and this can be installed as a part of debian package without depending on pip version or any specific python library with different version dependency and hence avoid virtualenv type of implementation to help anybody and everybody use this tool to reproduce issues and test patches.    

python chromeDebugging.py --help  
usage: chromeDebugging.py [-h] [--testcase TESTCASE_TO_RUN]
                          [--test TEST_TO_RUN] [--ip IP_ADDRESS]
                          [--after_test_delay WAIT_DEVICE_INITIALIZATION]
                          [--count ITERATION_COUNT] [--command CMD_TO_RUN]
                          [--search_for SEARCH_PATTERNS [SEARCH_PATTERNS ...]]

optional arguments:
  -h, --help            show this help message and exit
  --testcase TESTCASE_TO_RUN
                        testcase to run is before reboot or suspend test
  --test TEST_TO_RUN    test to run is either "reboot" or "suspend" or
                        "rtc_coldboot" or "ec_coldboot" or servo_coldboot
  --ip IP_ADDRESS       provide remote system ip
  --after_test_delay WAIT_DEVICE_INITIALIZATION
                        Provide Device initialization delay in seconds after
                        test!
  --count ITERATION_COUNT
                        Provide iteration count!
  --command CMD_TO_RUN  Please mention the command to check in double quotes!
  --search_for SEARCH_PATTERNS [SEARCH_PATTERNS ...]
                        provide one or many search strings with space. If
                        found, test will FAIL/STOP.  

#python chromeDebugging.py --test reboot --ip <DUT_IP> --command "dmesg --level=err" --search_for "error" "usb"  



