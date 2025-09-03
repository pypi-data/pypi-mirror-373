from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HarmonicsCls:
	"""Harmonics commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("harmonics", core, parent)

	def set(self, disped_harmonics: enums.DispedHarmonics, power=repcap.Power.Default) -> None:
		"""POWer<*>:HARMonics:DISPlay:HARMonics \n
		Snippet: driver.power.harmonics.display.harmonics.set(disped_harmonics = enums.DispedHarmonics.ALL, power = repcap.Power.Default) \n
		Selects which harmonics are displayed in the bargraph: all, odd even or depending on the standard definition. \n
			:param disped_harmonics: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(disped_harmonics, enums.DispedHarmonics)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:DISPlay:HARMonics {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.DispedHarmonics:
		"""POWer<*>:HARMonics:DISPlay:HARMonics \n
		Snippet: value: enums.DispedHarmonics = driver.power.harmonics.display.harmonics.get(power = repcap.Power.Default) \n
		Selects which harmonics are displayed in the bargraph: all, odd even or depending on the standard definition. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: disped_harmonics: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:DISPlay:HARMonics?')
		return Conversions.str_to_scalar_enum(response, enums.DispedHarmonics)
