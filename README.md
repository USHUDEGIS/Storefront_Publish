# AGO Update Tools

This is a python package that updates feature services in AGO. The module works by taking MXDs and converting
 them into Feature Services in ArcGIS Online. The MXDs should only contain one layer per MXD, and also must have a
 description for each title. Additionally, each layer should have the responsible program office in the credits section.
 It is important to ensure that each layer has a description or else the service will not be published.

## Dependencies
This script requires the following additional modules:

1. ArcPy (Tested with both 10.1 and 10.2)
2. Requests (Could be replaced with urllib1 or urllib2 if necessary)
3. NLTK (Required to create representative tags for the feature services)

The NTLK module requires the installation of the stopwords dictionary. This is noted as a TODO in the update_tools
 module and should be uncommented on the first run.

        # TODO package nltk on hud-machine
        # import nltk
        # nltk.download() #to download text data sets, including stop words
        from nltk.corpus import stopwords
        from nltk import word_tokenize
        from nltk import pos_tag

## Inputs
The script is controlled by a config file (config.ini). The config file is broken out into subsections that are used to
access the input parameters. Each section is demarcated using square brackets.

The script requires five inputs:

1. AGO Username;
2. AGO Password;
3. The directory where all service MXD's are stored;
4. The UID of the Open Data Group; and
5. A directory to store all logged outputs from the script.

### Example Config File
    [USER PARAMETERS]
    AGOuser: <USERNAME>
    Password: <PASSWORD>

    [MXD Folder]
    MXDfolder: //hwvanad4071/data/AGO Open Data/Layer MXDs

    [OPEN DATA GROUP]
    Group: 0beb510e69ee44db904a28dae41b8c31

    [LOG FOLDER]
    Logfolder: //hwvanad4071/data/AGO Open Data/log

Note that for the open data group, you must enter the uid of the group, not the group's name itself. Also note that for
the log folder input, all backslashes have been replaced with forward slashes. If you just copy and paste the path in,
remember to switch those.

## Logging
The module creates one log for each run and saves the sd files and settings for each service. A run directory is created
which provides a timestamp of when the file was created. Contained with that directory should be a directory for
each service, the service's sd file and configuration settings. The file structure is diagrammed below

    +-- log_directory
    |   |
    |   --- run_[timestamp_1]
    |   |   --- [servicename_1]
    |   |   |   --- sd
    |   |   |   |   |
    |   |   |   |   -- [servicename].sd
    |   |   |   --- settings
    |   |   |       |
    |   |   |       -- [servicename].ini
    |   |   |
    |   |   +-- [servicename_2]
    |   |   +-- ...
    |   |   +-- [servicename_n]
    |   |   -- run_logfile.log
    |   |
    |   +-- run_[timestamp_2]
    |   +-- ...
    |   +-- run_[timestamp_n]

### The logfile
The log file by default reports at the info level as a way to help track the progress of the script and also to assist
in debugging. All warnings include the traceback and hopefully provide enough detail to resolve the issue. All logging
is controlled by two loggers defined in a class function call. Two loggers are used to help discern between the
 run_update script and the update_tools script. Logging can be controlled using the following:

    DirMGMT().lgr.info("This is an example info log for the update_tools script")
    DirMGMT().lgr2.error("This is an example error log for the run_update script")

