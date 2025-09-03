from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ActiveCls:
	"""Active commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("active", core, parent)

	def set(self, first: bool, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:ACTive \n
		Snippet: driver.measurement.active.set(first = False, measIndex = repcap.MeasIndex.Default) \n
		No command help available \n
			:param first: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.bool_to_str(first)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:ACTive {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> bool:
		"""MEASurement<*>:ACTive \n
		Snippet: value: bool = driver.measurement.active.get(measIndex = repcap.MeasIndex.Default) \n
		No command help available \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: first: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:ACTive?')
		return Conversions.str_to_bool(response)
