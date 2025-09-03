from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PolarityCls:
	"""Polarity commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("polarity", core, parent)

	def set(self, polarity: enums.SbusArincPolarity, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:ARINc:POLarity \n
		Snippet: driver.sbus.arinc.polarity.set(polarity = enums.SbusArincPolarity.ALEG, serialBus = repcap.SerialBus.Default) \n
		Selects the wire on which the bus signal is measured : A Leg or B Leg. The setting affects the digitization of the signal. \n
			:param polarity: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(polarity, enums.SbusArincPolarity)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:ARINc:POLarity {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusArincPolarity:
		"""SBUS<*>:ARINc:POLarity \n
		Snippet: value: enums.SbusArincPolarity = driver.sbus.arinc.polarity.get(serialBus = repcap.SerialBus.Default) \n
		Selects the wire on which the bus signal is measured : A Leg or B Leg. The setting affects the digitization of the signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: polarity: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:ARINc:POLarity?')
		return Conversions.str_to_scalar_enum(response, enums.SbusArincPolarity)
