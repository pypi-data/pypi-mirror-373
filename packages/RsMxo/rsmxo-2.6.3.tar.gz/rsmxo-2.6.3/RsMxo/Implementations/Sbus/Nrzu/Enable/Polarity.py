from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PolarityCls:
	"""Polarity commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("polarity", core, parent)

	def set(self, enable_polarity: enums.SbusSpiCsPolarity, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:NRZU:ENABle:POLarity \n
		Snippet: driver.sbus.nrzu.enable.polarity.set(enable_polarity = enums.SbusSpiCsPolarity.ACTHigh, serialBus = repcap.SerialBus.Default) \n
		Sets the polarity for the enable line. \n
			:param enable_polarity:
				- ACTLow: The transmitted signal for the enable line is active high (high = 1) .
				- ACTHigh: The transmitted signal for the enable line is active low (low = 1) .
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')"""
		param = Conversions.enum_scalar_to_str(enable_polarity, enums.SbusSpiCsPolarity)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZU:ENABle:POLarity {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusSpiCsPolarity:
		"""SBUS<*>:NRZU:ENABle:POLarity \n
		Snippet: value: enums.SbusSpiCsPolarity = driver.sbus.nrzu.enable.polarity.get(serialBus = repcap.SerialBus.Default) \n
		Sets the polarity for the enable line. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: enable_polarity:
				- ACTLow: The transmitted signal for the enable line is active high (high = 1) .
				- ACTHigh: The transmitted signal for the enable line is active low (low = 1) ."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZU:ENABle:POLarity?')
		return Conversions.str_to_scalar_enum(response, enums.SbusSpiCsPolarity)
