from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ScaleCls:
	"""Scale commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("scale", core, parent)

	def set(self, vertical_scale: float, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:TRACk:SCALe \n
		Snippet: driver.measurement.track.scale.set(vertical_scale = 1.0, measIndex = repcap.MeasIndex.Default) \n
		Sets or queries the vertical scale of the track diagram. If method RsMxo.Measurement.Track.Contiunous.set is ON, use the
		command to query the current value. If method RsMxo.Measurement.Track.Contiunous.set is OFF, the command sets the scale. \n
			:param vertical_scale: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.decimal_value_to_str(vertical_scale)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:TRACk:SCALe {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> float:
		"""MEASurement<*>:TRACk:SCALe \n
		Snippet: value: float = driver.measurement.track.scale.get(measIndex = repcap.MeasIndex.Default) \n
		Sets or queries the vertical scale of the track diagram. If method RsMxo.Measurement.Track.Contiunous.set is ON, use the
		command to query the current value. If method RsMxo.Measurement.Track.Contiunous.set is OFF, the command sets the scale. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: vertical_scale: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:TRACk:SCALe?')
		return Conversions.str_to_float(response)
