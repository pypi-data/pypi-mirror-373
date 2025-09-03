from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LlevelCls:
	"""Llevel commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("llevel", core, parent)

	def set(self, lower_level: float, power=repcap.Power.Default, refLevel=repcap.RefLevel.Default) -> None:
		"""POWer<*>:QUALity:REFLevel<*>:ABSolute:LLEVel \n
		Snippet: driver.power.quality.refLevel.absolute.llevel.set(lower_level = 1.0, power = repcap.Power.Default, refLevel = repcap.RefLevel.Default) \n
		Sets the lower reference level in absolute values. This is required, e.g., to determine a fall. \n
			:param lower_level: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.decimal_value_to_str(lower_level)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'POWer{power_cmd_val}:QUALity:REFLevel{refLevel_cmd_val}:ABSolute:LLEVel {param}')

	def get(self, power=repcap.Power.Default, refLevel=repcap.RefLevel.Default) -> float:
		"""POWer<*>:QUALity:REFLevel<*>:ABSolute:LLEVel \n
		Snippet: value: float = driver.power.quality.refLevel.absolute.llevel.get(power = repcap.Power.Default, refLevel = repcap.RefLevel.Default) \n
		Sets the lower reference level in absolute values. This is required, e.g., to determine a fall. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: lower_level: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:REFLevel{refLevel_cmd_val}:ABSolute:LLEVel?')
		return Conversions.str_to_float(response)
