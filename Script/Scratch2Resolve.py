#!/usr/bin/env python3
'''
Scratch to Resolve - 2024-04-08 01.39 PM
By Andrew Hazelden <andrew@andrewhazelden.com>

# Overview:
This script imports Assimilate Scratch/LiveFX content into BMD Resolve Studio.

Each clip is created as a media pool item. The filename, tile color, and comment attributes are assigned to each node.

# Script Installation:

## Part A

Copy the included scripts into the "Assimilator/Defaults/Script/" folder on your hard disk.

On macOS this folder is located at:
/Library/Application Support/Assimilator/Defaults/Script/

On Windows this folder is located at:
C:\Program Files\Assimilate\Settings\Script\

## Part B

How to Enable the "Scratch to Resolve" script: 

1. Launch BMD Resolve Studio and Assimilate Scratch/LiveFX.

2. Once Assimilate has launched, click on the "System Settings..." button on the splash screen.

3. In the "System Settings" dialog select "Custom Commands".  

MacOS Custom Command:

	Title: Resolve Studio
	Type: Application
	File: /Library/Application Support/Assimilator/Defaults/Script/Scratch2Resolve-macOS.command
	XML Export: Selection

Windows Custom Command:

	Title: Resolve Studio
	Type: Application
	File: C:\Program Files\Assimilate\Settings\Script\Scratch2Resolve-Win.bat
	XML Export: Selection

To define the File attribute, click the "Set" button. 

4. In the "Set Executable" dialog change the "All Formats..." pop-up menu to "All Files..." to allow the selection of more file types.

Then in the path entry text field at the top-center of the dialog paste in the text:

macOS Path:
	/Library/Application Support/Assimilator/Defaults/Script/

Windows Path:
	C:\Program Files\Assimilate\Settings\Script\

Make sure the file "Scratch2Resolve-macOS.command" or "Scratch2Resolve-Win.bat" is selected. Then press the "Open" button to close the dialog.

5. Open a Scratch project and switch to the Construct tab. Select several clips.  In the Construct tab click on the "Tools" button. Then click on the Custom Commands > Resolve Studio" button to run this script.

6. Switch to Resolve Studio. The selected Scratch clips are now displayed in the media pool.


# Troubleshooting:

The "Scratch2Resolve-Win.bat" script on Windows expects your Python 3 executable to be in the PATH environment variable, and to have the filename of "python.exe". You can revise the script if your executable is named "python3.exe" or you want to use an absolute filepath.

If you click on the "Resolve Studio" custom command button and see the command prompt based error message "Could not connect to the foreground Resolve session" it means the Fusion Render Node or Fusion Studio processes running on the same system intercepted the content that was being passed to Resolve Studio. Quit the Fusion Render Node/Fusion Studio processes and things should work as expected.

If you click on the "Resolve Studio" custom command button and see the command prompt based error message "the following arguments are required: xml_path" it means you need to go back and adjust the custom command parameters. Change the "XML Export:" setting to "Selection".

# Script CLI Usage Example:

It is possible to run the included "Scratch2Resolve.py" python script from the command-line.

(Modify the path to the XML file in the example below to line up with your project's needs)

macOS CLI Command:
python3 "/Library/Application Support/Assimilator/Defaults/Script/Scratch2Resolve.py" "/Library/Application Support/Assimilator/Project/LiveLink/Temp/cmd-0.xml"

Windows CLI Command:
python "C:\Program Files\Assimilate\Settings\Script\Scratch2Resolve.py" "C:\ProgramData\Assimilator\Project\Project1\Temp\cmd-0.xml"


# Script Copyright:

The "Scratch2Resolve.py" script is based upon Assimilate's "s2nuke_v9.py" script:
/Library/Application Support/Assimilator/Defaults/Script/s2nuke_v9.py

The original "s2nuke_v9.py" script was provided with the following license terms:
* Copyright (C) 2018 ASSIMILATE BV.
*
* Permission to use, copy, modify, and distribute this software for any
* purpose with or without fee is hereby granted, provided that the above
* copyright notice and this permission notice appear in all copies.
*
* THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR IMPLIED
* WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF
* MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE AUTHORS AND
* CONTRIBUTORS ACCEPT NO RESPONSIBILITY IN ANY CONCEIVABLE MANNER.
'''

