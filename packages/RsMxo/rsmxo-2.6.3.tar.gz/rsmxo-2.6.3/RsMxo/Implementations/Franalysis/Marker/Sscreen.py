from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SscreenCls:
	"""Sscreen commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sscreen", core, parent)

	def set(self, marker=repcap.Marker.Default) -> None:
		"""FRANalysis:MARKer<*>:SSCReen \n
		Snippet: driver.franalysis.marker.sscreen.set(marker = repcap.Marker.Default) \n
		Resets the marker to their initial positions. Reset is helpful if the markers have disappeared from the display or need
		to be moved for a larger distance. \n
			:param marker: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Marker')
		"""
		marker_cmd_val = self._cmd_group.get_repcap_cmd_value(marker, repcap.Marker)
		self._core.io.write(f'FRANalysis:MARKer{marker_cmd_val}:SSCReen')

	def set_and_wait(self, marker=repcap.Marker.Default, opc_timeout_ms: int = -1) -> None:
		marker_cmd_val = self._cmd_group.get_repcap_cmd_value(marker, repcap.Marker)
		"""FRANalysis:MARKer<*>:SSCReen \n
		Snippet: driver.franalysis.marker.sscreen.set_and_wait(marker = repcap.Marker.Default) \n
		Resets the marker to their initial positions. Reset is helpful if the markers have disappeared from the display or need
		to be moved for a larger distance. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param marker: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Marker')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'FRANalysis:MARKer{marker_cmd_val}:SSCReen', opc_timeout_ms)
