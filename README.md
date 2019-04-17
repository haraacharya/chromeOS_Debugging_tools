# chromeOS_Debugging_tools
#Idealy to run any client server tests in chromeos, either we have to install paramiko/fabric like libraries or rely on autotest which needs cros_sdk environment
#The idea of this tools project is to come up with easy to use tools with very little to none dependencies so that can be used by all in any environment.
#e.g: the first tool named chromeDebugging.py has only 1 dependency named sshpass. and this can be installed as a part of debian package without depending on pip version or any specific python library with different version dependency and hence avoid virtualenv type of implementation to help anybody and everybody use this tool to reproduce issues and test patches.
