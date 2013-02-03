import os, subprocess, commands, time
from subprocess import Popen, PIPE

VIDEO_PREFIX =	"/video/preen"
SKINS_LIST =	"http://anomiesoftware.com/downloads/preenSkinsLaika1.xml"
SKINS_FOLDER =	"~/Library/Application\ Support/Plex/addons/"
SKINS_FOLDER_PYTHON = "~/Library/Application Support/Plex/addons/"

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
  


def PreenMainMenu():
	Log("starting PreenMainMenu")
	return SkinBrowser()

# This function looks through our Dict for every skin we are tracking
# For each skin it adds a menu item which will start the download of the skin
def SkinBrowser():
	Log("starting SkinBrowser")
	dir = MediaContainer(viewGroup="InfoList")

	# for every skin in the Dict add a menu item to download the skin if the skin is for Laika
	currentSkinList = Dict[ASSkinDictionaryDefault]
	currentSkinList.sort(key=str.lower)
	
	for knownSkin in currentSkinList:
		if ( Data.Exists("skinfo." + String.Encode(knownSkin)) ):
			knownSkinDict = Data.LoadObject("skinfo." + String.Encode(knownSkin))
			Log("adding to SkinBrowserMenu: %s" % knownSkinDict[ASSkinNameDefault])
			if ( ASCompatibilityDefault in knownSkinDict ) :
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
		
# This function will download a selected skin with git
def DownloadSkin(sender, whichSkin):
	Log("starting DownloadSkin")

	resultOut = ""
	resultError = ""
	
	# if the folder for the skin exists we just go to that folder and pull the skin.
	# if it doesn't exist, we go to the path and run git clone
	if (not os.path.exists(os.path.expanduser(SKINS_FOLDER_PYTHON + Data.LoadObject("skinfo." + whichSkin)[ASServerFolderDefault]))):
		Log("starting clone")
		theCommand = ['sh', '-c', \
			'cd ' + os.path.expanduser(SKINS_FOLDER) + '; ' + \
			'/usr/local/git/bin/git clone git://github.com/' + Data.LoadObject("skinfo." + whichSkin)[ASSkinPathDefault] + \
			" " + Data.LoadObject("skinfo." + whichSkin)[ASServerFolderDefault] + " " + \
			'&> /dev/null &']

		theProcess = subprocess.Popen(theCommand, stdin=PIPE, stdout=PIPE, stderr=PIPE)
		resultOut, resultError = theProcess.communicate()
		return MessageContainer(
			L("Download started."),
			L("This skin has started downloading.")
		)

	else:
		Log("starting pull")
		theCommand = ['sh', '-c', 'cd ' +  os.path.expanduser(SKINS_FOLDER_PYTHON + Data.LoadObject("skinfo." + whichSkin)[ASServerFolderDefault]) + '; ' \
			'git pull']
		theProcess = subprocess.Popen(theCommand, stdin=PIPE, stdout=PIPE, stderr=PIPE)
		resultOut, resultError = theProcess.communicate()
		return MessageContainer(
			L("Update started."),
			L("This skin has started updating.")
		)
		

# ProcessSkinsList downloads a skin list (XML) from anomiesoftware.com
# It then adds that to the plugin's Data storage provides by PMS
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
