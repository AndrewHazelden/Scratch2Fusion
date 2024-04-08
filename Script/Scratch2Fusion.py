#!/usr/bin/env python3
'''
Scratch to Fusion - 2024-04-08 01.39 PM
By Andrew Hazelden <andrew@andrewhazelden.com>

# Overview:
This script imports Assimilate Scratch/LiveFX content into BMD Fusion Studio.

Each clip is created as a Loader node in Fusion. The filename, tile color, and comment attributes are assigned to each node.

# Script Installation:

## Part A

Copy the included scripts into the "Assimilator/Defaults/Script/" folder on your hard disk.

On macOS this folder is located at:
/Library/Application Support/Assimilator/Defaults/Script/

On Windows this folder is located at:
C:\Program Files\Assimilate\Settings\Script\

## Part B

How to Enable the "Scratch to Fusion" script: 

1. Launch BMD Fusion Studio and Assimilate Scratch/LiveFX.

2. Once Assimilate has launched, click on the "System Settings..." button on the splash screen.

3. In the "System Settings" dialog select "Custom Commands".  

MacOS Custom Command:

	Title: Fusion Studio
	Type: Application
	File: /Library/Application Support/Assimilator/Defaults/Script/Scratch2Fusion-macOS.command
	XML Export: Selection

Windows Custom Command:

	Title: Fusion Studio
	Type: Application
	File: C:\Program Files\Assimilate\Settings\Script\Scratch2Fusion-Win.bat
	XML Export: Selection

To define the File attribute, click the "Set" button. 

4. In the "Set Executable" dialog change the "All Formats..." pop-up menu to "All Files..." to allow the selection of more file types.

Then in the path entry text field at the top-center of the dialog paste in the text:

macOS Path:
	/Library/Application Support/Assimilator/Defaults/Script/

Windows Path:
	C:\Program Files\Assimilate\Settings\Script\

Make sure the file "Scratch2Fusion-macOS.command" or "Scratch2Fusion-Win.bat" is selected. Then press the "Open" button to close the dialog.

5. Open a Scratch project and switch to the Construct tab. Select several clips.  In the Construct tab click on the "Tools" button. Then click on the Custom Commands > Fusion Studio" button to run this script.

6. Switch to Fusion Studio. The selected Scratch clips are now displayed in Fusion.


# Troubleshooting:

The "Scratch2Fusion-Win.bat" script on Windows expects your Python 3 executable to be in the PATH environment variable, and to have the filename of "python.exe". You can revise the script if your executable is named "python3.exe" or you want to use an absolute filepath.

If you click on the "Fusion Studio" custom command button and see the command prompt based error message "Could not connect to the foreground Fusion composite" it means the Fusion Render Node process running on the same system intercepted the content that was being passed to Fusion Studio. Quit the Fusion Render Node process and things should work as expected.

If you click on the "Fusion Studio" custom command button and see the command prompt based error message "the following arguments are required: xml_path" it means you need to go back and adjust the custom command parameters. Change the "XML Export:" setting to "Selection".

# Script CLI Usage Example:

It is possible to run the included "Scratch2Fusion.py" python script from the command-line.

(Modify the path to the XML file in the example below to line up with your project's needs)

python3 "/Library/Application Support/Assimilator/Defaults/Script/Scratch2Fusion.py" "/Library/Application Support/Assimilator/Project/LiveLink/Temp/cmd-0.xml"

# Script Copyright:

The "Scratch2Fusion.py" script is based upon Assimilate's "s2nuke_v9.py" script:
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
		lib_path = '/Applications/Blackmagic Fusion 18/Fusion.app/Contents/Libraries/fusionscript.so'
	elif sys.platform.startswith('win'):
		lib_path = 'C:\\Program Files\\Blackmagic Design\\Fusion 18\\fusionscript.dll'
	elif sys.platform.startswith('linux'):
		lib_path = '/opt/BlackmagicDesign/Fusion18/fusionscript.so'

	if not os.path.isfile(lib_path):
		print('[Fusion Studio] [Library Does Not Exist on Disk]', lib_path)

	bmd = imp.load_dynamic('fusionscript', lib_path)
	if bmd:
		sys.modules[__name__] = bmd
	else:
		raise ImportError('[Fusion Studio] Could not locate module dependencies')
	return bmd

def Resolve():
	app = FuScriptLib().scriptapp('Resolve')
	return app

def Fusion():
	app = FuScriptLib().scriptapp('Fusion', 'localhost')
	return app

# Get the Fusion objects
fu = Fusion()
fusion = Fusion()
bmd = FuScriptLib()

# Connect to the current foreground comp
print(fusion)
comp = fu.GetCurrentComp()

def AddNode(clip_dict):
	print(clip_dict)
	# Deselect the nodes
	comp.CurrentFrame.FlowView.Select()
	# Add a Loader node
	ldr = comp.AddTool('Loader', -32768, -32768)
	# Set the Loader node filename
	filename = comp.MapPath(clip_dict['file'])
	ldr.Clip[fu.TIME_UNDEFINED] = filename
	comp.Print(filename + '\n')
	# Set the global frame ranges
	ldr.SetAttrs({'GlobalStart' : clip_dict['in']})
	ldr.SetAttrs({'GlobalEnd' : clip_dict['out']})
	# Set the node tile color
	# The default color for Loader nodes is blue in Fusion (note_color = 0)
	color = {'R': 0.474509803921569, 'G': 0.658823529411765, 'B': 0.815686274509804}
	if clip_dict['note_color'] == None:
		# blue
		color = {'R': 0.474509803921569, 'G': 0.658823529411765, 'B': 0.815686274509804}
	elif clip_dict['note_color'] == '0':
		# yellow
		color = {'R': 0.886274509803922, 'G': 0.662745098039216, 'B': 0.109803921568627}
	elif clip_dict['note_color'] == '1':
		# red
		color = {'R': 0.913725490196078, 'G': 0.549019607843137, 'B': 0.709803921568627}
	elif clip_dict['note_color'] == '2':
		# green
		color = {'R': 0.266666666666667, 'G': 0.56078431372549, 'B': 0.396078431372549}
	elif clip_dict['note_color'] == '3':
		# blue
		color = {'R': 0.474509803921569, 'G': 0.658823529411765, 'B': 0.815686274509804}
	elif clip_dict['note_color'] == '4':
		# purple
		color = {'R': 0.6, 'G': 0.450980392156863, 'B': 0.627450980392157}
	elif clip_dict['note_color'] == '5':
		# orange
		color = {'R': 0.92156862745098, 'G': 0.431372549019608, 'B': 0}
	elif clip_dict['note_color'] == '6':
		# cyan
		color = {'R': 0, 'G': 0.596078431372549, 'B': 0.6}
	elif clip_dict['note_color'] == '7':
		# pink
		color = {'R': 0.913725490196078, 'G': 0.549019607843137, 'B': 0.709803921568627}
	elif clip_dict['note_color'] == '8':
		# black
		color = {'R': 0.549019607843137, 'G': 0.352941176470588, 'B': 0.247058823529412}
	elif clip_dict['note_color'] == '9':
		# white
		color = {'R': 0.725490196078431, 'G': 0.690196078431373, 'B': 0.592156862745098}

	ldr.TileColor = color

	# Set the comment to hold the Scratch note
	ldr.Comments = clip_dict['note']

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
	AddNode(clip_dict)

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

	comp.Print('[Importing Media]\n')
	clips_dict = {}
	for clip in clips:
		ParseClip(clip, clip_NB, clips_dict)

	return xml_infos

def Main():
	print('\n------------------')
	print('Scratch 2 Fusion')
	print('------------------')

	parser = argparse.ArgumentParser(
		description='''Import Assimilate Scratch/LiveFX Construct content into BMD Fusion Studio via an XML importer.'''
	)
	parser.add_argument('xml_path', help='The path to your Scratch xml file')
	args = parser.parse_args()

	xml = args.xml_path
	if xml:
		if comp:
			# Add a new undo history item
			comp.StartUndo('Scratch to Fusion')
	
			# Stop file dialogs from appearing
			comp.Lock()
	
			# Process the XML file
			comp.Print('[XML Document] ' + xml + '\n\n')
			mClipData = XML_Selection(xml)
	
			# Allow file dialogs to appear
			comp.Unlock()
	
			#Close off the undo history item block
			comp.EndUndo(True)
		else:
			print('[Scratch 2 Fusion] Could not connect to the foreground Fusion composite')
	else:
		print('[Scratch 2 Fusion] XML filepath is invalid')
	print('[Done]')

if __name__ == '__main__':
	Main()
