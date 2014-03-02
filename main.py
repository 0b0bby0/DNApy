#!/usr/bin/python


#DNApy is a DNA editor written purely in python. 
#The program is intended to be an intuitive, fully featured, 
#extendable, editor for molecular and synthetic biology.  
#Enjoy!
#
#copyright (C) 2014  Martin Engqvist | 
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#LICENSE:
#
#DNApy is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 3 of the License, or
#(at your option) any later version.
# 
#DNApy is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Library General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software Foundation,
#Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#Get source code at: https://github.com/0b0bby0/DNApy
#
from copy import deepcopy
from string import *
from os import access,listdir
import sys, os
import wx
import wx.richtext as rt

from wxPython.lib.buttons import *
from wxPython.lib.colourselect import *

import pyperclip


import dna
import genbank

#GUI components
import dnaeditor
import features
import genbankfileview


#TODO
#grey out things until a new file is made or one is opened
#open new window for new files
#test which functions are broken
#add vector view
#add pretty dna view
#improve the feature editor (especially the "location" field)
#make rightklick menus


files={}   #dictionary with all configuration files

files['default_dir'] = os.path.abspath(os.path.dirname(sys.argv[0]))+"/"
files['default_dir']=replace(files['default_dir'], "\\", "/")
files['default_dir']=replace(files['default_dir'], "library.zip", "")

variables=files['default_dir']+"variables"   ##path to the file of the global variables
settings=files['default_dir']+"settings"   ##path to the file of the global settings
execfile(variables) #gets all the pre-assigned variables
execfile(settings) #gets all the pre-assigned settings




class MyFrame(wx.Frame):
	tab_list=[] #list of tabs 
	current_tab=0 #contains the current tab
	panel=[] #list of panels for the textbox

	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title, size=windowsize) #size of program
		ID=wx.NewId()
		self.DNApy = wx.Notebook(self, ID, style=0) ######create blank notebook
		wx.EVT_NOTEBOOK_PAGE_CHANGED(self, ID, self.page_change)



		self.generate_dnaview_tab("")
		self.generate_featureview_tab("")
		self.generate_vectorview_tab("")
		self.generate_sequencingview_tab('')
		self.generate_genbankview_tab("")
		
		#create toolbars
		self.__generate_toolbar()
		self.__generate_searchandmutate_toolbar()
		
		
		#create Menu Bar
		self.create_menu()

		#create statusbar
		self.statusbar = self.CreateStatusBar(2)
		self.statusbar.SetStatusStyles(styles=[wx.SB_FLAT, wx.SB_FLAT])

		self.do_layout()
		self.Centre()
	def OnKeyPress(self, evt):
		print('keypress')

	def do_layout(self):
		'''Pack toolbar and the tabs in their sizers'''
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.frame_1_toolbar, 0, wx.EXPAND)
		#if second toolbar is present, add that too.
		try:
			sizer.Add(self.frame_2_toolbar, 0, wx.EXPAND)
		except:
			pass
		sizer.Add(self.DNApy, -1, wx.EXPAND)
		self.SetSizer(sizer)	
		
			

##### Generate tabs and define content #####

	def generate_dnaview_tab(self, evt):
		number=len(self.tab_list)

		self.panel.append(wx.Panel(self.DNApy, -1))

		self.dnaview = dnaeditor.MyPanel(self.panel[number])
	
		self.tab_list.append(self.dnaview)


		sizer_1=wx.BoxSizer(wx.HORIZONTAL)
		sizer_1.Add(self.tab_list[number], 1, wx.EXPAND, 0)
		self.DNApy.AddPage(self.panel[number], "DNA")
		self.panel[number].SetSizer(sizer_1)

		

	def generate_featureview_tab(self, evt):
		number=len(self.tab_list)

		self.panel.append(wx.Panel(self.DNApy, -1))

		self.featureview = features.FeatureCreate(self.panel[number], id=wx.ID_ANY, editor=True)
	
		self.tab_list.append(self.featureview)


		sizer_1=wx.BoxSizer(wx.HORIZONTAL)
		sizer_1.Add(self.tab_list[number], 1, wx.EXPAND, 0)
		self.DNApy.AddPage(self.panel[number], "Features")
		self.panel[number].SetSizer(sizer_1)


	def generate_vectorview_tab(self, evt):
		pass

	def generate_sequencingview_tab(self, evt):
		pass

	def generate_genbankview_tab(self, evt):
		number=len(self.tab_list)

		self.panel.append(wx.Panel(self.DNApy, -1))
		self.genbankview = genbankfileview.MyPanel(self.panel[number], style=wx.VSCROLL|wx.HSCROLL)
		self.genbankview.SetEditable(False)

		self.tab_list.append(self.genbankview)


		sizer_1=wx.BoxSizer(wx.HORIZONTAL)
		sizer_1.Add(self.tab_list[number], 1, wx.EXPAND, 0)
		self.DNApy.AddPage(self.panel[number], "GenBank")
		self.panel[number].SetSizer(sizer_1)

