from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrequencyCls:
	"""Frequency commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frequency", core, parent)

	def set(self, frequency: float, point=repcap.Point.Default) -> None:
		"""FRANalysis:AMPLitude:PROFile:POINt<*>:FREQuency \n
		Snippet: driver.franalysis.amplitude.profile.point.frequency.set(frequency = 1.0, point = repcap.Point.Default) \n
		Sets the start frequency for the selected point. \n
			:param frequency: No help available
			:param point: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Point')
		"""
		param = Conversions.decimal_value_to_str(frequency)
		point_cmd_val = self._cmd_group.get_repcap_cmd_value(point, repcap.Point)
		self._core.io.write(f'FRANalysis:AMPLitude:PROFile:POINt{point_cmd_val}:FREQuency {param}')

	def get(self, point=repcap.Point.Default) -> float:
		"""FRANalysis:AMPLitude:PROFile:POINt<*>:FREQuency \n
		Snippet: value: float = driver.franalysis.amplitude.profile.point.frequency.get(point = repcap.Point.Default) \n
		Sets the start frequency for the selected point. \n
			:param point: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Point')
			:return: frequency: No help available"""
		point_cmd_val = self._cmd_group.get_repcap_cmd_value(point, repcap.Point)
		response = self._core.io.query_str(f'FRANalysis:AMPLitude:PROFile:POINt{point_cmd_val}:FREQuency?')
		return Conversions.str_to_float(response)
