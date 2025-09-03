from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DiagnosticCls:
	"""Diagnostic commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("diagnostic", core, parent)

	def get(self, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> str:
		"""LAYout<*>:ZOOM<*>:DIAG \n
		Snippet: value: str = driver.layout.zoom.diagnostic.get(layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Returns the index of the diagram that shows the zoomed waveform. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
			:return: zoom_diagram_key: String wiht the index of the zoom diagram, e.g. '9'."""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		response = self._core.io.query_str(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:DIAG?')
		return trim_str_response(response)