################ file functions #################

	def new_file(self, evt):
		'''Create new gb file'''
		gb = genbank.new_file() #make new gb in panel	
		self.dnaview.gbviewer.SetValue(genbank.gb.get_dna())
		self.SetTitle('NewFile - DNApy')
		self.page_change("")

		self.frame_1_toolbar.EnableTool(502, 1)
		self.frame_1_toolbar.EnableTool(503, 1)
		self.frame_1_toolbar.EnableTool(504, 1)
		self.frame_1_toolbar.EnableTool(505, 1)
		self.frame_1_toolbar.EnableTool(506, 1)
		self.frame_1_toolbar.EnableTool(511, 1)
		self.frame_1_toolbar.EnableTool(512, 1)
		self.Bind(wx.EVT_UPDATE_UI, self.update_statusbar)


	def open_file(self, evt):
		'''Function for opening file'''
		self.dir_to_open = default_filepath
		dlg = wx.FileDialog( self, style=wx.OPEN|wx.FILE_MUST_EXIST,   defaultDir=self.dir_to_open ,wildcard='GenBank files (*.gb)|*|Any file (*)|*')
		dlg.ShowModal()
		fileName = dlg.GetFilename()
		all_path=dlg.GetPath()
		dire=dlg.GetDirectory()
		dlg.Destroy()
		if(fileName == None or fileName == "" ):
			return1
		
		name, extension = fileName.split('.')
		if extension == 'gb':
			gb = genbank.open_file(all_path) #make a genbank object and read file
			self.dnaview.gbviewer.SetValue(genbank.gb.get_dna())
			self.SetTitle(fileName+' - DNApy')
			if genbank.gb.clutter == True: #if tags from ApE or Vector NTI is found in file
				dlg = wx.MessageDialog(self, style=wx.YES_NO|wx.CANCEL, message='This file contains tags from the Vector NTI or ApE programs. Keeping these tags may break compatibility with other software. Removing them will clean up the file, but may result in the loss of some personalized styling options when this file is viewed in Vector NTI or ApE. Do you wish to REMOVE these tags?')
				result = dlg.ShowModal()
				dlg.Destroy()
				if result == wx.ID_YES: #if yes, remove clutter
					genbank.gb.clean_clutter()
			self.page_change("")

			self.frame_1_toolbar.EnableTool(502, 1)
			self.frame_1_toolbar.EnableTool(503, 1)
			self.frame_1_toolbar.EnableTool(504, 1)
			self.frame_1_toolbar.EnableTool(505, 1)
			self.frame_1_toolbar.EnableTool(506, 1)
			self.frame_1_toolbar.EnableTool(511, 1)
			self.frame_1_toolbar.EnableTool(512, 1)

		else:
			print("error, not a gb file")		

		self.Bind(wx.EVT_UPDATE_UI, self.update_statusbar)
#		wx.EVT_CLOSE(self, self.OnCloseWindow)
		
#		wx.EVT_KEY_DOWN(self, self.OnKeyPress)

	
	
	def save_file(self, evt):
		'''Function for saving file'''
#		try:


		genbank.gb.write_file(genbank.gb.get_filepath())
		

#		except:
#			self.save_as_file("")
		

	def save_as_file(self, evt):
		'''Function for saving file as'''
		filepath = genbank.gb.get_filepath()
		print(filepath)	
		for i in range(len(filepath)): #get directory for file
			if filepath[i] == '/':
				dire = filepath[0:i+1]
		#get save dialog
		dlg = wx.FileDialog( self, style=wx.SAVE | wx.OVERWRITE_PROMPT,defaultDir=dire,wildcard='TXT files (*)|*|Any file (*)|*')
		dlg.ShowModal()
		all_path=dlg.GetPath()
		fileName=dlg.GetFilename()
		dire=dlg.GetDirectory()
		dlg.Destroy()
		if (fileName == None or fileName == ""):
			return
		else:
			#try:
			genbank.gb.set_filepath(all_path)
			self.save_file("")
			#except:
			#	error_window(7, self)


	def quit(self, evt):
		'''Function for quiting program'''
		print("close")
