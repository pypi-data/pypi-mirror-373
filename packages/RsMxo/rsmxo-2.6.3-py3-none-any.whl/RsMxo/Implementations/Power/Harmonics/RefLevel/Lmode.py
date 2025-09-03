from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LmodeCls:
	"""Lmode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("lmode", core, parent)

	def set(self, level_mode: enums.AbsRel, power=repcap.Power.Default, refLevel=repcap.RefLevel.Default) -> None:
		"""POWer<*>:HARMonics:REFLevel<*>:LMODe \n
		Snippet: driver.power.harmonics.refLevel.lmode.set(level_mode = enums.AbsRel.ABS, power = repcap.Power.Default, refLevel = repcap.RefLevel.Default) \n
		Defines if the reference level is set in absolute or relative values. \n
			:param level_mode: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.enum_scalar_to_str(level_mode, enums.AbsRel)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:REFLevel{refLevel_cmd_val}:LMODe {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default, refLevel=repcap.RefLevel.Default) -> enums.AbsRel:
		"""POWer<*>:HARMonics:REFLevel<*>:LMODe \n
		Snippet: value: enums.AbsRel = driver.power.harmonics.refLevel.lmode.get(power = repcap.Power.Default, refLevel = repcap.RefLevel.Default) \n
		Defines if the reference level is set in absolute or relative values. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: level_mode: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:REFLevel{refLevel_cmd_val}:LMODe?')
		return Conversions.str_to_scalar_enum(response, enums.AbsRel)
