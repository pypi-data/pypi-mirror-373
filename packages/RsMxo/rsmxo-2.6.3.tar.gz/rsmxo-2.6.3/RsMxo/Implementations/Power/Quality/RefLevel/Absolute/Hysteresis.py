from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HysteresisCls:
	"""Hysteresis commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hysteresis", core, parent)

	def set(self, hyst_abs: float, power=repcap.Power.Default, refLevel=repcap.RefLevel.Default) -> None:
		"""POWer<*>:QUALity:REFLevel<*>:ABSolute:HYSTeresis \n
		Snippet: driver.power.quality.refLevel.absolute.hysteresis.set(hyst_abs = 1.0, power = repcap.Power.Default, refLevel = repcap.RefLevel.Default) \n
		Defines a hysteresis for the middle reference level. A rise or fall from the middle reference value that does not exceed
		the hysteresis is rejected as noise. \n
			:param hyst_abs: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.decimal_value_to_str(hyst_abs)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'POWer{power_cmd_val}:QUALity:REFLevel{refLevel_cmd_val}:ABSolute:HYSTeresis {param}')

	def get(self, power=repcap.Power.Default, refLevel=repcap.RefLevel.Default) -> float:
		"""POWer<*>:QUALity:REFLevel<*>:ABSolute:HYSTeresis \n
		Snippet: value: float = driver.power.quality.refLevel.absolute.hysteresis.get(power = repcap.Power.Default, refLevel = repcap.RefLevel.Default) \n
		Defines a hysteresis for the middle reference level. A rise or fall from the middle reference value that does not exceed
		the hysteresis is rejected as noise. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: hyst_abs: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:REFLevel{refLevel_cmd_val}:ABSolute:HYSTeresis?')
		return Conversions.str_to_float(response)
