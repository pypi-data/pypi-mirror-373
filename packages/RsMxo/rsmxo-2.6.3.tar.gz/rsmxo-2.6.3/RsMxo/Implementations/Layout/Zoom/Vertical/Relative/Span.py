from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SpanCls:
	"""Span commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("span", core, parent)

	def set(self, relative_span: float, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> None:
		"""LAYout<*>:ZOOM<*>:VERTical:RELative:SPAN \n
		Snippet: driver.layout.zoom.vertical.relative.span.set(relative_span = 1.0, layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Defines the height of the zoom area in relative values. \n
			:param relative_span: No help available
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
		"""
		param = Conversions.decimal_value_to_str(relative_span)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		self._core.io.write(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:VERTical:RELative:SPAN {param}')

	def get(self, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> float:
		"""LAYout<*>:ZOOM<*>:VERTical:RELative:SPAN \n
		Snippet: value: float = driver.layout.zoom.vertical.relative.span.get(layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Defines the height of the zoom area in relative values. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
			:return: relative_span: No help available"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:VERTical:RELative:SPAN?')
		return Conversions.str_to_float(response)
