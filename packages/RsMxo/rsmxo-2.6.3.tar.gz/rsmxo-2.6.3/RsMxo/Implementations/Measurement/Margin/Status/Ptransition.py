from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PtransitionCls:
	"""Ptransition commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ptransition", core, parent)

	def set(self, value: bool, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:MARGin:STATus:PTRansition \n
		Snippet: driver.measurement.margin.status.ptransition.set(value = False, measIndex = repcap.MeasIndex.Default) \n
		Sets the positive transition filter. If a bit is set, a transition from 0 to 1 in the condition part causes an entry to
		be made in the corresponding bit of the EVENt part of the register. \n
			:param value: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.bool_to_str(value)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:MARGin:STATus:PTRansition {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> bool:
		"""MEASurement<*>:MARGin:STATus:PTRansition \n
		Snippet: value: bool = driver.measurement.margin.status.ptransition.get(measIndex = repcap.MeasIndex.Default) \n
		Sets the positive transition filter. If a bit is set, a transition from 0 to 1 in the condition part causes an entry to
		be made in the corresponding bit of the EVENt part of the register. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: value: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:MARGin:STATus:PTRansition?')
		return Conversions.str_to_bool(response)
