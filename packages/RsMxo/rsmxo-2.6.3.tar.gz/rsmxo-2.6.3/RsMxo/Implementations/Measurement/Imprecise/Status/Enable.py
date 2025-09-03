from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, value: bool, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:IMPRecise:STATus:ENABle \n
		Snippet: driver.measurement.imprecise.status.enable.set(value = False, measIndex = repcap.MeasIndex.Default) \n
		Sets the ENABle part that allows true conditions in the EVENt part to be reported for the summary bit in the status byte.
		These events can be used for a service request. If a bit in the ENABle part is 1, and the corresponding EVENt bit is true,
		a positive transition occurs in the summary bit. This transition is reported to the next higher level. See Table 'Source
		values for STATus:QUEStionable:...:[:EVENt] and STATus:QUEStionable:...:[:ENABLe]' for a list of the return values. \n
			:param value: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.bool_to_str(value)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:IMPRecise:STATus:ENABle {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> bool:
		"""MEASurement<*>:IMPRecise:STATus:ENABle \n
		Snippet: value: bool = driver.measurement.imprecise.status.enable.get(measIndex = repcap.MeasIndex.Default) \n
		Sets the ENABle part that allows true conditions in the EVENt part to be reported for the summary bit in the status byte.
		These events can be used for a service request. If a bit in the ENABle part is 1, and the corresponding EVENt bit is true,
		a positive transition occurs in the summary bit. This transition is reported to the next higher level. See Table 'Source
		values for STATus:QUEStionable:...:[:EVENt] and STATus:QUEStionable:...:[:ENABLe]' for a list of the return values. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: value: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:IMPRecise:STATus:ENABle?')
		return Conversions.str_to_bool(response)
