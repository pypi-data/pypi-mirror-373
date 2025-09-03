from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StandardCls:
	"""Standard commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("standard", core, parent)

	def set(self, standard: enums.PwrHarmonicsStandard, power=repcap.Power.Default) -> None:
		"""POWer<*>:HARMonics:STANdard \n
		Snippet: driver.power.harmonics.standard.set(standard = enums.PwrHarmonicsStandard.ENA, power = repcap.Power.Default) \n
		Sets a standard for the current harmonic measurement. \n
			:param standard: ENA: EN 61000-3-2 Class A ENB: EN 61000-3-2 Class B ENC: EN 61000-3-2 Class C END: EN 61000-3-2 Class D MIL: MIL-STD-1399 RTCA: RTCA DO-160
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(standard, enums.PwrHarmonicsStandard)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:STANdard {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.PwrHarmonicsStandard:
		"""POWer<*>:HARMonics:STANdard \n
		Snippet: value: enums.PwrHarmonicsStandard = driver.power.harmonics.standard.get(power = repcap.Power.Default) \n
		Sets a standard for the current harmonic measurement. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: standard: ENA: EN 61000-3-2 Class A ENB: EN 61000-3-2 Class B ENC: EN 61000-3-2 Class C END: EN 61000-3-2 Class D MIL: MIL-STD-1399 RTCA: RTCA DO-160"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:STANdard?')
		return Conversions.str_to_scalar_enum(response, enums.PwrHarmonicsStandard)
