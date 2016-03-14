import urllib
import urllib2
import json
import simplejson
import sys
import os
import requests
import arcpy
import ConfigParser
import datetime
import logging
import uuid
from xml.etree import ElementTree as ET
import nltk
from nltk import word_tokenize, data
import time

nltk.data.path.append('E:\\AGO_Load_Scripts\\new_ago\update_tools\\nltk_data')

http_proxy = "http://proxy.hud.gov:8080"
https_proxy = "https://proxy.hud.gov:8443"

proxyDict = {
	"http": http_proxy,
	"https": https_proxy
}

base_path = str(os.path.dirname(os.path.realpath('__file__'))).replace("\\", "/")
base_path = base_path+'/new_ago/update_tools'

# Create requisite directories
class DirMGMT(object):
    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        self.baseLog = ConfigFile(base_path).log_folder
        self.logDir = os.path.join(self.baseLog, "run_" + self.timestamp)
        self.service_temp_dir = os.path.join(base_path, "tempDir")
        self.setDir = os.path.join(base_path, "settings")
        self.lgr = logging.getLogger('update_tools')
        self.lgr2 = logging.getLogger('run_update')


    def dirMgmt(self):
        reqDirs = [self.service_temp_dir, self.baseLog, self.logDir, self.setDir]
        for d in reqDirs:
            if not os.path.isdir(d):
                os.mkdir(d)
        self.logMgmt()

    def logMgmt(self):
        self.lgr.setLevel(logging.DEBUG)
        self.lgr2.setLevel(logging.DEBUG)
        # add a file handler
        fh = logging.FileHandler(os.path.join(self.logDir, 'run_logfile.log'))
        fh2 = logging.FileHandler(os.path.join(self.logDir, 'run_logfile.log'))

        fh.setLevel(logging.INFO)
        fh2.setLevel(logging.INFO)

        # create a formatter and set the formatter for the handler.
        frmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        frmt2 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        fh.setFormatter(frmt)
        fh2.setFormatter(frmt2)

        # add the Handler to the logger
        self.lgr.addHandler(fh)
        self.lgr2.addHandler(fh)

        # You can now start issuing logging statements in your code
        self.lgr.info('Logger Created') # Neither will this.

    def createSetLogFile(self, servicename):
        logSet = os.path.join(self.logDir, servicename)
        os.mkdir(logSet)
        # setDirs = [logSet, logSet+'/sd', logSet+'/settings']
        # for d in setDirs:
        #     os.mkdir(d)


class ConfigFile(object):
    def __init__(self, base_path):
        self.settings = ConfigParser.ConfigParser()
        self.settings.read(base_path+'/config.ini')
        self.user_profile = str(self.settings.get('USER PARAMETERS', 'AGOuser'))
        self.pswd = str(self.settings.get('USER PARAMETERS', 'Password'))
        self.mxd_folder = str(self.settings.get('MXD Folder', 'MXDfolder'))
        self.ago_group = str(self.settings.get('OPEN DATA GROUP', 'Group'))
        self.log_folder = str(self.settings.get('LOG FOLDER', 'Logfolder'))


