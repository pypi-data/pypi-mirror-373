from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SscreenCls:
	"""Sscreen commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sscreen", core, parent)

	def set(self, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default) -> None:
		"""LAYout<*>:ZOOM<*>:SSCReen \n
		Snippet: driver.layout.zoom.sscreen.set(layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Sets the zoom area to the whole screen. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
		"""
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		self._core.io.write(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:SSCReen')

	def set_and_wait(self, layout=repcap.Layout.Default, zoom=repcap.Zoom.Default, opc_timeout_ms: int = -1) -> None:
		layout_cmd_val = self._cmd_group.get_repcap_cmd_value(layout, repcap.Layout)
		zoom_cmd_val = self._cmd_group.get_repcap_cmd_value(zoom, repcap.Zoom)
		"""LAYout<*>:ZOOM<*>:SSCReen \n
		Snippet: driver.layout.zoom.sscreen.set_and_wait(layout = repcap.Layout.Default, zoom = repcap.Zoom.Default) \n
		Sets the zoom area to the whole screen. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param layout: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Layout')
			:param zoom: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zoom')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'LAYout{layout_cmd_val}:ZOOM{zoom_cmd_val}:SSCReen', opc_timeout_ms)