#    		self.close_all("")
       		self.Close()
       		#self.Destroy()		


	def OnCloseWindow(self, evt):
		'''not currently used'''
#		self.close_all("")
#		foo=self.GetSize()  ###except for the window size of file 
#		if(self.IsMaximized()==0):
#			file=open(files['size'], "w")
#			file.write(str(foo[0])+"\n"+str(foo[1]))
#			file.close()
		self.Close()
		#self.Destroy()


##########################################################


	def page_change(self, ev):
		'''When changing between tabs'''
		self.Refresh()
		self.current_tab=self.DNApy.GetSelection()
#		self.tab_list[self.current_tab].SetFocus()   #to restore the pointer
		try:
			self.tab_list[self.current_tab].updateUI()
		except:
			pass

	def update_statusbar(self, evt):
		'''Updates statusbar'''
		#this stuff is for the statusbar
#		if len(self.tab_list) == 0:
#			string = 'File unmodified'
#		elif self.tab_list[self.current_tab].modify==0:
#			string = 'File unmodified'
#		elif self.tab_list[self.current_tab].modify==1:
#			string = 'File not yet saved'
		self.current_tab=self.DNApy.GetSelection()
		if self.current_tab == 0: #if dna editor is active
			
			mposition, Feature = self.dnaview.mouse_position("") #get mouse position
		
		
			try:
				Position = str(mposition+1)
			except:
				Position = ""
		
			try:
				Feature = str(Feature)
			except:
				Feature = ""
		
			try:		
				SelectionFrom, SelectionTo = (str(self.dnaview.gbviewer.GetSelection()[0]+1), str(self.dnaview.gbviewer.GetSelection()[1]))
				if SelectionFrom == '-1' and SelectionTo == '-2': #no selection if true
					SelectionFrom, SelectionTo = ("0", "0")
			except:
				SelectionFrom, SelectionTo = ("0", "0")
			try:	
				Length = str(self.dnaview.gbviewer.GetSelection()[1] - self.dnaview.gbviewer.GetSelection()[0])
			except:
				Length = ""


			self.SetStatusText('Position: %s      Feature: %s' % (Position, Feature), 0) #text in first field
		
			if float(Length)/3 == 1: #if one triplet is selected, show the AA
				AA = ': %s' % dna.translate(self.dnaview.gbviewer.GetStringSelection())
			else:
				AA = ''
			
			self.SetStatusText('Selection: %s to %s,   %s bp,   %.1f AA%s' % (SelectionFrom, SelectionTo, Length, float(Length)/3, AA), 1) #text in second field

		else:
			self.SetStatusText('', 0)
			self.SetStatusText('', 1)		


##########################################

	def make_outputpopup(self):
		'''Creates a popup window in which output can be printed'''
		self.outputframe = wx.Frame(None, title="Output Panel") # creation of a Frame with a title
		self.output = output.create(self.outputframe, style=wx.VSCROLL|wx.HSCROLL) # creation of a richtextctrl in the frame
		

############## Info methods

	def info(self, event):
		string = '''
This file is part of DNApy. DNApy is a DNA editor written purely in python. 
The program is intended to be an intuitive, fully featured, 
extendable, editor for molecular and synthetic biology.  
Enjoy!

copyright (C) 2014  Martin Engqvist | 

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
LICENSE:
This file is part of DNApy.
DNApy is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
 
DNApy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Library General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get source code at: https://github.com/0b0bby0/DNApy

'''
		self.make_outputpopup()		
		self.output.write(string+'\n', 'Text')
		self.outputframe.Show()
		
	def IUPAC_codes(self, event):
		'''Prints info about the IUPAC codes for DNA and amino acids'''
		string = '''
Nucleotide code 	Base
A 				Adenine
C 				Cytosine
G 				Guanine
T (or U) 			Thymine (or Uracil)
R 				A or G
Y 				C or T
S 				G or C
W 				A or T
K 				G or T
M 				A or C
B 				C or G or T
D 				A or G or T
H 				A or C or T
V 				A or C or G
N 				any base
. or - 				gap

Amino acid 	Three letter 	Amino acid
A 			Ala 			Alanine
C 			Cys 			Cysteine
D 			Asp 			Aspartic Acid
E 			Glu 			Glutamic Acid
F 			Phe 			Phenylalanine
G 			Gly 			Glycine
H 			His 			Histidine
I 			Ile 			Isoleucine
K 			Lys 			Lysine
L 			Leu 			Leucine
M 			Met 			Methionine
N 			Asn 			Asparagine
P 			Pro 			Proline
Q 			Gln 			Glutamine
R 			Arg 			Arginine
S 			Ser 			Serine
T 			Thr 			Threonine
V 			Val 			Valine
W 			Trp 			Tryptophan
Y 			Tyr 			Tyrosine
'''

		self.make_outputpopup()		
		self.output.write(string+'\n', 'Text')
		self.outputframe.Show()


	
	def codon_table(self, event):
		'''Prints the standard codon table for translating DNA to protein'''
		string = '''
Put Table here
'''
		self.make_outputpopup()	
		self.output.write(string+'\n', 'Text')
		self.outputframe.Show()
 