class GetLayerProperties:
    def __init__(self, mxd_folder, mxd_file):
        self.mxd_file = mxd_file
        mxd = arcpy.mapping.MapDocument(r""+mxd_folder+"/"+mxd_file)
        df = arcpy.mapping.ListDataFrames(mxd, "")[0]
        lyr = arcpy.mapping.ListLayers(mxd, "", df)[0]
        self.lyr = arcpy.mapping.ListLayers(mxd, "", df)[0]
        self.lyr_name = str(self.lyr)
        self.lyr_desc_check = str(self.lyr.description.encode('ascii', 'ignore'))

        # tokenize the test description
        from nltk import word_tokenize
        self.utag_token_check = word_tokenize(self.lyr_desc_check)

        # Return layer with uTag in the description
        self.utag_position = -1
        self.lyr_desc = self.check_desc()

        # Update the mxd
        lyr.description = self.lyr_desc
        mxd.save()

        self.utag_token = word_tokenize(self.lyr_desc)
        self.utag = self.utag_token[self.utag_position]
        self.lyr_tag = str(self.lyr.credits)
        self.words = []


    def check_desc(self):
        if 'uTag' not in self.utag_token_check:
            utagval = str(uuid.uuid4())
            DirMGMT().lgr.info("No uTag found. Assigning " + utagval + " as uTag for this service.")
            DirMGMT().lgr.info("The new description will read: " + self.lyr_desc_check + '\n\n uTag: ' + utagval)
            return self.lyr_desc_check + '\n\n uTag: ' + utagval
        else:
            if len(self.utag_token_check[-1]) == 36:
                DirMGMT().lgr.info("Found a valid uTag")
                return self.lyr_desc_check
            else:
                for idx, val in enumerate(self.utag_token_check):
                    if len(val) == 36:
                        self.utag_position = idx
                        DirMGMT().lgr.info("found utag in an unexpected location. Consider moving uTag to the end of description.")
                        return self.lyr_desc_check

    # function that creates tags from layer description
    def generate_tags(self):
        # TODO package nltk on hud-machine
        # import nltk
        # nltk.download() #to download text data sets, including stop words
        from nltk.corpus import stopwords
        from nltk import word_tokenize
        from nltk import pos_tag
        tokens = word_tokenize(self.lyr_desc)
        tokens = [w for w in tokens if not w.lower() in stopwords.words("english")]
        tokens = [w for w in tokens if not len(w) < 2]
        self.words = []
        for w in tokens:
            if tokens.count(w) > 1:
                tokens.remove(w)
        token_tag = pos_tag(tokens)
        if str(self.lyr.credits):
            self.words.append(str(self.lyr.credits))
        for w in token_tag:
            if w[1] == 'NNP' and w[0] != 'uTag' and w[0] != 'Metadata' and w[-1] != 36:
                self.words.append(w[0])
        self.words.append(self.utag)
        return self.words


class SettingsFile(object):
    def __init__(self, base_path, inputfile):
        self.inputfile = inputfile
        self.settings_file = str(base_path+"/settings/settings_"+inputfile[:-4]+".ini")

    def createSetFile(self, service_title, mxd_folder, tags, description, ago_group, user_profile, pswd):
        cfgfile = open(self.settings_file, 'w')
        sdSettings = ConfigParser.ConfigParser()
        sdSettings.add_section('FS_INFO')
        sdSettings.set('FS_INFO', 'SERVICENAME', service_title)
        sdSettings.set('FS_INFO', 'MXD', mxd_folder+"/"+self.inputfile)
        sdSettings.set('FS_INFO', 'TAGS', ', '.join(tags))
        sdSettings.set('FS_INFO', 'DESCRIPTION', description)
        sdSettings.set('FS_INFO', 'MAXRECORDS', str(1000))
        sdSettings.add_section('FS_SHARE')
        sdSettings.set('FS_SHARE', 'SHARE', True)
        sdSettings.set('FS_SHARE', 'EVERYONE', 'true')
        sdSettings.set('FS_SHARE', 'ORG', 'true')
        sdSettings.set('FS_SHARE', 'GROUPS', ago_group)
        sdSettings.add_section('AGOL')
        sdSettings.set('AGOL', 'USER', user_profile)
        sdSettings.set('AGOL', 'PASSWORD', pswd)
        sdSettings.write(cfgfile)
        cfgfile.close()


