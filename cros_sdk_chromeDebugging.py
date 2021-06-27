import argparse
import os
import platform
import re
import sys
import time
import subprocess
from datetime import datetime
import logging
import logging.handlers


chrome_debug_log_folder = os.getcwd() + "/debug_log"
if not os.path.exists(chrome_debug_log_folder):
    os.makedirs(chrome_debug_log_folder)

log_file_name = chrome_debug_log_folder + "/" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') +"_chrome_debug.log"
#lname = datetime.now().strftime('%Y-%m-%d_%H:%M') +"_chrome_debug.log"

logging.basicConfig(filename= log_file_name, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
dlogger = logging.getLogger(__name__)
dlogger.addHandler(handler)


#CONFIG PARAMETERS FOR USER TO CHANGE
s0ix_residency_file = '/sys/kernel/debug/telemetry/s0ix_residency_usec'
s0ix_lidclose_wait = 10
s0ix_lidopen_wait = 10
#cros_sdk_path = '/home/cssdesk/google_source'
#abs_cros_sdk_path = '/home/cssdesk/depot_tools/cros_sdk --no-ns-pid'
wait_device_initialization = 15
shutdown_wait_time = 15
reboot_wait_time = 150
reboot_wait_time_minute = str(round(reboot_wait_time/float(60), 2))
#END CONFIG PARAMETERS FOR USER TO CHANGE

def check_if_remote_system_is_live(ip):
    hostname = ip
    # print ("hostname is", hostname)
    try:
        response = os.system("ping -c 1 " + hostname + '>/dev/null 2>&1')
    except:
        return False

    if response == 0:
        return True
    else:
        return False

def run_command(command, dut_ip, username="root", password="test0000"):
    
    if check_if_remote_system_is_live(dut_ip):
        sshpassCmd = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + username + "@" + dut_ip + " '" + command +  "'"
        print (sshpassCmd)
        p = subprocess.Popen(sshpassCmd, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        
        ## Wait for command to terminate. Get return returncode ##
        p_status = p.wait()
        # print ("Command output : ", output)
        # print ("Command exit status/return code : ", p_status)
        if p_status != 0:
            return False
        else:
            return output.decode('ascii')

def run_reboot(dut_ip, username="root", password="test0000", reboot_wait_time=60):
    
    if check_if_remote_system_is_live(dut_ip):
        sshpassCmd = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + username + "@" + dut_ip + " 'reboot'"
        print (sshpassCmd)
        p = subprocess.Popen(sshpassCmd, stdout=subprocess.PIPE, shell=True)
        time.sleep(3)
        if check_if_remote_system_is_live(dut_ip):
            print ("System reboot didn't happen.")
            return False
        else:
            for i in range(reboot_wait_time):
                time.sleep(1)
                if check_if_remote_system_is_live(dut_ip):
                    print ("Waiting for device initialization after test in seconds: ", wait_device_initialization)
                    time.sleep(wait_device_initialization)
                    return True
            print ("system didn't reboot back on after %d seconds wait delay" % (reboot_wait_time))
            return False
    else:
        print ("DUT is not live")
        return False

def rtc_cold_reboot(dut_ip, username="root", password="test0000", shutdown_wait_time=10, reboot_wait_time=80):
    
    if check_if_remote_system_is_live(dut_ip):
        sshpassCmd1 = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + username + "@" + dut_ip + " 'echo +15 > /sys/class/rtc/rtc0/wakealarm'"
        print (sshpassCmd1)
        p = subprocess.Popen(sshpassCmd1, stdout=subprocess.PIPE, shell=True)

        sshpassCmd2 = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + username + "@" + dut_ip + " 'shutdown -h now'"
        print (sshpassCmd2)
        p = subprocess.Popen(sshpassCmd2, stdout=subprocess.PIPE, shell=True)
        time.sleep(shutdown_wait_time)
        if not check_if_remote_system_is_live(dut_ip):
            print ("System shutdown successfull.")
            for i in range(reboot_wait_time):
                time.sleep(1)
                if check_if_remote_system_is_live(dut_ip):
                    print ("Waiting for device initialization after test in seconds: ", wait_device_initialization)
                    time.sleep(wait_device_initialization)
                    return True
        else:
            print ("system didn't shutdown after %d seconds wait delay" % (shutdown_wait_time))
            return False
    else:
        print ("DUT is not live")
        return False

def ec_pwrbtn():
    os.chdir(cros_sdk_path)	
    dlogger.info (os.getcwd())
    ec_console_powerbtn_command = 'dut-control ec_uart_cmd:powerbtn'
    os.system(ec_console_powerbtn_command)

def ec_cold_reboot(dut_ip, username="root", password="test0000", shutdown_wait_time=10, reboot_wait_time=120):
    
    if check_if_remote_system_is_live(dut_ip):
        sshpassCmd1 = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + username + "@" + dut_ip + " 'ectool reboot_ec cold at-shutdown'"
        dlogger.info (sshpassCmd1)
        p = subprocess.Popen(sshpassCmd1, stdout=subprocess.PIPE, shell=True)
        sshpassCmd2 = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + username + "@" + dut_ip + " 'shutdown -P now'"
        dlogger.info (sshpassCmd2)
        p = subprocess.Popen(sshpassCmd2, stdout=subprocess.PIPE, shell=True)
        time.sleep(shutdown_wait_time)
        if not check_if_remote_system_is_live(dut_ip):
            dlogger.info ("System shutdown successfull.")
            for i in range(reboot_wait_time):
                time.sleep(1)
                if check_if_remote_system_is_live(dut_ip):
                    dlogger.info ("Waiting for %d seconds for device initialization after boot."%(wait_device_initialization))
                    time.sleep(wait_device_initialization)
                    return True
            dlogger.info ("System didnt come back on with ectool reboot ec. There might be chipset force shutdown issue in ec log")
            dlogger.info ("Trying ec powerbtn wake to continue the test")
            ec_pwrbtn()
            for i in range(reboot_wait_time):
                time.sleep(1)
                if check_if_remote_system_is_live(dut_ip):
                    dlogger.info ("Waiting for %d seconds for device initialization after boot."%(wait_device_initialization))
                    time.sleep(wait_device_initialization)
                    return True    
        else:
            dlogger.info ("system didn't shutdown after %d seconds wait delay" % (shutdown_wait_time))
            return False
    else:
        dlogger.info ("DUT is not live")
        return False

def run_suspend(dut_ip, username="root", password="test0000"):
    if check_if_remote_system_is_live(dut_ip):
        suspendCmd = 'suspend_stress_test -c 1'
        suspend_output = run_command(suspendCmd, dut_ip )
        if suspend_output:
            if searchPatternMatched(suspend_output, pattern_list=["suspend_failures: 0", "firmware log errors: 0"]):
                return True 
            else:
                print ("No suspend failures observed!")
                return False   
        else:
            return False    

def searchPatternMatched(searchInString, pattern_list=None):
    if not pattern_list:
        return False
    
    matched = []
    for search_item in pattern_list:
        if re.search(search_item, searchInString, re.IGNORECASE):
            print ("MATCHED ON [%s]" % (search_item))
            matched.append(search_item)
    if len(matched) >= 1:
        return matched
    else:
        return False

def is_tool(name):
    """Check whether `name` is on PATH."""

    from distutils.spawn import find_executable

    return find_executable(name) is not None

def servod_process():
    import subprocess    
    script_working_directory = os.getcwd()
    # os.system("pgrep servod | xargs sudo kill -9")
    p = subprocess.Popen('pgrep servod', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    retval = p.wait()
    out, err = p.communicate()

    if out:
        servod_pid = int(out.strip())
        dlogger.info('servod Process found.')
        return True

    dlogger.info('starting a fresh servod...')
    dlogger.info (os.getcwd())
    

    servod_cmd = 'sudo ' + 'servod ' + '--board=volteer ' + '&'
    os.system(servod_cmd)
    time.sleep(15)
    
    
    output = subprocess.Popen(['pgrep', 'servod'], stdout=subprocess.PIPE).communicate()[0]

    if output:
        dlogger.info("Servod started successfully")
        return True
    else:
        dlogger.info("Servod couldn't be started successfully. Exiting test.")
        return False

def g3_check():
    ec_uart_capture_enable_command = 'dut-control ec_uart_capture:on'
    ec_uart_capture_disable_command = 'dut-control ec_uart_capture:off'
    ec_console_system_status_command ='dut-control ec_uart_cmd:powerinfo'
    ec_console_system_status_output = 'dut-control ec_uart_stream'
    os.system(ec_uart_capture_enable_command)
    os.system(ec_console_system_status_command)
    system_status_check = os.popen(ec_console_system_status_output).read()
    os.system(ec_uart_capture_disable_command)
    dlogger.info (system_status_check)
    
    if system_status_check.find("G3") != -1:
        dlogger.info ("System successfully went to G3")
        return True
    else:
        dlogger.info ("System is not in G3.")
        return False
        

def servo_coldboot(dut_ip, username="root", password="test0000", shutdown_wait_time=10):
    pwr_btn_command = 'dut-control pwr_button:press sleep:0.5 pwr_button:release'
    ec_reset_command = 'dut-control ec_uart_cmd:reboot'
    dlogger.info ("Sending shutdown command to the DUT")
    sshpassCmd = "sshpass -p " + password + " ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + username + "@" + dut_ip + " 'shutdown -P now'"
    dlogger.info (sshpassCmd)
    p = subprocess.Popen(sshpassCmd, stdout=subprocess.PIPE, shell=True)
    dlogger.info ("Waiting for %d seconds for shutdown"%(shutdown_wait_time))
    time.sleep(shutdown_wait_time)
    if not check_if_remote_system_is_live(dut_ip):
        dlogger.info ("System shutdown successfull.")
    else:
        dlogger.info ("System shutdown not successful. Trying again after 10 seconds.")
        time.sleep(10)
        dlogger.info ("Sending shutdown command 2nd time to the DUT")
        p = subprocess.Popen(sshpassCmd, stdout=subprocess.PIPE, shell=True)
        dlogger.info ("Waiting for %d seconds for shutdown"%(shutdown_wait_time))
        time.sleep(shutdown_wait_time)
        if check_if_remote_system_is_live(dut_ip):
            dlogger.info ("System is not shutingdown with command. 2 attempts tried. Exiting test")
            return False
	
    #os.chdir(cros_sdk_path)	
    #dlogger.info (os.getcwd())
    dlogger.info ("Will continue to check G3 for next 20 seconds.")
    g3_status = False
    for i in range(20):
        time.sleep(1)
        if g3_check():
            dlogger.info("DUT went into to G3 successfully")
            g3_status = True
            break
    if not g3_status:
        dlogger.error("DUT didnt enter G3 after %d seconds."%(shutdown_wait_time + 20) )
        return False
           

    dlogger.info ("Pressing powerbtn to poweron system")
    for i in range(3):
        os.system(pwr_btn_command)
        dlogger.info ("Waiting for %s minutes for the system to come up." %(reboot_wait_time_minute))
        for i in range(reboot_wait_time):
            time.sleep(1)
            if check_if_remote_system_is_live(dut_ip):
                dlogger.info("Waiting for %d seconds for device initialization after system boot." %(wait_device_initialization))
                time.sleep(wait_device_initialization)
                return True

    dlogger.info ("Powerbtn wake didnt work even after 3 attempts. Will try Ec reset to recover system")
    os.system(ec_reset_command)
    dlogger.info("Waiting for %s minutes after ec reset for the system to come up." % (reboot_wait_time_minute))
    for i in range(reboot_wait_time):
        time.sleep(1)
        if check_if_remote_system_is_live(dut_ip):
            dlogger.info("Waiting for %d seconds for device initialization after system boot." %(wait_device_initialization))
            time.sleep(wait_device_initialization)
            dlogger.info("Able to recover system with ec reset.")
            return True
    dlogger.info("3 attempts of powerbtn wake and 1 attempt of ec reset failed to recover system.")
    return False


def lid_s0ix_test(dut_ip, username="root", password="test0000"):
    lid_close_command = 'python' + ' ' + abs_cros_sdk_path + ' ' + 'dut-control ec_uart_cmd:lidclose'
    lid_open_command = 'python' + ' ' + abs_cros_sdk_path + ' ' + 'dut-control ec_uart_cmd:lidopen'

    if check_if_remote_system_is_live(dut_ip):
        system_loggedin_check_cmd = 'ls -l /home/chronos/user | grep -i Downloads'
        if run_command(system_loggedin_check_cmd, dut_ip):
            dlogger.info("DUT is logged in")
            dlogger.info("checking s0ix increment counter")
            s0ix_counter_check_after_test = "cat " + s0ix_residency_file
            s0ix_residency_before_s0ix = run_command(s0ix_counter_check_after_test, ip_address, username="root", password="test0000")
            dlogger.info("s0ix residency count before s0ix is: %s" %(s0ix_residency_before_s0ix))
        else:
            dlogger.info("DUT is not logged in. Exiting test as lidclose will shutdown the system.")
            sys.exit()

    os.chdir(cros_sdk_path)
    dlogger.info(os.getcwd())

    dlogger.info("Sending lidclose command")
    os.system(lid_close_command + '>/dev/null 2>&1')
    dlogger.info("lidclose waiting for %d seconds"% (s0ix_lidclose_wait))
    time.sleep(s0ix_lidclose_wait)
    dlogger.info("Sending lidopen command")
    os.system(lid_open_command + '>/dev/null 2>&1')
    dlogger.info("lidopen waiting for %d seconds" % (s0ix_lidopen_wait))
    time.sleep(s0ix_lidopen_wait)
    if check_if_remote_system_is_live(dut_ip):
        dlogger.info("checking s0ix increment counter")
        s0ix_counter_check_after_test = "cat " + s0ix_residency_file
        s0ix_residency_after_s0ix = run_command(s0ix_counter_check_after_test, ip_address, username="root", password="test0000")
        dlogger.info("s0ix residency count after s0ix is: %s" %(s0ix_residency_after_s0ix))
        if (int(s0ix_residency_after_s0ix) > int(s0ix_residency_before_s0ix)):
            dlogger.info("S0ix counter incremented")
            return True
        else:
            dlogger.info("S0ix counter didn't incremented. Will exit test.")
            return False
    else:
        dlogger.info("Unable to wake system up after lidopen")
        return False



if __name__ == "__main__":

    if not is_tool("sshpass"):
        dlogger.info ("sshpass is not installed. Please install sshpass with sudo apt-get install sshpass")
        dlogger.info ("sudo emerge sshpass if running from inside cros_sdk")

    parser = argparse.ArgumentParser()
    parser.add_argument('--testcase', dest='testcase_to_run', default = "", help='testcase to run is before reboot or suspend test')
    parser.add_argument('--test', dest='test_to_run', default = "reboot", help='test to run is either "reboot" or "lid_s0ix" or "suspend" or "rtc_coldboot" or "ec_coldboot" or servo_coldboot')
    parser.add_argument('--ip', dest='ip_address', help='provide remote system ip')
    parser.add_argument('--after_test_delay', dest='wait_device_initialization', default = 10, help='Provide Device initialization delay in seconds after test!')
    parser.add_argument('--count', dest='iteration_count', default = 5, help='Provide iteration count!')
    parser.add_argument('--command', dest='cmd_to_run', default = "dmesg --level=err", help='Please mention the command to check in double quotes!')
    parser.add_argument('--search_for', dest='search_patterns', help='provide one or many search strings with space. If found, test will FAIL/STOP.', nargs='+')
    args = parser.parse_args()

    pattern_list = args.search_patterns

    testcase = args.testcase_to_run.lower()
    cmd_to_run = args.cmd_to_run
    
    if args.ip_address:
        ip_address = args.ip_address
    else:
        ip_address = False
        dlogger.info ("check with --help or give cmd argument --ip <ip_address>")
        sys.exit(1)
        
    
    
    wait_device_initialization = args.wait_device_initialization
    iteration_count = args.iteration_count
    test_to_run = args.test_to_run
    
    print ("Testcase selected to run                                 :", testcase)
    print ("Test selected to run                                     :", test_to_run)
    print ("system ip address is                                     :", ip_address)
    print ("after_test_delay for device initialization in seconds    :", wait_device_initialization)
    print ("Iteration_count is                                       :", iteration_count)
    print ("cmd to run after selected test                           :", cmd_to_run)
    print ("stop test if pattern matches                             :", pattern_list)

    if test_to_run == "lid_s0ix":
        print ("s0ix_residency_file path is                              :", s0ix_residency_file)
        print ("cros_sdk_path is                                         :", cros_sdk_path)
        print ("abs_cros_sdk_path is                                     :", abs_cros_sdk_path)

    print ("**********************************************************")
    
    if test_to_run == "servo_coldboot" or test_to_run == "lid_s0ix":
        if servod_process():
            dlogger.info ("Servod PASS. Will continue test.**************")
        else:
            dlogger.info ("Servod not running.")
            dlogger.info ("Unable to start servod.")
            dlogger.info ("Exiting test.")
            sys.exit()


    if (sys.version_info > (3, 0)):
        input("Press Enter to continue...")
    else:
        raw_input("Press Enter to continue...")
    
        
    count = 0
    
    while (count < int(iteration_count)):
        dlogger.info ("******************************")
        dlogger.info ("******************************")
        dlogger.info ("STARTING ITERATION %d of %d" % (count, int(iteration_count)))
        dlogger.info ("******************************")
        dlogger.info ("******************************")

        if testcase:
            testcase_output = run_command(testcase, ip_address, username="root", password="test0000")
            dlogger.info (testcase_output)
            time.sleep(5)

        # if test_to_run == "suspend":
        #     print (run_suspend(ip_address))
        # elif test_to_run == "rtc_coldboot":
        #     print (rtc_cold_reboot(ip_address, wait_device_initialization=wait_device_initialization ))
        # elif test_to_run == "ec_coldboot":
        #     print (ec_cold_reboot(ip_address, wait_device_initialization=wait_device_initialization ))
        # elif test_to_run == "servo_coldboot":
        #     print (servo_coldboot(ip_address))
        # elif test_to_run == "lid_s0ix":
        #     print (lid_s0ix_test(ip_address))
        # else:
        #     print (run_reboot(ip_address, wait_device_initialization=wait_device_initialization))

        result = False

        if test_to_run == "suspend":
            result = run_suspend(ip_address)
        elif test_to_run == "rtc_coldboot":
            result = rtc_cold_reboot(ip_address)
        elif test_to_run == "ec_coldboot":
            result = ec_cold_reboot(ip_address)
        elif test_to_run == "servo_coldboot":
            result = servo_coldboot(ip_address)
        elif test_to_run == "lid_s0ix":
            result = lid_s0ix_test(ip_address)
        else:
            result = run_reboot(ip_address)

        if not result:
            dlogger.info ("Exiting test.")
            break   
        
        count = count + 1
        cmd_output = run_command(cmd_to_run, ip_address, username="root", password="test0000")
        dlogger.info (cmd_output)
        if cmd_output:       
            if searchPatternMatched(cmd_output, pattern_list):
                break
            else:
                dlogger.info ("cmd %s successfull!"%(cmd_to_run))
        else:
            dlogger.info ("please check the command you are trying!. Not exiting test for command failure.")
            #dlogger.info ("Exiting test.")
            #break
    dlogger.info ("******************************")
    dlogger.info ("******************************")
    dlogger.info ("Completed ITERATION %d of %d" % (count, int(iteration_count)))
    dlogger.info ("******************************")
    dlogger.info ("******************************")
