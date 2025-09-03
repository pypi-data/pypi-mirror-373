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

	def set(self, io_0_polarity: enums.SbusSpiCsPolarity, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:QSPI:IOZero:POLarity \n
		Snippet: driver.sbus.qspi.ioZero.polarity.set(io_0_polarity = enums.SbusSpiCsPolarity.ACTHigh, serialBus = repcap.SerialBus.Default) \n
		Selects if the transmitted signal for the respective line is active high (high = 1) or active low (low = 1) . \n
			:param io_0_polarity: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(io_0_polarity, enums.SbusSpiCsPolarity)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:IOZero:POLarity {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusSpiCsPolarity:
		"""SBUS<*>:QSPI:IOZero:POLarity \n
		Snippet: value: enums.SbusSpiCsPolarity = driver.sbus.qspi.ioZero.polarity.get(serialBus = repcap.SerialBus.Default) \n
		Selects if the transmitted signal for the respective line is active high (high = 1) or active low (low = 1) . \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: io_0_polarity: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:IOZero:POLarity?')
		return Conversions.str_to_scalar_enum(response, enums.SbusSpiCsPolarity)