################ genbank methods ###############
	def OnKeyPress(self, evt):
		'''Checks which key is pressed and if one of them is A, T, C or G inserts the base into the file'''
		#this is not working
		print('ok')
		print(evt)

		keycode = event.GetUnicodeKey()
#		if keycode == :
#			insert...
	
		evt.Skip()

	def match_selection(self):
		'''Checks whether the dnaview selection matches that stored in the selection variable in genbank and if not, updates it'''
		print('match selection')
		viewerstart, viewerend = self.dnaview.gbviewer.GetSelection()
		if viewerstart == -2 and viewerend == -2: # if not a selection
			viewerstart = self.dnaview.gbviewer.GetInsertionPoint()
			viewerend = viewerstart
		gbstart, gbend = genbank.gb.get_dna_selection()
		if viewerstart != gbstart or viewerend != gbend:
			selection = (viewerstart, viewerend)
			genbank.gb.set_dna_selection(selection)
			#print(selection)

	def update_viewer(self):
		'''Accessory function for realizing changes to DNA'''
		self.dnaview.gbviewer.SetValue(genbank.gb.get_dna())
		self.dnaview.updateUI()
		start, finish = genbank.gb.get_dna_selection()
		print(start, finish)
		print(self.dnaview.gbviewer.SetSelection(start, finish))
		if start != finish: self.dnaview.gbviewer.SetSelection(start, finish)
		elif start == finish: self.dnaview.gbviewer.SetInsertionPoint(start)
		self.dnaview.gbviewer.ShowPosition(start) 

	def select_all(self, evt):
		pass

	def uppercase(self, evt):
		'''Change selection to uppercase'''
		self.match_selection()
		genbank.gb.uppercase()
		self.update_viewer()
		
	def lowercase(self, evt):
		'''Change selection to lowercase'''
		self.match_selection()
		genbank.gb.lowercase()
		self.update_viewer() 

	def reverse_complement_selection(self, evt):
		'''Reverse-complement current selection'''
		self.match_selection()
		genbank.gb.reverse_complement_selection()
		self.update_viewer()

	def delete(self):
		'''Deletes a selection and updates dna and features'''
		self.match_selection()
		genbank.gb.delete()
		self.update_viewer()

	def cut(self, evt):
		'''Cut DNA and store it in clipboard together with any features present on that DNA'''
		self.match_selection()
		genbank.gb.cut()
		self.update_viewer()
		#need to add logic to make sure the correct panel is selected
			
	def cut_reverse_complement(self, evt):
		'''Cut reverse complement of DNA and store it in clipboard together with any features present on that DNA'''
		self.match_selection()
		genbank.gb.cut_reverse_complement()
		self.update_viewer()
		#need to add logic to make sure the correct panel is selected
		
	def paste(self, evt):
		'''Paste DNA and any features present on that DNA'''
		control = wx.Window.FindFocus() #which field is selected?

		if control == self.searchinput: #the searchbox
			control.SetValue(pyperclip.paste())

		elif control == self.dnaview.gbviewer: #the main dna window
			self.match_selection()
			genbank.gb.paste()
			self.update_viewer() # need to fix so that pasted dna is still highlighted
		
	def paste_reverse_complement(self, evt):
		'''Paste reverse complement of DNA and any features present on that DNA'''
		self.match_selection()
		genbank.gb.paste_reverse_complement()
		self.update_viewer()
		#need to add logic to make sure the correct panel is selected

	def copy(self, evt):
		'''Copy DNA and features into clipboard'''
		control = wx.Window.FindFocus() #which field is selected?

		if control == self.searchinput: #the searchbox
			start, finish = self.searchinput.GetSelection()
			if start != -2 and finish != -2: #must be a selection
				pyperclip.copy(self.searchinput.GetValue()[start:finish])

		elif control == self.dnaview.gbviewer: #the main dna window	
			self.match_selection()
			genbank.gb.copy()

	def copy_reverse_complement(self, evt):
		'''Copy reverse complement of DNA'''
		self.match_selection()
		genbank.gb.copy_reverse_complement()
		#need to add logic to make sure the correct panel is selected

	def Undo(self, evt):
		pass
		#I should store each genbank file as a deep copy in a list, that way I can get them back by undoing/redoing

	def Redo(self, evt):
		pass


