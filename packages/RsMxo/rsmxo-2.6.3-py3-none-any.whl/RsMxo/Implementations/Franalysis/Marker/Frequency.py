from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrequencyCls:
	"""Frequency commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frequency", core, parent)

	def set(self, frequency: float, marker=repcap.Marker.Default) -> None:
		"""FRANalysis:MARKer<*>:FREQuency \n
		Snippet: driver.franalysis.marker.frequency.set(frequency = 1.0, marker = repcap.Marker.Default) \n
		Returns the frequency for the specified marker. \n
			:param frequency: No help available
			:param marker: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Marker')
		"""
		param = Conversions.decimal_value_to_str(frequency)
		marker_cmd_val = self._cmd_group.get_repcap_cmd_value(marker, repcap.Marker)
		self._core.io.write(f'FRANalysis:MARKer{marker_cmd_val}:FREQuency {param}')

	def get(self, marker=repcap.Marker.Default) -> float:
		"""FRANalysis:MARKer<*>:FREQuency \n
		Snippet: value: float = driver.franalysis.marker.frequency.get(marker = repcap.Marker.Default) \n
		Returns the frequency for the specified marker. \n
			:param marker: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Marker')
			:return: frequency: No help available"""
		marker_cmd_val = self._cmd_group.get_repcap_cmd_value(marker, repcap.Marker)
		response = self._core.io.query_str(f'FRANalysis:MARKer{marker_cmd_val}:FREQuency?')
		return Conversions.str_to_float(response)
