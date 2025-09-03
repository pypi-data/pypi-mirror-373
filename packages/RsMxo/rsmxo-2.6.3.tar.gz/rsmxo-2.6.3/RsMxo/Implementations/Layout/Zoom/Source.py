from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, source: float, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> None:
		"""LAYout<*>:ZOOM<*>:SOURce \n
		Snippet: driver.layout.zoom.source.set(source = 1.0, layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Indicates which of the waveform diagrams is selected for zooming. The number is displayed on the screen in the middle of
		each diagram. \n
			:param source: Index of the diagram, which is zoomed.
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
		"""
		param = Conversions.decimal_value_to_str(source)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		self._core.io.write(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:SOURce {param}')

	def get(self, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> float:
		"""LAYout<*>:ZOOM<*>:SOURce \n
		Snippet: value: float = driver.layout.zoom.source.get(layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Indicates which of the waveform diagrams is selected for zooming. The number is displayed on the screen in the middle of
		each diagram. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
			:return: source: No help available"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:SOURce?')
		return Conversions.str_to_float(response)
