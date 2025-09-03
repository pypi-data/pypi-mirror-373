from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HysteresisCls:
	"""Hysteresis commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hysteresis", core, parent)

	def set(self, hysteresis: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:QSPI:IOZero:HYSTeresis \n
		Snippet: driver.sbus.qspi.ioZero.hysteresis.set(hysteresis = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets a value for the hysteresis for the IO0 line. \n
			:param hysteresis: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(hysteresis)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:IOZero:HYSTeresis {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:QSPI:IOZero:HYSTeresis \n
		Snippet: value: float = driver.sbus.qspi.ioZero.hysteresis.get(serialBus = repcap.SerialBus.Default) \n
		Sets a value for the hysteresis for the IO0 line. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: hysteresis: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:IOZero:HYSTeresis?')
		return Conversions.str_to_float(response)
