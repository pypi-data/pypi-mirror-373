from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UpperCls:
	"""Upper commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("upper", core, parent)

	def set(self, upp_ref_lev_rel: float, power=repcap.Power.Default, refLevel=repcap.RefLevel.Default) -> None:
		"""POWer<*>:HARMonics:REFLevel<*>:RELative:UPPer \n
		Snippet: driver.power.harmonics.refLevel.relative.upper.set(upp_ref_lev_rel = 1.0, power = repcap.Power.Default, refLevel = repcap.RefLevel.Default) \n
		Sets the upper relative reference level if method RsMxo.Power.Quality.RefLevel.Relative.Mode.set is set to USER. \n
			:param upp_ref_lev_rel: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.decimal_value_to_str(upp_ref_lev_rel)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:REFLevel{refLevel_cmd_val}:RELative:UPPer {param}')

	def get(self, power=repcap.Power.Default, refLevel=repcap.RefLevel.Default) -> float:
		"""POWer<*>:HARMonics:REFLevel<*>:RELative:UPPer \n
		Snippet: value: float = driver.power.harmonics.refLevel.relative.upper.get(power = repcap.Power.Default, refLevel = repcap.RefLevel.Default) \n
		Sets the upper relative reference level if method RsMxo.Power.Quality.RefLevel.Relative.Mode.set is set to USER. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: upp_ref_lev_rel: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:REFLevel{refLevel_cmd_val}:RELative:UPPer?')
		return Conversions.str_to_float(response)