Below is an example of a successful log output for a single service:

    2015-04-09 16:08:37,334 - update_tools - INFO - Logger Created
    2015-04-09 16:08:42,773 - update_tools - INFO - Found a valid uTag
    2015-04-09 16:08:44,755 - run_update - INFO - 8edf1d9c-4a1a-4e36-9efd-40e337b52079
    2015-04-09 16:08:44,844 - run_update - INFO - CDBG Economic Development Activity
    2015-04-09 16:08:44,855 - run_update - INFO - Log folder created.
    2015-04-09 16:08:49,513 - run_update - INFO - Settings File created. Path: C:/Users/C60544/Desktop/new_ago/
    update_tools/settings/settings_CDBG Economic Development Activity.ini
    2015-04-09 16:08:49,526 - update_tools - INFO - Starting Feature Service publish process
    2015-04-09 16:08:51,881 - update_tools - INFO - Querying AGO for CDBG Economic Development Activity Feature Service now...
    2015-04-09 16:08:52,951 - update_tools - INFO - found <type 'type'> : d94123ac375d41cca4950c514666e38f
    2015-04-09 16:08:52,964 - update_tools - INFO - Querying AGO for CDBG Economic Development Activity Service Definition now...
    2015-04-09 16:08:53,154 - update_tools - INFO - found <type 'type'> : ff4765eb8db747a8bb6fab6d2b260dfa
    2015-04-09 16:08:53,165 - update_tools - INFO - Querying AGO for CDBG Economic Development Activity Service Definition now...
    2015-04-09 16:08:53,289 - update_tools - INFO - found <type 'type'> : ff4765eb8db747a8bb6fab6d2b260dfa
    2015-04-09 16:16:48,967 - update_tools - INFO - Created C:/Users/C60544/Desktop/new_ago/update_tools\tempDir\
    CDBG Economic Development Activity.sd
    2015-04-09 16:17:17,013 - update_tools - INFO - updated SD:   ff4765eb8db747a8bb6fab6d2b260dfa
    2015-04-09 16:17:17,752 - update_tools - INFO - successfully updated...[{u'encodedServiceURL':
    u'http://services.arcgis.com/VTyQ9soqVukalItT/arcgis/rest/services/CDBG_Economic_Development_Activity/FeatureServer'
    , u'jobId': u'8c2c344f-1ca5-47ba-ae5e-dc4574d03e3b', u'serviceurl': u'http://services.arcgis.com/VTyQ9soqVukalItT/
    arcgis/rest/services/CDBG_Economic_Development_Activity/FeatureServer', u'type': u'Feature Service',
    u'serviceItemId': u'd94123ac375d41cca4950c514666e38f', u'size': 12050508}]...
    2015-04-09 16:17:17,940 - update_tools - INFO - successfully shared...d94123ac375d41cca4950c514666e38f...
    2015-04-09 16:17:17,951 - update_tools - INFO - finished.
    2015-04-09 16:17:17,963 - run_update - INFO - The complete_update function ran successfully.
    2015-04-09 16:17:18,529 - update_tools - INFO - Querying AGO for CDBG Economic Development Activity Feature Service now...
    2015-04-09 16:17:18,664 - update_tools - INFO - found <type 'type'> : d94123ac375d41cca4950c514666e38f
    2015-04-09 16:17:18,678 - update_tools - INFO - Querying AGO for CDBG Economic Development Activity Service Definition now...
    2015-04-09 16:17:18,796 - update_tools - INFO - found <type 'type'> : ff4765eb8db747a8bb6fab6d2b260dfa
    2015-04-09 16:17:21,108 - update_tools - INFO - updated Feature Layer:   d94123ac375d41cca4950c514666e38f
    2015-04-09 16:17:21,121 - run_update - INFO - The update_attributes function ran successfully.
    2015-04-09 16:17:23,132 - run_update - INFO -
    CDBG Economic Development Activity has run successfully. SD and settings files have been moved to log folder.


Note that when a service has completed, the info log includes a carriage return at the beginning of the info output
to help identify where the for loop occurs. This is because the script is designed to be run against a large number
of services.

## Script organization
The tool is composed of two parts: a script named 'run_update.py' that calls functions and classes in the
'update_tools.py' module. The update_tools module stores most of the variables within classes, which are later accessed
by class calls in the run_update script.

### run_update.py
The run_update script ensures that the environment is correctly configured by reading in the configuration settings and
setting up the requisite temporary directories. It then creates a list of all the MXDs contained within MXD folder, and
initiates a for loop that checks the MXD for any issues, assigns a unique id if one is not present, and checks for the
presence of that unique id in the ArcGIS Online environment. If the ID is found, the a new SD is created and then
uploaded to update the service. If the ID is not found, the service is published to the AGO environment. Note that the
initial upload can take considerably more time than a subsequent service update.

### update_tools.py
There are several classes and functions in this script. Here's a complete list of all of them and what they do:

#### The Update_tools.py Classes
The update_tools.py module contains 6 classes. They are:

