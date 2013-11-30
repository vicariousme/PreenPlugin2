import os, subprocess, commands, time
from subprocess import Popen, PIPE

VIDEO_PREFIX =	"/video/preen"
SKINS_LIST =	"http://anomiesoftware.com/downloads/preenSkinsPHT1.xml"

SKIMAGES_FOLDER = "http://www.anomiesoftware.com/skimages/"

#skin defaults - all are elements of ASSkinDictionay (except for itself)
ASSkinDictionaryDefault	= 		"ASSkinDictionary"
ASSkinNameDefault = 			"ASSkinName"
ASSkinPathDefault = 			"ASSkinPath"
ASServerFolderDefault = 		"ASServerFolder"
ASSkinBranchDefault = 			"ASSkinBranch"
ASAuthorNameDefault = 			"ASAuthorName"
ASConversionNameDefault = 		"ASConversionName"
ASStatusDefault = 				"ASStatus"
ASLastGitUpdateDefault = 		"ASLastGitUpdate"
ASSkinDemoURLDefault = 			"ASSkinDemoURL"
ASCompatibilityDefault = 		"ASCompatibility"

#other dictionary items
ASUserIDDefault = 				"ASUserID"
ASSendCurrentSkinDefault = 		"ASSendCurrentSkin"
ASAskedAboutSendSkinDefault = 	"ASAskedAboutSendSkin"

CACHE_INTERVAL       = 3600 # HTTP cache interval in seconds

NAME = L('Title')

ART  = 'art-default.jpg'
ICON = 'icon-default.png'

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, PreenMainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("Photos", viewMode="List", mediaType="photos")

    ## defaults
    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "List"
    MediaContainer.art = R(ART)
    DirectoryItem.thumb = R(ICON)
    VideoItem.thumb = R(ICON)
    
    HTTP.CacheTime = CACHE_1HOUR
	
	# Download the list of skins when PMS starts us
    processSkinsList()

# No preferences to validate currently
def ValidatePrefs():
	return
  

####################################################################################################
# PreenMainMenu
#
# This function is called when the Main Menu is needed.
# 
# For now all we do is return the menu.
####################################################################################################
def PreenMainMenu():
	Log("starting PreenMainMenu")
	return MediaCenterChooser()

####################################################################################################
# MediaCenterChooser
#
# Allow the user to tell us if they're using Plex Media Center (older) or
# Plex Home Theater (newer). The Plex version with the most users should
# be the first selection to reduce user clicking.
####################################################################################################
def MediaCenterChooser():
	dir = MediaContainer(viewGroup="InfoList")

	# The menu item for PHT skins
	dir.Append(
		Function(
			DirectoryItem(
				SkinBrowser,
				"Plex Home Theater Skins (Plex 1.0+)",
				subtitle="Skins for PHT",
				summary="Show skins for Plex Home Theater",
			), compatibility="PHT"
		)
	)

	# The menu item for Laika skins
	dir.Append(
		Function(
			DirectoryItem(
				SkinBrowser,
				"Laika Skins (Plex 9.5 - 9.8)",
				subtitle="Skins for Laika",
				summary="Show skins for the Laika version of Plex Media Center",
			), compatibility="Laika"
		)
	)

	return dir

####################################################################################################
# SkinBrowser
#
# This function looks through our Dict for every skin we are tracking
# For each skin it adds a menu item which will start the download of the skin
####################################################################################################
def SkinBrowser(sender, compatibility):
	Log("starting SkinBrowser")
	dir = MediaContainer(viewGroup="InfoList")

	# for every skin in the Dict add a menu item to download the skin if the skin is for Laika
	currentSkinList = Dict[ASSkinDictionaryDefault]
	currentSkinList.sort(key=str.lower)
	
	for knownSkin in currentSkinList:
		if ( Data.Exists("skinfo." + String.Encode(knownSkin)) ):
			knownSkinDict = Data.LoadObject("skinfo." + String.Encode(knownSkin))
			Log("adding to SkinBrowserMenu: %s" % knownSkinDict[ASSkinNameDefault])
			if ( knownSkinDict[ASCompatibilityDefault] == compatibility ) :
				skinDisplayName = knownSkinDict[ASSkinNameDefault]
				dir.Append(
					Function(
						DirectoryItem(
							DownloadSkin,
							skinDisplayName,
							subtitle=knownSkinDict[ASStatusDefault],
							summary="Original Skin By:\t" + knownSkinDict[ASAuthorNameDefault] + "\nConversion By:\t" + knownSkinDict[ASConversionNameDefault],
							thumb=SKIMAGES_FOLDER + knownSkinDict[ASSkinNameDefault] + ".jpeg",
							art=R(ART)
						), whichSkin=E(knownSkinDict[ASSkinNameDefault])
					)
				)
								
	return dir

