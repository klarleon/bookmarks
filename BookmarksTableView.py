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
			title = self.bm_manager.get_title(row)
			input = console.input_alert('Edit Bookmark Name:', '', title)
			if not input == '':
				self.bm_manager.set_title(row, input)
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
		row_title = self.bm_manager.get_title(row)
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
		
