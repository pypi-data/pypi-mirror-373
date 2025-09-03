from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, mode: enums.AbsRel, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> None:
		"""LAYout<*>:ZOOM<*>:VERTical:MODE \n
		Snippet: driver.layout.zoom.vertical.mode.set(mode = enums.AbsRel.ABS, layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Defines if absolute or relative values are used to specify the y-axis values. Since the zoom area refers to the active
		signal, relative values ensure that the zoom area remains the same. \n
			:param mode: No help available
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.AbsRel)
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		self._core.io.write(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:VERTical:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> enums.AbsRel:
		"""LAYout<*>:ZOOM<*>:VERTical:MODE \n
		Snippet: value: enums.AbsRel = driver.layout.zoom.vertical.mode.get(layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Defines if absolute or relative values are used to specify the y-axis values. Since the zoom area refers to the active
		signal, relative values ensure that the zoom area remains the same. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
			:return: mode: No help available"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:VERTical:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AbsRel)
