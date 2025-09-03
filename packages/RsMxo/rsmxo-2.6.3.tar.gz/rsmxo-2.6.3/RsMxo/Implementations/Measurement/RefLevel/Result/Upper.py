from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UpperCls:
	"""Upper commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("upper", core, parent)

	def get(self, measIndex=repcap.MeasIndex.Default, refLevel=repcap.RefLevel.Default) -> float:
		"""MEASurement<*>:REFLevel<*>:RESult:UPPer \n
		Snippet: value: float = driver.measurement.refLevel.result.upper.get(measIndex = repcap.MeasIndex.Default, refLevel = repcap.RefLevel.Default) \n
		Return the lower, middle, and upper reference level, respectively. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: upper: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:REFLevel{refLevel_cmd_val}:RESult:UPPer?')
		return Conversions.str_to_float(response)