import xml.etree.ElementTree as ET
import sys, os, argparse, json, re, glob, platform

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

# The imp library will be depreciated in Python 3.12. Look for a replacement option at that time.
import imp

def FuScriptLib():
	lib_path = ''
	if sys.platform.startswith('darwin'):
		lib_path = '/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so'
	elif sys.platform.startswith('win'):
		lib_path = 'C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\fusionscript.dll'
	elif sys.platform.startswith('linux'):
		lib_path = '/opt/resolve/libs/Fusion/fusionscript.so'

	if not os.path.isfile(lib_path):
		print('[Resolve Studio] [Library Does Not Exist on Disk]', lib_path)

	bmd = imp.load_dynamic('fusionscript', lib_path)
	if bmd:
		sys.modules[__name__] = bmd
	else:
		raise ImportError('[Resolve Studio] Could not locate module dependencies')
	return bmd

def Resolve():
	app = FuScriptLib().scriptapp('Resolve')
	return app

def Fusion():
	app = FuScriptLib().scriptapp('Fusion', 'localhost')
	return app

# Get the Fusion objects
resolve = Resolve()
res = Resolve()
app = Resolve()
bmd = FuScriptLib()

def GetTimeline():
	project = GetProject()
	timeline = project.GetCurrentTimeline()

	if not timeline:
		if project.GetTimelineCount() > 0:
			timeline = project.GetTimelineByIndex(1)
			project.SetCurrentTimeline(timeline)

	return timeline

def GetProject():
	# Get the current Resolve timeline
	resolve = Resolve()
	projectManager = resolve.GetProjectManager()
	project = projectManager.GetCurrentProject()
	return project

def GetMediaPool():
	resolve = Resolve()
	projectManager = resolve.GetProjectManager()
	project = projectManager.GetCurrentProject()
	mediapool = project.GetMediaPool()
	return mediapool

def GetFolder(parentFolder, childFolder, mediapool):
	if parentFolder != None:
		for folder in parentFolder.GetSubFolderList():
			if folder.GetName() == childFolder:
				return folder
		else:
			return mediapool.AddSubFolder(parentFolder, childFolder)
	else:
		return None

def ImportMedia(clip_dict):
	print(clip_dict)
	project = GetProject()
	mediapool = GetMediaPool()

	mpItems = mediapool.ImportMedia([clip_dict['file']])
	if not mpItems:
		return
	for mpItem in mpItems:
		mpItem.SetClipProperty('StartIndex', clip_dict['in'])
		mpItem.SetClipProperty('EndIndex', clip_dict['out'])
		mpItem.SetClipProperty('Description', clip_dict['note'])

		# Clip Color
		if clip_dict['note_color'] == None:
			color = 'Blue'
		elif clip_dict['note_color'] == '0':
			color = 'Yellow'
		elif clip_dict['note_color'] == '1':
			color = 'Pink'
		elif clip_dict['note_color'] == '2':
			color = 'Green'
		elif clip_dict['note_color'] == '3':
			color = 'Blue'
		elif clip_dict['note_color'] == '4':
			color = 'Violet'
		elif clip_dict['note_color'] == '5':
			color = 'Orange'
		elif clip_dict['note_color'] == '6':
			color = 'Teal'
		elif clip_dict['note_color'] == '7':
			color = 'Pink'
		elif clip_dict['note_color'] == '8':
			color = 'Chocolate'
		elif clip_dict['note_color'] == '9':
			color = 'Tan'
		else:
			color = 'Blue'

		mpItem.SetClipColor(color)