####################################################################################################
# DownloadSkin
#
# This function downloads the skin when the user selects it. At a high level it:
#  - Figure out what folder the skin needs to go in
#  - Clone the skin if it doesn't already exist (in a new process)
#  - Pull the latest if the skin already exists (in a new process)
####################################################################################################
def DownloadSkin(sender, whichSkin):
	Log("starting DownloadSkin")

	resultOut = ""
	resultError = ""

	# figure out which folder we'll need to go to
	whichPlex = Data.LoadObject("skinfo." + whichSkin)[ASCompatibilityDefault]
	unescapedPath = "";
	escapedPath = "";
	if (whichPlex == "PHT"):
		unescapedPath = "~/Library/Application Support/Plex Home Theater/addons/"
		escapedPath = "~/Library/Application\ Support/Plex\ Home\ Theater/addons/"
	elif (whichPlex == "Laika"):
		unescapedPath = "~/Library/Application Support/Plex/addons/"
		escapedPath = "~/Library/Application\ Support/Plex/addons/"

	# if the folder for the skin exists we just go to that folder and pull the skin.
	# if it doesn't exist, we go to the path and run git clone
	if (not os.path.exists(os.path.expanduser(unescapedPath + Data.LoadObject("skinfo." + whichSkin)[ASServerFolderDefault]))):
		Log("starting clone")
		theCommand = ['sh', '-c', \
			'cd ' + os.path.expanduser(escapedPath) + '; ' + \
			'/usr/local/git/bin/git clone git://github.com/' + Data.LoadObject("skinfo." + whichSkin)[ASSkinPathDefault] + \
			" " + Data.LoadObject("skinfo." + whichSkin)[ASServerFolderDefault] + " " + \
			'&> /dev/null &']

		theProcess = subprocess.Popen(theCommand, stdin=PIPE, stdout=PIPE, stderr=PIPE)
		resultOut, resultError = theProcess.communicate()
		return MessageContainer(
			L("Download started."),
			L("This skin has started downloading.")
		)

	# if the skin already exists, we simply pull the latest version from github
	else:
		Log("starting pull")
		theCommand = ['sh', '-c', 'cd ' +  os.path.expanduser(unescapedPath + Data.LoadObject("skinfo." + whichSkin)[ASServerFolderDefault]) + '; ' \
			'git pull']
		theProcess = subprocess.Popen(theCommand, stdin=PIPE, stdout=PIPE, stderr=PIPE)
		resultOut, resultError = theProcess.communicate()
		return MessageContainer(
			L("Update started."),
			L("This skin has started updating.")
		)
		
####################################################################################################
# ProcessSkinsList
#
# ProcessSkinsList downloads a skin list (XML) from anomiesoftware.com
# It then adds that to the plugin's Data storage provides by PMS
####################################################################################################
def processSkinsList():
	Log("starting processSkinsList")
	#download the XML file and separate out the preenSkin elements
	skinListFromURL = XML.ElementFromURL(SKINS_LIST)
	skinList = skinListFromURL.xpath("//preenSkin")
	
	tempSkinList = []
	
	recordAttributes = {}
	for skinListType in skinList:
		# for every preenSkin element:
		#	if the data already exists in Data, update the data elements to ensure
		#		they have the latest data
		#	if the data doesn't exist, add the entire thing to Data
		if ( Data.Exists( "skinfo." + skinListType.get(ASSkinNameDefault) ) ):
			recordAttributes = Data.LoadObject( "skinfo." + skinListType.get(ASSkinNameDefault) )
			for anAttribute in skinListType.attrib:
				recordAttributes[anAttribute] = skinListType.attrib[anAttribute]
			tempSkinList.append(skinListType.get(ASSkinNameDefault))
		else:
			for anAttribute in skinListType.attrib:
				recordAttributes[anAttribute] = skinListType.attrib[anAttribute]
			tempSkinList.append(skinListType.get(ASSkinNameDefault))
		Data.SaveObject("skinfo." + String.Encode(skinListType.get(ASSkinNameDefault)), recordAttributes)
			
	Dict[ASSkinDictionaryDefault] = tempSkinList