class ReadSF(object):
    def __init__(self, settingfile_input):
        self.settingfile_input = settingfile_input
        self.config = ConfigParser.ConfigParser()
        self.config.read(settingfile_input)
        self.servicename = self.config.get('FS_INFO', 'SERVICENAME')
        self.mxd = self.config.get('FS_INFO', 'MXD')
        self.tags = self.config.get('FS_INFO', 'TAGS')
        self.description = self.config.get('FS_INFO', 'DESCRIPTION')
        self.desc_token = word_tokenize(self.description)[-1]
        self.maxrecords = self.config.get('FS_INFO', 'MAXRECORDS')
        self.share = self.config.get('FS_SHARE', 'SHARE')
        self.everyone = self.config.get('FS_SHARE', 'EVERYONE')
        self.org = self.config.get('FS_SHARE', 'ORG')
        self.groups = self.config.get('FS_SHARE', 'GROUPS')
        self.user = self.config.get('AGOL', 'USER')
        self.pwd = self.config.get('AGOL', 'PASSWORD')


class AGOLHandler(object):
    def __init__(self, username, password, serviceName, utag):
        self.username = username
        self.password = password
        self.serviceName = serviceName
        self.utag = utag
        self.token, self.http = self.getToken(username, password)
        self.itemID = self.findItem("Feature Service")
        self.SDitemID = self.findItem("Service Definition")
        self.jresp = self.jresp

    def getToken(self, username, password, exp=60):

        referer = "http://www.arcgis.com/"
        query_dict = {'username': username,
                      'password': password,
                      'expiration': str(exp),
                      'client': 'referer',
                      'referer': referer,
                      'f': 'json'}

        query_string = urllib.urlencode(query_dict)
        url = "https://www.arcgis.com/sharing/rest/generateToken"

        token = json.loads(urllib2.urlopen(url + "?f=json", query_string).read())

        if "token" not in token:
            DirMGMT().lgr.error(token['error'])
            sys.exit()
        else:
            httpPrefix = "http://www.arcgis.com/sharing/rest"
            if token['ssl'] == True:
                httpPrefix = "https://www.arcgis.com/sharing/rest"

            return token['token'], httpPrefix

    def findItem(self, findType):
        #
        # Find the itemID of whats being updated
        #
        searchURL = self.http + "/search"

        query_dict = {'f': 'json',
                      'token': self.token,
                      'q': "tags:\"" +
                           self.utag +
                           "\" AND owner:\"" +
                           self.username +
                           "\" AND type:\"" +
                           findType + "\""}

        DirMGMT().lgr.info("Querying AGO for " + self.serviceName + " " + findType + " now...")

        jsonResponse = sendAGOLReq(searchURL, query_dict)

        if jsonResponse['total'] == 0:
            DirMGMT().lgr.info("\nCould not find a service to update. If you expected something to be there, check the service name in the settings.ini")
            # sys.exit()
            self.jresp = 0
            pass

        elif jsonResponse['total'] == 1:
            DirMGMT().lgr.info("found {} : {}".format(type, jsonResponse['results'][0]["id"]))
            self.jresp = 1
            return jsonResponse['results'][0]["id"]

        else:
            DirMGMT().lgr.info("There appears to be a total of " + str(jsonResponse['total']) + " objects with the same uID. Remove any duplicates.")
            self.jresp = 0

    def publish_new(self, mxd_folder, mxd, settingfile_input):

        service_lower = ReadSF(settingfile_input).servicename.replace(' ', '_')

        # tempDir = os.path.join(base_path, "tempDir")
        tempDir = DirMGMT().service_temp_dir
        finalSD = os.path.join(tempDir, service_lower + ".sd")

        makeSD(mxd_folder + "/" + mxd, service_lower, tempDir, finalSD, str(1000), settingfile_input)
        arcpy.SignInToPortal_server(ReadSF(settingfile_input).user, ReadSF(settingfile_input).pwd,
                                    "http://www.arcgis.com/")

        arcpy.UploadServiceDefinition_server(finalSD,
                                             "My Hosted Services",
                                             "#",
                                             "#",
                                             "FROM_SERVICE_DEFINITION",
                                             "#",
                                             "STARTED",
                                             "USE_DEFINITION",
                                             "SHARE_ONLINE",
                                             "PUBLIC",
                                             "SHARE_ORGANIZATION",
                                             ReadSF(settingfile_input).groups)
        DirMGMT().lgr.info(ReadSF(settingfile_input).servicename + " has been published.")


        # Return the Feature Service's ID
        searchURL = self.http + "/search"
        feature_service = "Feature Service"
        query_dict = {'f': 'json',
                      'token': self.token,
                      'q': "tags:\"" + self.utag + "\" AND owner:\"" + self.username + "\" AND type:\"" + feature_service + "\""}

        jsonResponse = sendAGOLReq(searchURL, query_dict)
        feature_id = jsonResponse['results'][0]['id']


        # Set sharing on Feature Service
        everyone = ReadSF(settingfile_input).everyone
        orgs = ReadSF(settingfile_input).org
        groups = ReadSF(settingfile_input).groups
        inputUsername = ReadSF(settingfile_input).user
        inputPswd = ReadSF(settingfile_input).pwd
        serviceName = ReadSF(settingfile_input).servicename

        #TODO Remove global if possible
        # global agol
        agol = AGOLHandler(inputUsername, inputPswd, serviceName, ReadSF(settingfile_input).desc_token)
        enableSharing(feature_id, everyone, orgs, groups)

    def update_attributes(self, settingfile_input):
        searchURL = self.http + "/search"
        feature_service = "Feature Service"

        query_dict = {'f': 'json',
                      'token': self.token,
                      'q': "tags:\"" + self.utag + "\" AND owner:\"" + self.username + "\" AND type:\"" + feature_service + "\""}

        jsonResponse = sendAGOLReq(searchURL, query_dict)
        if jsonResponse['total'] == 0:
            #feature_id = jsonResponse['results'][0]['id']
            DirMGMT().lgr.error("\n.Couldn't find the service.\n")
            sys.exit()

        else:
            #jsonResponse = sendAGOLReq(searchURL, query_dict)
            feature_id = jsonResponse['results'][0]['id']

        # Update
        updateURL = agol.http + '/content/users/{}/items/{}/update'.format(agol.username, feature_id)

        sentence_break = data.load('tokenizers/punkt/english.pickle')

        temp_desc = ReadSF(settingfile_input).description
        utagloc = temp_desc.find('uTag')
        cut = temp_desc[utagloc:utagloc+42]
        temp_desc = temp_desc.replace(cut, '')
        # TODO remove tags from
        temp_tags = ReadSF(settingfile_input).tags
        # utag = temp_tags.split()[-1]
        # lutag = temp_tags.rfind(utag)-2
        # temp_tags = temp_tags[0:lutag]


        url = updateURL + "?f=json&token=" + agol.token + \
              "&type=Feature Service" \
              "&title=" + agol.serviceName.replace('_', ' ') + \
              "&tags=" + temp_tags + \
              "&snippet=" + sentence_break.tokenize(ReadSF(settingfile_input).description.strip())[0] + \
              "&description=" + temp_desc
              # "&description=" + ReadSF(settingfile_input).description.replace("\n\nuTag: "+ReadSF(settingfile_input).tags[-1], '')

        response = requests.post(url)
        itemPartJSON = json.loads(response.text)

        if "success" in itemPartJSON:
            # itemPartID = itemPartJSON['id']
            itemPartTitle = itemPartJSON['id']
            DirMGMT().lgr.info("updated Feature Layer:   {}".format(itemPartTitle))
            return True
        else:
            DirMGMT().lgr.error("\n.sd file not uploaded. Check the errors and try again.\n")
            DirMGMT().lgr.error(itemPartJSON)
            sys.exit()