######################################

	def list_features(self, evt):
		'''List all features in output panel'''
		self.make_outputpopup()
#		tabtext = str(self.gbviewer.GetPageText(self.gbviewer.GetSelection()))
		tabtext = 'Replace!'
		self.output.write('%s | List features\n' % tabtext, 'File')
		featurelist = genbank.gb.list_features()
		self.output.write(featurelist, 'Text')
		self.outputframe.Show()


######### Toolbar and Menu ############

	def __generate_toolbar(self):
		'''For generating toolbar with buttons'''
				
		self.frame_1_toolbar = wx.ToolBar(self, wx.ID_ANY, style=wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_DOCKABLE)

   		#syntax for toolbar
   		#AddLabelTool(self, id, label, bitmap, bmpDisabled, kind, shortHelp, longHelp, clientData) 
   		

   		
   		#New Document
   		self.frame_1_toolbar.AddLabelTool(500, "New Document", wx.Bitmap(files['default_dir']+"/icon/new.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'New File', "New File") #last one is the one displayed in status bar
   		wx.EVT_TOOL(self, 500, self.new_file)
		#Open File
   		self.frame_1_toolbar.AddLabelTool(501, "Open File", wx.Bitmap(files['default_dir']+"/icon/open.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Load File', 'Load File')
   		wx.EVT_TOOL(self, 501, self.open_file)
		#Save current file
   		self.frame_1_toolbar.AddLabelTool(502, "Save current file", wx.Bitmap(files['default_dir']+"/icon/save.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Save File', 'Save File')
   		wx.EVT_TOOL(self, 502, self.save_file)
		#Save as
   		self.frame_1_toolbar.AddLabelTool(503, "Save as", wx.Bitmap(files['default_dir']+"/icon/saveas.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Save File As', 'Save File As')
   		wx.EVT_TOOL(self, 503, self.save_as_file)
		#cut
   		self.frame_1_toolbar.AddLabelTool(504, "cut", wx.Bitmap(files['default_dir']+"/icon/cut.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'cut', 'cut')
   		wx.EVT_TOOL(self, 504, self.cut)
		#copy
   		self.frame_1_toolbar.AddLabelTool(505, "copy", wx.Bitmap(files['default_dir']+"/icon/copy.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'copy', 'copy')
   		wx.EVT_TOOL(self, 505, self.copy)
		#paste
   		self.frame_1_toolbar.AddLabelTool(506, "paste", wx.Bitmap(files['default_dir']+"/icon/paste.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'paste', 'paste')
   		wx.EVT_TOOL(self, 506, self.paste)
   		#Undo
   		self.frame_1_toolbar.AddLabelTool(513, "Undo", wx.Bitmap(files['default_dir']+"/icon/undo.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Undo', 'Undo')
   		wx.EVT_TOOL(self, 513, self.Undo)   
   		#Redo
   		self.frame_1_toolbar.AddLabelTool(514, "Redo", wx.Bitmap(files['default_dir']+"/icon/redo.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Redo', 'Redo')
   		wx.EVT_TOOL(self, 514, self.Redo) 
		#Print current window
#   		self.frame_1_toolbar.AddLabelTool(510, "Print current window", wx.Bitmap(files['default_dir']+"/icon/print.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Print Current Window', 'Print Current Window')
 #  		wx.EVT_TOOL(self, 510, self.print_setup)
   		self.frame_1_toolbar.AddCheckTool(511, wx.Bitmap(files['default_dir']+"/icon/search.png", wx.BITMAP_TYPE_ANY), wx.Bitmap(files['default_dir']+"/icon/search.png", wx.BITMAP_TYPE_ANY), 'Find', 'Find')
   		wx.EVT_TOOL(self, 511, self.toggle_searchandmutate_toolbar)

   		self.frame_1_toolbar.AddCheckTool(512, wx.Bitmap(files['default_dir']+"/icon/mutate.png", wx.BITMAP_TYPE_ANY), wx.Bitmap(files['default_dir']+"/icon/search.png", wx.BITMAP_TYPE_ANY), 'Mutate', 'Mutate')
   		wx.EVT_TOOL(self, 512, self.toggle_searchandmutate_toolbar)

		
		self.frame_1_toolbar.Realize()
		
		self.frame_1_toolbar.EnableTool(502, 0)
		self.frame_1_toolbar.EnableTool(503, 0)
		self.frame_1_toolbar.EnableTool(504, 0)
		self.frame_1_toolbar.EnableTool(505, 0)
		self.frame_1_toolbar.EnableTool(506, 0)
		self.frame_1_toolbar.EnableTool(513, 0)
		self.frame_1_toolbar.EnableTool(514, 0)
		self.frame_1_toolbar.EnableTool(511, 0)
		self.frame_1_toolbar.EnableTool(512, 0)

	def __generate_searchandmutate_toolbar(self):
		##### Toolbar 2 #####
		self.nucleotideoraminoacidSelection = 0

		self.frame_2_toolbar = wx.ToolBar(self, wx.ID_ANY, style=wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_DOCKABLE)
		
		self.findormutSelection = 'Find'
		self.add_search_tools(self.findormutSelection)
			

		self.frame_2_toolbar.Realize()
		self.frame_2_toolbar.Hide()


	def add_search_tools(self, typeof):
		'''Adds tools to the find/mutate toolbar. A string "find" or "mutate" is passed to determine which tollbar to build'''
	
		#nucleotide or amino acid
		if typeof == 'Find':
			self.nucleotideoraminoacid = wx.ComboBox(self.frame_2_toolbar, id=601, size=(120, 28), choices=['Nucleotide', 'Amino Acid', 'Position', 'Feature'], style=wx.CB_READONLY)
		elif typeof == 'Mutate':
			self.nucleotideoraminoacid = wx.ComboBox(self.frame_2_toolbar, id=601, size=(120, 28), choices=['Nucleotide', 'Amino Acid'], style=wx.CB_READONLY)
		self.frame_2_toolbar.AddControl(self.nucleotideoraminoacid)
		self.nucleotideoraminoacid.SetSelection(self.nucleotideoraminoacidSelection)
		wx.EVT_COMBOBOX(self, 601, self.OnChangeSearchParams)

		#'input'
		self.searchinput=wx.TextCtrl(self.frame_2_toolbar, id=wx.ID_ANY, size=(100, 28), value="")
		self.frame_2_toolbar.AddControl(self.searchinput)
	
		if typeof == 'Mutate':
			self.tobox=wx.TextCtrl(self.frame_2_toolbar, id=wx.ID_ANY, size=(25, 28), value="to")
			self.frame_2_toolbar.AddControl(self.tobox)
			self.mutateto=wx.TextCtrl(self.frame_2_toolbar, id=wx.ID_ANY, size=(100, 28), value="")
			self.frame_2_toolbar.AddControl(self.mutateto)

		#'in'
		nucleotideoraa = self.nucleotideoraminoacid.GetValue()
		if nucleotideoraa == 'Nucleotide' or nucleotideoraa == 'Amino Acid':
			self.inbox=wx.TextCtrl(self.frame_2_toolbar, id=wx.ID_ANY, size=(25, 28), value="in")
			self.frame_2_toolbar.AddControl(self.inbox)
			self.inbox.SetEditable(False)
			
		#featurebox
		if nucleotideoraa == 'Nucleotide' or nucleotideoraa == 'Amino Acid':
			try:
				#get features...
				self.featurebox = wx.ComboBox(self.frame_2_toolbar, id=603, size=(120, 28), choices=['Molecule' and features], style=wx.CB_READONLY)
			except:
				self.featurebox = wx.ComboBox(self.frame_2_toolbar, id=603, size=(120, 28), choices=['Molecule'], style=wx.CB_READONLY)
			self.frame_2_toolbar.AddControl(self.featurebox)
			wx.EVT_COMBOBOX(self, 603, self.placeholder)
			self.featurebox.SetSelection(0)
		
		#'go'
		if typeof == 'Find':
			#find previous
	   		self.frame_2_toolbar.AddLabelTool(507, "Find previous", wx.Bitmap(files['default_dir']+"/icon/up.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Find previous', 'Find previous')
	   		wx.EVT_TOOL(self, 507, self.find_previous)
			#find next
	   		self.frame_2_toolbar.AddLabelTool(509, "Find next", wx.Bitmap(files['default_dir']+"/icon/down.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Find next', 'Find next')
	   		wx.EVT_TOOL(self, 509, self.find_next)
			#search glass
	   		self.frame_2_toolbar.AddLabelTool(604, "Find", wx.Bitmap(files['default_dir']+"/icon/search.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Find', 'Find')
	   		wx.EVT_TOOL(self, 604, self.find)
		elif typeof == 'Mutate':
			self.frame_2_toolbar.AddLabelTool(604, "Mutate", wx.Bitmap(files['default_dir']+"/icon/up.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, 'Mutate', 'Mutate')
	   		wx.EVT_TOOL(self, 604, self.find)

	def find(self, evt):
		'''Find nucleotide in molecule'''
		self.nucleotideoraminoacid.GetValue()
		self.featurebox.GetValue()
		searchstring = self.searchinput.GetValue()
		genbank.gb.find_dna(searchstring)
		try:
			self.tab_list[self.current_tab].updateUI()
		except:
			pass

		start, finish = genbank.gb.get_dna_selection()
		self.dnaview.gbviewer.SetSelection(start, finish)
		self.dnaview.gbviewer.ShowPosition(start) 
	
	def find_previous(self, evt):
		'''Select prevous search hit'''
		genbank.gb.find_previous()
		start, finish = genbank.gb.get_dna_selection()
		self.dnaview.gbviewer.SetSelection(start, finish)
		self.dnaview.gbviewer.ShowPosition(start) 

	def find_next(self, evt):
		'''Select next search hit'''
		genbank.gb.find_next()
		start, finish = genbank.gb.get_dna_selection()
		self.dnaview.gbviewer.SetSelection(start, finish)
		self.dnaview.gbviewer.ShowPosition(start) 

	def mutate(self, evt):
		pass

	def placeholder(self, evt):
		pass

	def OnChangeSearchParams(self, evt):
		'''When changes are made to options in the searchbar, update which downstream options are available'''
		#get selection for find or mutate
		if evt.GetId() == 601:
			self.nucleotideoraminoacidSelection = self.nucleotideoraminoacid.GetSelection()

		self.frame_2_toolbar.ClearTools()
		self.add_search_tools(self.findormutSelection)


	def toggle_searchandmutate_toolbar(self, evt):
		'''Toggles the visibility of the search toolbar'''
		if self.frame_1_toolbar.GetToolState(511) == True and self.frame_1_toolbar.GetToolState(512) == False:
			self.frame_2_toolbar.Show()
			self.frame_1_toolbar.EnableTool(512, 0)
			self.frame_2_toolbar.ClearTools()
			self.findormutSelection = 'Find'
			self.add_search_tools(self.findormutSelection)

		elif self.frame_1_toolbar.GetToolState(511) == False and self.frame_1_toolbar.GetToolState(512) == True:
			self.frame_2_toolbar.Show()
			self.frame_1_toolbar.EnableTool(511, 0)
			self.frame_2_toolbar.ClearTools()
			self.findormutSelection = 'Mutate'
			self.add_search_tools(self.findormutSelection)

		elif self.frame_1_toolbar.GetToolState(511) == False and self.frame_1_toolbar.GetToolState(512) == False:
			self.frame_1_toolbar.EnableTool(511, 1)
			self.frame_1_toolbar.EnableTool(512, 1)
			self.frame_2_toolbar.Hide()

		self.Layout()


	def create_menu(self):     #method for creating menu
		self.menubar = wx.MenuBar()
		fileitem = wx.Menu()
			
		#new document
		fileitem.Append(1, "New\tCtrl+Q", "New File")
		wx.EVT_MENU(self, 1, self.new_file)

		#open document
		fileitem.Append(2, "Open\tCtrl+O", "Open File")
		wx.EVT_MENU(self, 2, self.open_file)
		fileitem.AppendSeparator()

		#save document
		fileitem.Append(3, "Save\tCtrl+S", "Save current file")
		wx.EVT_MENU(self, 3, self.save_file)

		#save document as
		fileitem.Append(4, "Save as", "Save a copy of current file")
		wx.EVT_MENU(self, 4, self.save_as_file)

		#save all
#		fileitem.Append(5, "Save all", "Save all open tabs")
#		wx.EVT_MENU(self, 5, self.save_all)
#		fileitem.AppendSeparator()

		#close single
#		fileitem.Append(5, "Close", "Close current file")
#		wx.EVT_MENU(self, 5, self.dnaview.close_file)

		#close all
#		fileitem.Append(6, "Close all", "Close all tabs")
#		wx.EVT_MENU(self, 6, self.dnaview.close_all)
#		fileitem.AppendSeparator()

		#quit
		fileitem.Append(7, "Quit", "Quit program")
		wx.EVT_MENU(self, 7, self.quit)

		self.menubar.Append(fileitem, "&File")

		######################### For 'Edit DNA' menu item #############################################
		self.edit = wx.Menu()
		#undo
		self.edit.Append(9, "Undo\tCtrl+Z", "Undo")
		wx.EVT_MENU(self, 9, self.Undo)

		#redo
		self.edit.Append(10, "Redo\tCtrl+Y", "Redo")
		wx.EVT_MENU(self, 10, self.Redo)
		self.edit.AppendSeparator() #________________________devider

		#cut
		self.edit.Append(11, "cut\tCtrl+X", "cut selected DNA")
		wx.EVT_MENU(self,11, self.cut)

		#copy
		self.edit.Append(12, "copy\tCtrl+C", "copy selected DNA")
		wx.EVT_MENU(self, 12, self.copy)

		#paste
		self.edit.Append(13, "paste\tCtrl+V", "paste DNA")
		wx.EVT_MENU(self, 13, self.paste)
		
		#cut reverse complement
		self.edit.Append(111, "cut Rev-Comp\tCtrl+Shift+X", "cut reverse-complement of selected DNA")
		wx.EVT_MENU(self,111, self.cut_reverse_complement)

		#copy reverse complement
		self.edit.Append(121, "copy Rev-Comp\tCtrl+Shift+C", "copy reverse-complement of selected DNA")
		wx.EVT_MENU(self, 121, self.copy_reverse_complement)		
		
		#paste reverse complement
		self.edit.Append(131, "paste Rev-Comp\tCtrl+Shift+V", "paste reverse-complement of DNA")
		wx.EVT_MENU(self, 131, self.paste_reverse_complement)

		#reverse-complement selection
		self.edit.Append(141, "Rev-Comp selection\tCtrl+R", "Reverse-complement seleected DNA")
		wx.EVT_MENU(self,141, self.reverse_complement_selection)
		self.edit.AppendSeparator() #________________________devider
		
		#select all
		self.edit.Append(14, "Select all", "Select all text")
		wx.EVT_MENU(self, 14, self.select_all)
		self.edit.AppendSeparator() #________________________devider

		#uppercase
		self.edit.Append(34, "uppercase\tCtrl+W", "Convert selected text to uppercase")
		wx.EVT_MENU(self, 34, self.uppercase)

		#lowercase
		self.edit.Append(35, "lowercase\tCtrl+E", "Convert selected text to lowercase")
		wx.EVT_MENU(self, 35, self.lowercase)
		self.edit.AppendSeparator() #________________________devider

		self.menubar.Append(self.edit, "Edit DNA")
		
	
	
		######## Features menu item ########
		self.features = wx.Menu()
		
		self.features.Append(40, "List Features", "List all features in file")
		wx.EVT_MENU(self,40, self.list_features)
		
#		self.features.Append(41, "Edit Features", "Edit features in file")
#		wx.EVT_MENU(self,41, self.edit_features)		
		
		self.menubar.Append(self.features, "Features")
		


		######## Protein menu item #########
		self.protein = wx.Menu()
		
		#translate
		self.protein.Append(30, "Translate\tCtrl+T", "Translate DNA to protein")
		wx.EVT_MENU(self,30, self.dnaview.translate_selection)

		#translate reverse complement
		self.protein.Append(31, "Translate Rev-Comp\tCtrl+Shift+T", "Translate DNA to protein")
		wx.EVT_MENU(self,31, self.dnaview.translate_selection_reverse_complement)

		#translate feature
		self.protein.Append(32, "Translate feature", "Translate DNA feature to protein")
		wx.EVT_MENU(self,32, self.dnaview.translate_feature)

		self.menubar.Append(self.protein, "Protein")



		########## For 'Help' menu item #############
		self.help = wx.Menu()
		#about program
		self.help.Append(21, "About", "About this program")
		wx.EVT_MENU(self, 21, self.info)

		#print IUPAC codes for dna and AA
		self.help.Append(22, "IUPAC codes", "IUPAC codes of DNA and amino acids")
		wx.EVT_MENU(self, 22, self.IUPAC_codes)


		self.menubar.Append(self.help, "Help")

		self.SetMenuBar(self.menubar)










##### main loop
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "DNApy")
        frame.Show(True)
        self.SetTopWindow(frame)
        return True
        
if __name__ == '__main__': #if script is run by itself and not loaded	
	app = MyApp(0)
	app.MainLoop()
