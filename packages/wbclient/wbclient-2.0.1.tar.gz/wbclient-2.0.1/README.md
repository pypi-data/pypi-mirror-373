# WhistleBlower
A tool to monitor and control FileMaker Server processes, and a managing FileMaker solution.
## In detail
WhistleBlower is a combination of a locally running Python script, and a monitoring FileMaker solution.
WhistleBlower can log information of a locally running FileMaker Server, and processes command line instructions on the server machine.
It can read all log files, it can log memory and cpu usage of all FileMaker Server processes, as well as gather information about all attached storage volumes.
WhistleBlower can also execute command line instructions, and return the results.
Communication with the monitoring FileMaker Server is done through the FileMaker Data API.
## Installation
WhistleBlower runs on all FileMaker Server platform (Ubuntu/WIndows/macOS), and requires a centrally running FileMaker Server that supports the FileMaker Data API (18+). There are not local FileMaker Server requirements.
Whistelblower als requires python3 to be installed,
### to install:
(Ubuntu 22.04)
running as root

<code></br>
cd ~</br>
mkdir wbclient</br>
cd wbclient</br>
apt install python3.10-venv</br>
</code>

(this will restart fmshelper!)

<code>
<br>
python3 -m venv wbclient </br>
source wbclient/bin/activate</br>
</code>

Using pip:
<code>
</br>
pip install wbclient </br>
</code>

Using a folder containing the distribution:
<code>
</br>
pip install ~/dist/wbclient-1.0.0-py3-none-any.whl </br>
</code>

If you just launch wbclient by typing
<code></br>
wbclient
</code>

The application will have created a wb_config.json file in
/root/.config/wbclient/wb_config.json
edit thei

### to configure
<code></br>
nano /root/.config/wbclient/wb_config.json
</code>

The file contains the following JSON entries:
#### serverid
The is the account used to log in to the central monitoring FileMaker Serve WhistleBlower FileMaker file.
#### host_name
The DNS name of the server that is hosting the WhistleBlower FileMaker file.
#### use_ssl
We strongly recommend setting this to "true".
#### port
Normally 443, but can be changed if your FileMaker Server is e.g. behind a NAT firewall.
#### database_name
Normally "whistleblower", but you can change this name.
#### post_layout
"wb_post" by default, this is the name of the FileMaker layout used during the logging Data API calls.
#### command_layout
"wb_commands" by default, this is the name of the FileMaker layout where the queue table for giving commands resides.
#### post_script
"process_data" by default, this is the name of the script that is execcuted after Data API calls that log information.
#### password
Enter the serverid value and the password entered here, also in the security settings of the WhistleBlower FileMaker file, and give this user the "whistleblower" privilege set.
#### post_interval
This is the time in seconds that the Python code pauses between subsequent actions - checking log files, querying system information and processing commands.
#### keyboard_control
"False" by default, use this if you want to control the python code using the keyboard. Can be handy when running the WhistleBlower tool from the console.
#### command_user
"fmserver" being the default account, because this is the default account FileMaker Server runs as. Theis can be altered to have less or more privileges on the FileMaker Server when executing commands.
#### command_whitelist
This JSON arrary can contain a number of commands that will be executed with elevated privileges, whatever the command_user.
### Running the WhistleBlower tool
the command "wbclient" can be invoked from the console, or the server can be configured to run whistleblower at startup.
#### important
wbclient should be run with elevated privileges. This means using sudo on Ubuntu or macOS, or running a PowerShell as Administrator on Windows.
