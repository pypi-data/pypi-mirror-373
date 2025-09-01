# recent_items_list

RecentItemsList acts like a list, except that calling the "bump()" method on it
bumps an item to the beginning of the list.

By default, only the last 10 items are kept in the list. If a new item is
"bumped" to the beginning of a RecentItemsList that already has 10 items, the
item at the end of the list is dropped. You can change this by setting the
"maxlen" property on an instance of RecentItemsList.

When

## Example:

In __init__:

	self._recent_files = RecentItemsList(self.settings.value("recent_files", defaultValue = []))
	self.menuOpen_Recent.aboutToShow.connect(self.fill_recent_files)

### Filling a menu:

	@pyqtSlot()
	def fill_recent_files(self):
		self.menuOpen_Recent.clear()
		actions = []
		for filename in self._recent_files:
			action = QAction(filename, self)
			action.triggered.connect(partial(self.load_file, filename))
			actions.append(action)
		self.menuOpen_Recent.addActions(actions)


### When item is found:

	self._recent_files.bump(filename)

### When item is missing:

	self._recent_files.remove(filename)

### Save to QSettings:

	self.settings.setValue("recent_files", self._recent_files.items)

## Auto-save

Optionally, you provide a callback which will be called whenever the list changes:

	self._recent_files = RecentItemsList(self.settings.value("recent_files", defaultValue = []))
	self._recent_files.on_change(self.save_recent_files)

	def save_recent_files(self, items):
		self.settings.setValue("recent_files", items)

### Another implementation:

	def recent_files():
		global RECENT_FILES
		def sync(items):
			settings().setValue(KEY_RECENT_FILES, items)
		if RECENT_FILES is None:
			RECENT_FILES = RecentItemsList(settings().value(KEY_RECENT_FILES, []))
			RECENT_FILES.on_change(sync)
		return RECENT_FILES

