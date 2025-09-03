from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, state: bool, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> None:
		"""LAYout<*>:ZOOM<*>[:ENABle] \n
		Snippet: driver.layout.zoom.enable.set(state = False, layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Enables the zoom. \n
			:param state: No help available
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
		"""
		param = Conversions.bool_to_str(state)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		self._core.io.write(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:ENABle {param}')

	def get(self, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> bool:
		"""LAYout<*>:ZOOM<*>[:ENABle] \n
		Snippet: value: bool = driver.layout.zoom.enable.get(layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Enables the zoom. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
			:return: state: No help available"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)