def enableSharing(newItemID, everyone, orgs, groups):
    #
    # Share an item with everyone, the organization and/or groups
    #

    shareURL = agol.http + '/content/users/{}/items/{}/share'.format(agol.username, newItemID)

    if groups == None:
        groups = ''

    query_dict = {'f': 'json',
                  'everyone': everyone,
                  'org': orgs,
                  'groups': groups,
                  'token': agol.token}

    jsonResponse = sendAGOLReq(shareURL, query_dict)

    DirMGMT().lgr.info("successfully shared...{}...".format(jsonResponse['itemId']))


def sendAGOLReq(URL, query_dict):
    #
    # Helper function which takes a URL and a dictionary and sends the request
    #

    query_string = urllib.urlencode(query_dict)

    jsonResponse = urllib.urlopen(URL, query_string)
    jsonOuput = json.loads(jsonResponse.read())
    print jsonOuput

    wordTest = ["success", "results", "services", "notSharedWith"]
    if any(word in jsonOuput for word in wordTest):
        return jsonOuput
    else:
        DirMGMT().lgr.error("\nfailed:")
        DirMGMT().lgr.error(jsonOuput)
        sys.exit()


def makeSD(mxd, serviceName, tempDir, outputSD, maxRecords, settingfile_input):
    #
    # create a draft SD and modify the properties to overwrite an existing FS
    #

    arcpy.env.overwriteOutput = True
    # All paths are built by joining names to the tempPath
    SDdraft = os.path.join(tempDir, "tempdraft.sddraft")
    newSDdraft = os.path.join(tempDir, "updatedDraft.sddraft")

    # arcpy.mapping.CreateMapSDDraft(MXD, SDdraft, serviceName, "MY_HOSTED_SERVICES")
    arcpy.mapping.CreateMapSDDraft(mxd, SDdraft, serviceName, "MY_HOSTED_SERVICES",
                                   None, False, None,
                                   ReadSF(settingfile_input).description,
                                   ReadSF(settingfile_input).tags)

    # Read the contents of the original SDDraft into an xml parser
    doc = ET.parse(SDdraft)

    root_elem = doc.getroot()
    if root_elem.tag != "SVCManifest":
        raise ValueError("Root tag is incorrect. Is {} a .sddraft file?".format(SDdraft))

    # Change service type from map service to feature service
    for config in doc.findall("./Configurations/SVCConfiguration/TypeName"):
        if config.text == "MapServer":
            config.text = "FeatureServer"

    #Turn off caching
    for prop in doc.findall("./Configurations/SVCConfiguration/Definition/" +
            "ConfigurationProperties/PropertyArray/" +
            "PropertySetProperty"):
        if prop.find("Key").text == 'isCached':
            prop.find("Value").text = "false"
        if prop.find("Key").text == 'maxRecordCount':
            prop.find("Value").text = maxRecords

    # Turn on feature access capabilities
    for prop in doc.findall("./Configurations/SVCConfiguration/Definition/Info/PropertyArray/PropertySetProperty"):
        if prop.find("Key").text == 'WebCapabilities':
            prop.find("Value").text = "Query"

    # Add the namespaces which get stripped, back into the .SD
    root_elem.attrib["xmlns:typens"] = 'http://www.esri.com/schemas/ArcGIS/10.2'
    root_elem.attrib["xmlns:xs"] = 'http://www.w3.org/2001/XMLSchema'

    # Write the new draft to disk
    with open(newSDdraft, 'w') as f:
        doc.write(f, 'utf-8')

    # Analyze the service
    analysis = arcpy.mapping.AnalyzeForSD(newSDdraft)

    if analysis['errors'] == {}:
        # Stage the service
        arcpy.StageService_server(newSDdraft, outputSD)
        DirMGMT().lgr.info("Created {}".format(outputSD))
    else:
        # If the sddraft analysis contained errors, display them and quit.
        DirMGMT().lgr.error(analysis['errors'])
        sys.exit()


