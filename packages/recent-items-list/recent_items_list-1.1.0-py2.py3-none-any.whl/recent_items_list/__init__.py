#  recent_items_list/__init__.py
#
#  Copyright 2024 liyang <liyang@veronica>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
RecentItemsList acts like a list, except that calling the "bump()" method on it
bumps an item to the beginning of the list.
"""

__version__ = "1.1.0"


class RecentItemsList:
	"""
	A list which is ordered by the most recently selected item.
	"""

	maxlen = 10
	on_changed = None

	def __init__(self, items):
		self.items = items

	def bump(self, item):
		"""
		Bump the given item to the beginning of the list.
		If the given item is not in the list, add it to the beginning.
		"""
		old_items = self.items
		self.items = [item]
		self.items.extend( old_item for old_item in old_items if old_item != item )
		if self.maxlen > 0:
			self.items = self.items[:self.maxlen]
		if self.on_changed:
			self.on_changed(self.items)

	def remove(self, item):
		self.items = [old_item for old_item in self.items if old_item != item]
		if self.on_changed:
			self.on_changed(self.items)

	def on_change(self, callback):
		"""
		Registers a callback which is run every time the list changes.
		The callback must have the signature:

			def <function_name>(self, items):

		"""
		if callable(callback):
			self.on_changed = callback
		else:
			raise RuntimeError('Callback is not callable')

	def __iter__(self):
		return self.items.__iter__()

	def __len__(self):
		return self.items.__len__()


#  end recent_items_list/__init__.py
