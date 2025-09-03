from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnCls:
	"""En commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("en", core, parent)

	def set(self, fundamental_freq_en_61000: enums.FundamentalFreqEn61000, power=repcap.Power.Default) -> None:
		"""POWer<*>:HARMonics:FREQuency:EN \n
		Snippet: driver.power.harmonics.frequency.en.set(fundamental_freq_en_61000 = enums.FundamentalFreqEn61000.AUTO, power = repcap.Power.Default) \n
		Sets the fundamental frequency of the input signal for the EN61000 standard, if method RsMxo.Power.Harmonics.Standard.set
		is set to ENA / ENB / ENC / END. \n
			:param fundamental_freq_en_61000: F50: 50 Hz F60: 60 Hz AUTO: automatically set
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(fundamental_freq_en_61000, enums.FundamentalFreqEn61000)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:FREQuency:EN {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.FundamentalFreqEn61000:
		"""POWer<*>:HARMonics:FREQuency:EN \n
		Snippet: value: enums.FundamentalFreqEn61000 = driver.power.harmonics.frequency.en.get(power = repcap.Power.Default) \n
		Sets the fundamental frequency of the input signal for the EN61000 standard, if method RsMxo.Power.Harmonics.Standard.set
		is set to ENA / ENB / ENC / END. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: fundamental_freq_en_61000: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:FREQuency:EN?')
		return Conversions.str_to_scalar_enum(response, enums.FundamentalFreqEn61000)
