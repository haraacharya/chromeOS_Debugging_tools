# chromeOS_Debugging_tools

#Idealy to run any client server tests in chromeos, either we have to install paramiko/fabric like libraries or rely on autotest which needs cros_sdk environment

#The idea of this tools project is to come up with easy to use tools with very little to none dependencies so that can be used by all in any environment.

#e.g: the first tool named chromeDebugging.py has only 1 dependency named sshpass. and this can be installed as a part of debian package without depending on pip version or any specific python library with different version dependency and hence avoid virtualenv type of implementation to help anybody and everybody use this tool to reproduce issues and test patches.

python chromeDebugging.py --help
usage: chromeDebugging.py [-h] [--test TEST_TO_RUN] [--IP IP_ADDRESS]
                          [--COUNT ITERATION_COUNT] [--command CMD_TO_RUN]
                          [--search_for SEARCH_PATTERNS [SEARCH_PATTERNS ...]]

optional arguments:
  -h, --help            show this help message and exit
  --test TEST_TO_RUN    test to run is either "reboot" or "suspend"
  --IP IP_ADDRESS       provide remote system ip
  --COUNT ITERATION_COUNT
                        Provide iteration count!
  --command CMD_TO_RUN  Please mention the command to check in double quotes!
  --search_for SEARCH_PATTERNS [SEARCH_PATTERNS ...]
                        provide one or many search strings with space. If
                        found, test will FAIL/STOP.

#python chromeDebugging.py --test reboot --IP <DUT_IP> --command "dmesg --level=err" --search_for "error" "usb"
