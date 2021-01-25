import sqlite3

from core.webui.model.Widget import Widget
from core.webui.model.WidgetSizes import WidgetSizes


class Player(Widget):

	DEFAULT_SIZE = WidgetSizes.w
	DEFAULT_OPTIONS: dict = dict('deviceUid')

	def __init__(self, data: sqlite3.Row):
		super().__init__(data)
