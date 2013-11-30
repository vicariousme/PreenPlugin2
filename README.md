#Preen#

Preen is a skin manager for [Plex Home Theater and Plex Media Center](http://www.plexapp.com/desktop/). It has been available as a [Max OS X application](http://www.anomiesoftware.com/Anomie_Software/Preen.html) since 2010.

PreenPlugin exists to bring Preen as a Plugin for Plex Media Server. It is open-source Python code so that anyone can contribute. It can be modified to work for Windows. It can be maintained when I don't have time to maintain it.

##WARNING: Terrible Python code ahead.##
This is my first Python code, so if you hate, please contribute to making it better.

Git is currently required.

Desired Features:
 - Windows compatibility.
 - Automatically update skins.
 - Remove git requirement.
 - Show images from the skins when they are browsed.
 - Ability to change the skin from within the plugin.
 - Some soft of feedback about how far a git download has progressed.
	
Known Issues:
 - Not compatible with Alaska/Laika skin.
 - git pull won't work because of the skin encoding thing
 - we're naming folders improperly
 - Blur shows up twice (because we look at the skin names and the name Blur exists twice)

Changelog:
 - Nov 30, 2013: The plugin can download PHT skins with Git on the Mac.
 - Nov 30, 2013: The plugin now separates Laika skins from PHT skins.
 - Initial Release: The plugin can list skins from the skins list.
 - Initial Release: The plugin can download/update existing skins with git on the Mac.