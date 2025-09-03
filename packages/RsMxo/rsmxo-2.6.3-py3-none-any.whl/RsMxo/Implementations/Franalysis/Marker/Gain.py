from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GainCls:
	"""Gain commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gain", core, parent)

	def get(self, marker=repcap.Marker.Default) -> float:
		"""FRANalysis:MARKer<*>:GAIN \n
		Snippet: value: float = driver.franalysis.marker.gain.get(marker = repcap.Marker.Default) \n
		Returns the gain for the specified marker. \n
			:param marker: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Marker')
			:return: gain: No help available"""
		marker_cmd_val = self._cmd_group.get_repcap_cmd_value(marker, repcap.Marker)
		response = self._core.io.query_str(f'FRANalysis:MARKer{marker_cmd_val}:GAIN?')
		return Conversions.str_to_float(response)
