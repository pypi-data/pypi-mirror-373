from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MilCls:
	"""Mil commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mil", core, parent)

	def set(self, fundamental_freq_mil: enums.FundamentalFreqMil, power=repcap.Power.Default) -> None:
		"""POWer<*>:HARMonics:FREQuency:MIL \n
		Snippet: driver.power.harmonics.frequency.mil.set(fundamental_freq_mil = enums.FundamentalFreqMil.F400, power = repcap.Power.Default) \n
		Sets the fundamental frequency of the input signal for the MIL standard, if method RsMxo.Power.Harmonics.Standard.set is
		set to MIL. \n
			:param fundamental_freq_mil: F60: 60 Hz F400: 400 Hz
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(fundamental_freq_mil, enums.FundamentalFreqMil)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:FREQuency:MIL {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.FundamentalFreqMil:
		"""POWer<*>:HARMonics:FREQuency:MIL \n
		Snippet: value: enums.FundamentalFreqMil = driver.power.harmonics.frequency.mil.get(power = repcap.Power.Default) \n
		Sets the fundamental frequency of the input signal for the MIL standard, if method RsMxo.Power.Harmonics.Standard.set is
		set to MIL. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: fundamental_freq_mil: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:FREQuency:MIL?')
		return Conversions.str_to_scalar_enum(response, enums.FundamentalFreqMil)