1. DirMGMT
2. ConfigFile
3. GetLayerProperties
4. SettingsFile
5. ReadSF
6. AGOLHandler

##### The DirMGMT class:
The DirMGMT class handles the directories required, including the tempDir, the log sub-directories, and the settings
directories.

Upon initialization, it defines a few key variables, including:

1. A timestamp string in the following format: 'Year-Month-Day_Hour-Minute'. This is designed to stamp each feature
    service publication time;
2. Temporary directories for settings and sd files as well as the logging directories; and
3. The log file and the logging function calls.

The DirMGMT class also defines the following variables:

1. dirMgmt
2. logMgmt
3. createSetLogFile

Both dirMgmt and logMgmt takes no inputs and are responsible for creating directories if they are not already present
and creating the logging functions respectively. The createSetLogFile function requires the service name input to
then generate a log folder where all output files will be moved upon script completion or error.

Note that by default, the logging level is currently set to info. To change this, edit the logMgmt function.


##### The ConfigFile class:
The ConfigFile class is designed to store the configuration file variables and allow them to persist across functions.
The variables stored include:

        self.settings = ConfigParser.ConfigParser()
        self.settings.read(base_path+'/config.ini')
        self.user_profile = str(self.settings.get('USER PARAMETERS', 'AGOuser'))
        self.pswd = str(self.settings.get('USER PARAMETERS', 'Password'))
        self.mxd_folder = str(self.settings.get('MXD Folder', 'MXDfolder'))
        self.ago_group = str(self.settings.get('OPEN DATA GROUP', 'Group'))
        self.log_folder = str(self.settings.get('LOG FOLDER', 'Logfolder'))

##### The GetLayerProperties class:
This class is designed to access the MXD layer and save the layer's properties required for service publication,
which include: 1) Service name; 2) Description; and 3) Tags.

This class calls the NLTK (Natural Language Toolkit) to generate service tags from the layer's description and is
responsible for either generating or parsing the uid from the description. The best practice is to let the code append
the uid to the end of the description, however the code is capable of parsing the uid from anywhere within the
description. Currently the uid is simply a random string, however in the future there may be a need to develop a
meaningful uid (a composite of identifiable codes).

##### The SettingsFile class:
The SettingsFile class is responsible for generating the settings file used for each service. It is comprised of one
 function which requires 7 inputs, including: 1) the service title, 2) the mxd folder, 3) the service's tags,
 4) the service description, 5) the ArcGIS Online group, 6) the user profile name, 7) and the password, all of which
 are called using the ConfigFile class variables.

##### The ReadSF class:
The ReadSF class is solely responsible for storing the settingsfile variables set in SettingsFile class and make those
variables callable. It is used extensively in both run_update as well as update_tools.

##### The AGOLHandler class:
This class largely handles the interface with ArcGIS Online. It requires the settings file inputs to generate a token,
find items in ArcGIS Online, publish new items, and update the attributes. Each of these tasks are split into discrete
  functions:

1. getToken
2. findItem
3. publish_new
4. update_attributes


####  update_tools.py Functions
There are 6 discrete functions in the update_tools.py module:

1. enableSharing
2. sendAGOLReq
3. makeSD
4. upload
5. publish
6. complete_update

#####  The enableSharing function:
The enableSharing function is a helper function that sets the sharing parameters of the service. The enableSharing
function relies on the sendAGOLReq function to send the request.

##### The sendAGOLReq function:
The sendAGOLReq function is a helper function that sends requests to ArcGIS Online.

##### The makeSD function:
The makeSD function handles the creation of SDs for both the publishing of new services as well as the updating of
 existing ones. It creates a draft SD and modifies the properties to overwrite an existing feature service. This function
 is where service capabilities may be modified. By default all services are set only to query.

##### The upload function:
The upload function overwrites the existing SD on ArcGIS Online with the new SD and is the method that
uses the requests module.

##### The publish function:
The publish function publishes the existing SD on ArcGIS Online.

##### The complete_update function:
Lastly, the complete_update function uses all of the update_tools classes and functions to update the feature service.
 This function is dependent on all of the other classes and functions.
