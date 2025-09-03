from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, relative_levels: enums.RelativeLevels, power=repcap.Power.Default, refLevel=repcap.RefLevel.Default) -> None:
		"""POWer<*>:QUALity:REFLevel<*>:RELative:MODE \n
		Snippet: driver.power.quality.refLevel.relative.mode.set(relative_levels = enums.RelativeLevels.FIVE, power = repcap.Power.Default, refLevel = repcap.RefLevel.Default) \n
		The lower, middle and upper reference levels, defined as percentages of the high signal level. \n
			:param relative_levels:
				- FIVE: 5/50/95
				- TEN: 10/50/90
				- TWENty: 20/50/80
				- USER: Set the reference levels to individual values with POWerm:QUALity:REFLevelrl:RELative:LOWer, POWerm:QUALity:REFLevelrl:RELative:MIDDle, and POWerm:QUALity:REFLevelrl:RELative:UPPer.
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')"""
		param = Conversions.enum_scalar_to_str(relative_levels, enums.RelativeLevels)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'POWer{power_cmd_val}:QUALity:REFLevel{refLevel_cmd_val}:RELative:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default, refLevel=repcap.RefLevel.Default) -> enums.RelativeLevels:
		"""POWer<*>:QUALity:REFLevel<*>:RELative:MODE \n
		Snippet: value: enums.RelativeLevels = driver.power.quality.refLevel.relative.mode.get(power = repcap.Power.Default, refLevel = repcap.RefLevel.Default) \n
		The lower, middle and upper reference levels, defined as percentages of the high signal level. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: relative_levels:
				- FIVE: 5/50/95
				- TEN: 10/50/90
				- TWENty: 20/50/80
				- USER: Set the reference levels to individual values with POWerm:QUALity:REFLevelrl:RELative:LOWer, POWerm:QUALity:REFLevelrl:RELative:MIDDle, and POWerm:QUALity:REFLevelrl:RELative:UPPer."""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:QUALity:REFLevel{refLevel_cmd_val}:RELative:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.RelativeLevels)
