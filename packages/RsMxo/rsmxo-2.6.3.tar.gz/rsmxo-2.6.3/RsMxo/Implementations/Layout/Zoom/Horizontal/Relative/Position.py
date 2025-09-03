from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PositionCls:
	"""Position commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("position", core, parent)

	def set(self, relative_center: float, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> None:
		"""LAYout<*>:ZOOM<*>:HORizontal:RELative:POSition \n
		Snippet: driver.layout.zoom.horizontal.relative.position.set(relative_center = 1.0, layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Defines the x-value of the centerpoint of the zoom area in relative values. \n
			:param relative_center: Relative position of the centerpoint (x-value)
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
		"""
		param = Conversions.decimal_value_to_str(relative_center)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		self._core.io.write(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:HORizontal:RELative:POSition {param}')

	def get(self, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> float:
		"""LAYout<*>:ZOOM<*>:HORizontal:RELative:POSition \n
		Snippet: value: float = driver.layout.zoom.horizontal.relative.position.get(layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Defines the x-value of the centerpoint of the zoom area in relative values. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
			:return: relative_center: Relative position of the centerpoint (x-value)"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:HORizontal:RELative:POSition?')
		return Conversions.str_to_float(response)
