from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UlevelCls:
	"""Ulevel commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ulevel", core, parent)

	def set(self, upper_level: float, power=repcap.Power.Default, refLevel=repcap.RefLevel.Default) -> None:
		"""POWer<*>:HARMonics:REFLevel<*>:ABSolute:ULEVel \n
		Snippet: driver.power.harmonics.refLevel.absolute.ulevel.set(upper_level = 1.0, power = repcap.Power.Default, refLevel = repcap.RefLevel.Default) \n
		Sets the upper reference level in absolute values. This is required to determine a rise. \n
			:param upper_level: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.decimal_value_to_str(upper_level)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:REFLevel{refLevel_cmd_val}:ABSolute:ULEVel {param}')

	def get(self, power=repcap.Power.Default, refLevel=repcap.RefLevel.Default) -> float:
		"""POWer<*>:HARMonics:REFLevel<*>:ABSolute:ULEVel \n
		Snippet: value: float = driver.power.harmonics.refLevel.absolute.ulevel.get(power = repcap.Power.Default, refLevel = repcap.RefLevel.Default) \n
		Sets the upper reference level in absolute values. This is required to determine a rise. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: upper_level: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:REFLevel{refLevel_cmd_val}:ABSolute:ULEVel?')
		return Conversions.str_to_float(response)
