Preen
=====

Preen is a skin manager for Plex Media Center. It has been available as a Mac OS X application since 2010, which can be downloaded from http://www.anomiesoftware.com/Anomie_Software/Preen.html

This version of Preen is designed as a plugin for the Plex Media Server. It is open-source Python code so that anyone can contribute. It can be modified to work for Windows. It can be maintained when I don't have time to maintain it.

WARNING: Terrible Python code ahead. This is my first Python code, so if you hate it contribute to making it better.

Early versions will require git.

Initial Features:
	List skins from the skins list.
	Download/update existing skins with git on the Mac.
	
Desired Features:
	Windows compatibility.
	Automatically update skins.
	Remove git requirement.
	Show images from the skins when they are browsed.
	Ability to change the skin from within the plugin.
	Some soft of feedback about how far a git download has progressed.
	
Known Issues:
	Not compatible with Alaska/Laika skin.
	git pull won't work because of the skin encoding thing
	we're naming folders improperly
	Blur shows up twice (because we look at the skin names and the name Blur exists twice)