def upload(fileName, tags, description):
    #
    # Overwrite the SD on AGOL with the new SD.
    # This method uses 3rd party module: requests
    #

    updateURL = agol.http + '/content/users/{}/items/{}/update'.format(agol.username, agol.SDitemID)

    filesUp = {"file": open(fileName, 'rb')}

    url = updateURL + "?f=json&token=" + agol.token + \
          "&filename=" + fileName + \
          "&type=Service Definition" + \
          "&title=" + agol.serviceName + \
          "&tags=" + tags + \
          "&description=" + description

    DirMGMT().lgr.info(url)

    n = 0
    while True:
    	try:
    		response = requests.post(url,files=filesUp,proxies=proxyDict)
    		print(response)
    		print(response.status_code)
    		print(1)
    		if response.status_code == requests.codes.ok:
    			itemPartJSON = simplejson.loads(response.text)
    			print(2)
    			break
    		else:
    			print(3)
    			n += 1
    			time.sleep(30)
    		print(4)
    	except Exception as inst:
    		DirMGMT().lgr.error(inst)

 #    # TODO Fix response, currently returning 504
	# n = 0
	# while True:
	# 	print (hello)
		# try:
		# 	response = requests.post(url, files=filesUp, proxies=proxyDict)
		# 	DirMGMT().lgr.info(response)
		# 	# return True
		# 	DirMGMT().lgr.info(itemPartJSON)
		# 	if response.getcode() == 200:
		# 		DirMGMT().lgr.info(response)
		# 		# return True
		# 		DirMGMT().lgr.info(itemPartJSON)
		# 		itemPartJSON = simplejson.loads(response.text)
		# 		break
		# 	n += 1
		# 	time.sleep(30)
		# except Exception as inst:
		# 	DirMGMT().lgr.error(inst)



    if "success" in itemPartJSON:
        itemPartID = itemPartJSON['id']
        DirMGMT().lgr.info("updated SD:   {}".format(itemPartID))
        return True
    else:
        DirMGMT().lgr.error("\n.sd file not uploaded. Check the errors and try again.\n")
        DirMGMT().lgr.error(itemPartJSON)
        sys.exit()


