from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StopCls:
	"""Stop commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("stop", core, parent)

	def set(self, relative_stop: float, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> None:
		"""LAYout<*>:ZOOM<*>:HORizontal:RELative:STOP \n
		Snippet: driver.layout.zoom.horizontal.relative.stop.set(relative_stop = 1.0, layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Defines the upper limit of the zoom area on the x-axis in relative values. \n
			:param relative_stop: No help available
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
		"""
		param = Conversions.decimal_value_to_str(relative_stop)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		self._core.io.write(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:HORizontal:RELative:STOP {param}')

	def get(self, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> float:
		"""LAYout<*>:ZOOM<*>:HORizontal:RELative:STOP \n
		Snippet: value: float = driver.layout.zoom.horizontal.relative.stop.get(layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Defines the upper limit of the zoom area on the x-axis in relative values. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
			:return: relative_stop: No help available"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:HORizontal:RELative:STOP?')
		return Conversions.str_to_float(response)