def ParseClip(clip, clip_NB, clips_dict):
	clip_dict = {}
	clip_dict['uuid'] = clip.attrib['uuid']
	clip_dict['slot']='0'
	if 'type' in clip.attrib:
		clip_dict['type'] = clip.attrib['type']
	if 'slot' in clip.attrib:
		clip_dict['slot'] = clip.attrib['slot']
	if 'slot_len' in clip.attrib:
		clip_dict['slot_len'] = clip.attrib['slot_len']
	if 'layer' in clip.attrib:
		clip_dict['layer'] = clip.attrib['layer']
	if 'frame_no' in clip.attrib:
		clip_dict['frame_no'] = clip.attrib['frame_no']  # Only on the First clip of selection
	if 'frame_file' in clip.attrib:
		# Only on the First clip of selection
		clip_dict['frame_file'] = clip.attrib['frame_file']

	clip_dict['file'] = clip.find('file').text
	clip_dict['format'] = clip_dict['file'][-3:]
	clip_dict['name'] = clip.find('name').text

	# Remove any version numbers scratch might have added to the name
	idx = clip_dict['name'].find('[')
	if idx > 0:
		clip_dict['name'] = clip_dict['name'][0:idx]
	clip_dict['reel_id'] = ' '

	if clip.find('reel_id') is not None:
		clip_dict['reel_id'] = clip.find('reel_id').text

	clip_handles = clip.find('handles')
	clip_dict['in'] = clip_handles.find('in').text
	clip_dict['out'] = clip_handles.find('out').text
	clip_dict['length'] = clip.find('length').text

	clip_size = clip.find('size')
	clip_dict['width'] = clip_size.find('width').text
	clip_dict['height'] = clip_size.find('height').text
	clip_dict['aspect'] = '1'
	if clip.find('aspect') is not None:
		clip_dict['aspect'] = clip.find('aspect').text
	clip_dict['fps'] = clip.find('fps').text
	clip_dict['timecode'] = clip.find('timecode').text
	ColorGrade = clip.find('colorgrade')
	Input = ColorGrade.find('input')

	clip_dict['note'] = ''
	clip_dict['note_color'] = clip.find('note_color')

	if clip.find('notes') is not None:
		notes = clip.find('notes')
		note = notes.find('note')
		clip_dict['note_color'] = note.attrib['status']
		clip_dict['note'] = note.text

	# Import the footage
	ImportMedia(clip_dict)

def XML_Selection(xml):
	clip_NB = 1
	xml_infos = {}
	project={}

	tree = ET.parse(xml)
	root = tree.getroot()

	project['datetime'] = root.attrib['datetime']
	project['version'] = root.attrib['version']
	project['name'] =  root.attrib['project']
	project['project_path'] =  root.attrib['project_path']
	project['media_path'] =  root.attrib['media_path']
	project['temp_path'] = root.attrib['temp_path']
	project['watch_folder'] =  root.attrib['watch_folder'].replace('\\', '/')
	xml_infos['project'] = project

	output = root.find('output')
	outputRes = output.find('resolution')
	outputWidth=outputRes.find('w').text
	outputHeight=outputRes.find('h').text

	xml_infos['output_res'] = [outputWidth,outputHeight]
	xml_infos['output_fps'] = output.find('fps').text

	Selection = root.find('selection')
	group = Selection.attrib['group']
	xml_infos['group_name'] =  group
	construct = Selection.attrib['construct']
	xml_infos['construct_name'] = construct
	clips = Selection.findall('shot')

	print('[Importing Media]\n')
	clips_dict = {}
	for clip in clips:
		ParseClip(clip, clip_NB, clips_dict)

	return xml_infos

def Main():
	print('\n------------------')
	print('Scratch 2 Resolve')
	print('------------------')

	parser = argparse.ArgumentParser(
		description='''Import Assimilate Scratch/LiveFX Construct content into BMD Resolve Studio via an XML importer.'''
	)
	parser.add_argument('xml_path', help='The path to your Scratch xml file')
	args = parser.parse_args()

	xml = args.xml_path
	if xml:
		if app:
			# Open the Media page
			resolve.OpenPage('media')
	
			project = GetProject()
			mediapool = GetMediaPool()

			print('[XML Document] ' + xml + '\n\n')
			mClipData = XML_Selection(xml)
		else:
			print('[Scratch 2 Resolve] Could not connect to the active Resolve session')
	else:
		print('[Scratch 2 Resolve] XML filepath is invalid')
	print('[Done]')

if __name__ == '__main__':
	Main()