def publish():
    #
    # Publish the existing SD on AGOL (it will be turned into a Feature Service)
    #

    publishURL = agol.http + '/content/users/{}/publish'.format(agol.username)

    query_dict = {'itemID': agol.SDitemID,
                  'filetype': 'serviceDefinition',
                  'overwrite': 'true',
                  'f': 'json',
                  'token': agol.token}

    jsonResponse = sendAGOLReq(publishURL, query_dict)
    DirMGMT().lgr.info("successfully updated...{}...".format(jsonResponse['services']))
    return jsonResponse['services'][0]['serviceItemId']


def complete_update(base_path, mxd_folder, mxd, settingfile_input):
    DirMGMT().lgr.info("Starting Feature Service publish process")

    # Get settings variables
    inputUsername = ReadSF(settingfile_input).user
    inputPswd = ReadSF(settingfile_input).pwd
    MXD = ReadSF(settingfile_input).mxd
    serviceName = ReadSF(settingfile_input).servicename
    tags = ReadSF(settingfile_input).tags
    description = ReadSF(settingfile_input).description
    maxRecords = ReadSF(settingfile_input).maxrecords
    shared = ReadSF(settingfile_input).share
    everyone = ReadSF(settingfile_input).everyone
    orgs = ReadSF(settingfile_input).org
    groups = ReadSF(settingfile_input).groups

    # Assign servicename SD to namespace
    finalSD = os.path.join(base_path, 'tempDir', serviceName + ".sd")
    tempDir = DirMGMT().service_temp_dir

    # initialize AGOLHandler class.
    # TODO see if global can be removed
    global agol
    agol = AGOLHandler(inputUsername, inputPswd, serviceName, ReadSF(settingfile_input).desc_token)

    # find item
    agol.findItem('Service Definition')
    if agol.jresp == 0:
        agol.publish_new(mxd_folder, mxd, settingfile_input)
    else:
        # Turn map document into .SD file for uploading
        makeSD(MXD, serviceName.replace(' ', '_'), tempDir, finalSD, maxRecords, settingfile_input)

        # overwrite the existing .SD on arcgis.com
        if upload(finalSD, tags, description):

            # publish the sd which was just uploaded
            newItemID = publish()

            # share the item
            if shared:
                enableSharing(newItemID, everyone, orgs, groups)

            DirMGMT().lgr.info("finished.")
