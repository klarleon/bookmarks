"""
When first run, will present a menu: 
	1. Bookmark currently open file in editor
	2. Open bookmarks list
"""

import ui
import dialogs
import console
import os
import editor
import json
from bookmark import *

class BookmarkItem (object):
	def __init__(self, name='', path=''):
		if path == '':
			pass
		self._name = name
		self._path = path
		
	def open(self, new_tab=True):
		editor.open_file(path, new_tab=new_tab)
		
	def get_name(self):
		return self._name
		
	def get_path(self):
		# returns the relative path of this bookmark
		return self._path

"""
Handles all the bookmark actions.
"""
class BookmarksManager (object):
	def __init__(self, bookmarks=None):
		self.fd = None # file descriptor of saved bookmarks
		self.will_open_new_tab = True
		self._filename = '.bookmarks.json'
		self._homepath = os.path.expanduser('~/Documents/')
		if bookmarks:
			self.bookmarks = bookmarks
		else:
			self.load_file()
		self.tableview = BookmarksTableView(self)
		
	def opens_new_tab(self):
		return self.will_open_new_tab
		
	def load_file(self):
		# If filename exists, load json file
		if os.path.isfile(self._homepath + self._filename):
			# Load content as dictionary and save as self.bookmarks
			try:
				with open(self._homepath + self._filename, 'r') as fd:
					self.bookmarks = json.load(fd)
			except ValueError: # no json data
					self.bookmarks = []
		
	def update_file(self):
		with open(self._homepath + self._filename, 'w') as fd:
			json.dump(self.bookmarks, fd)
			
	def open(self, index):
		path = self.bookmarks[index]['path']
		if self.will_open_new_tab:
			editor.open_file(path, new_tab=True)
		
	def add(self, name='', path=None):
		# Adds a new bookmark as a dictionary item to the self.bookmarks
		# bookmark -- {'name':'Custom Name', 'path':'path/to/item'}
		if path == None:
			pass
		bookmark = {'name': name, 'path': path}
		
		# TODO
		# Check if there is an already existing bookmark with the same path
		
		# Assert that bookmark.path is an existing file or directory
		if not os.path.exists(bookmark['path']):
			dialogs.alert('Invalid Bookmark')
			pass
		
		# Append this bookmark to self.bookmarks
		self.bookmarks.append(bookmark)
		
		# Update save file
		self.update_file()
		
		# Reload the table view
		# self.tableview.reload()
		
		# Show HUD confirmation
		dialogs.hud_alert('Created bookmark for ' + self.get_path(self.count()-1))
		
	def delete(self, index):
		# Delete bookmark
		self.bookmarks.pop(index)
		
	def get_name(self, index):
		# Gets the item in the list at the specific index and returns the displayed bookmark name.
		# If bookmark.name is an empty string, set it to the filename
		name = self.bookmarks[index]['name']
		if name == '':
			name = self.get_path(index).split('/')[-1]
		return name
		
	def get_path(self, index):
		# Returns the path to display
		fullpath = self.bookmarks[index]['path']
		return fullpath.split(self._homepath)[-1]
		
	def set_name(self, index, name):
		# Changes the displayed name of the bookmark at the specified index.
		self.bookmarks[index]['name'] = name
		
	def move(self, old_index, new_index):
		# Moves an item in self.bookmarks from oldIndex to newIndex.
			self.bookmarks.insert(new_index, self.bookmarks.pop(old_index))
		
	def is_file(self, index):
		if os.path.isfile(self.bookmarks[index]['path']):
			return True
		else:
			return False
			
	def is_dir(self, index):
		return not self.is_file(index)
			
	def get_icon(self, index):
		if self.is_file(index):
			return ui.Image.named('iob:document_text_32')
		else:
			return ui.Image.named('iob:folder_32')
		
	def count(self):
		return len(self.bookmarks)
		
	def show_tableview(self):
		self.tableview.show()

	
