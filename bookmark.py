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

	
def main():
	# TODO Load any settings first
	bm = BookmarksManager()
	selection = dialogs.alert(name='Select Action', button1='Add bookmark', button2='Open')
	if selection == 1:
		bm.add(path=editor.get_path())
	elif selection == 2:
		bm.show_tableview()
	return bm


if __name__ == '__main__':
	bm = main()
