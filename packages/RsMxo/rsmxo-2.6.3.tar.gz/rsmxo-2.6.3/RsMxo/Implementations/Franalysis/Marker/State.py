from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, markers: bool, marker=repcap.Marker.Default) -> None:
		"""FRANalysis:MARKer<*>:STATe \n
		Snippet: driver.franalysis.marker.state.set(markers = False, marker = repcap.Marker.Default) \n
		Enables the display of the marker table for the FRA. \n
			:param markers: No help available
			:param marker: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Marker')
		"""
		param = Conversions.bool_to_str(markers)
		marker_cmd_val = self._cmd_group.get_repcap_cmd_value(marker, repcap.Marker)
		self._core.io.write(f'FRANalysis:MARKer{marker_cmd_val}:STATe {param}')

	def get(self, marker=repcap.Marker.Default) -> bool:
		"""FRANalysis:MARKer<*>:STATe \n
		Snippet: value: bool = driver.franalysis.marker.state.get(marker = repcap.Marker.Default) \n
		Enables the display of the marker table for the FRA. \n
			:param marker: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Marker')
			:return: markers: No help available"""
		marker_cmd_val = self._cmd_group.get_repcap_cmd_value(marker, repcap.Marker)
		response = self._core.io.query_str(f'FRANalysis:MARKer{marker_cmd_val}:STATe?')
		return Conversions.str_to_bool(response)