class BookmarksTableView (ui.View):
	
	def __init__(self, bm_manager=None):
		self.name = 'Bookmarks'
		self.bm_manager = bm_manager
		self.tableview = None
		self.setup()
		
	def setup(self):
		# Create a table with title 'Bookmarks' and present
		self.tableview = self.make_tableview()
		self.will_switch_to_normal_mode()
		
	def make_tableview(self):
		tableview = ui.TableView()
		#self.tableview.name = 'Bookmarks'
		tableview.size_to_fit()
		tableview.frame = self.frame
		tableview.x = tableview.y = 0
		tableview.flex = 'WH'
		#tableview.row_height = 30
		#tableview.background_color = '#DBDBDB'
		tableview.allows_selection = True
		tableview.allows_selection_during_editing = True
		tableview.data_source = self
		tableview.delegate = self
		self.add_subview(tableview)
		return tableview
		
	def will_switch_to_edit_mode(self):
		plus_btn = ui.Image.named('iob:ios7_plus_empty_32')
		self.left_button_items = [ui.ButtonItem(image=plus_btn, action=self.add_button_tapped)]
		self.right_button_items = [ui.ButtonItem('Done', action=self.edit_button_tapped)]
		
	def will_switch_to_normal_mode(self):
		self.left_button_items = []
		self.right_button_items = [ui.ButtonItem('Edit', action=self.edit_button_tapped)]
		
	def will_close(self):
		self.bm_manager.update_file()
		
	@ui.in_background
	def tableview_did_select(self, tableview, section, row):
		# Called when a row was selected.
		if tableview.editing == True: #Edit mode
			name = self.bm_manager.get_name(row)
			input = console.input_alert('Edit Bookmark Name:', '', name)
			if not input == '':
				self.bm_manager.set_name(row, input)
				tableview.reload()
				
		else: #Normal mode
			if self.bm_manager.is_file(row):
				self.bm_manager.open(row)
			self.close()
		
	def tableview_move_row(self, tableview, from_section, from_row, to_section, to_row):
		# Called when the user moves a row with the reordering control (in editing mode).
		self.bm_manager.move(from_row, to_row)
		
	def edit_button_tapped(self, sender):
		if self.tableview.editing:
			self.tableview.set_editing(False)
			self.will_switch_to_normal_mode()
		else:
			self.tableview.set_editing(True)
			self.will_switch_to_edit_mode()
		
	def add_button_tapped(self, sender):
		# Bookmarks a file from the file picker dialog
		if selection == 1:
			path = editor.get_path()
		elif selection == 2:
			# TODO
			# Show file picker dialog
			pass
		self.bm_manager.add(path=path)
		self.reload()
	
	def tableview_cell_for_row(self, tableview, section, row):
		row_title = self.bm_manager.get_name(row)
		row_description = self.bm_manager.get_path(row)
		cell = ui.TableViewCell('subtitle')
		#cell.content_view
		try:
			cell.image_view.image = self.bm_manager.get_icon(row)
		except AttributeError:
			pass
			
		# add cell labels
		cell.text_label.text = row_title
		cell.detail_text_label.text = row_description
		cell.detail_text_label.text_color = '#555'
		cell.accessory_type = 'detail_button'
		return cell
		
	def tableview_accessory_button_tapped(self, sender):
		# called when the information button for a ta is tapped
		#console.input_alert(title='Title', message=self.bm_manager.)
		pass
		
	def tableview_number_of_rows(self, tableview, section):
		return self.bm_manager.count()
		
	def tableview_can_delete(self, tableview, section, row):
		# Return True if the user should be able to delete the given row.
		return True

	def tableview_can_move(self, tableview, section, row):
		# Return True if a reordering control should be shown for the given row (in editing mode).
		return True

	def tableview_delete(self, tableview, section, row):
		# Called when the user confirms deletion of the given row.
		#self.deletesnippet(self.snippets[row][0])
		#self.snippets.pop(row)
		self.bm_manager.delete(row)
		tableview.delete_rows([row])
		
	def show(self):
		self.present('fullscreen')
		
	def reload(self):
		self.tableview.reload()
		
		
def main():
	# TODO Load any settings first
	bm = BookmarksManager()
	selection = dialogs.alert(title='Select Action', button1='Add bookmark', button2='Open')
	if selection == 1:
		bm.add(path=editor.get_path())
	elif selection == 2:
		bm.show_tableview()
	return bm


if __name__ == '__main__':
	bm = main()
