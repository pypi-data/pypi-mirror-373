from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ScaleCls:
	"""Scale commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("scale", core, parent)

	def set(self, quad_spi_io_1_scale: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:QSPI:IOONe:SCALe \n
		Snippet: driver.sbus.qspi.ioOne.scale.set(quad_spi_io_1_scale = 1.0, serialBus = repcap.SerialBus.Default) \n
		Set the vertical scale of the IO1 signal. \n
			:param quad_spi_io_1_scale: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(quad_spi_io_1_scale)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:IOONe:SCALe {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:QSPI:IOONe:SCALe \n
		Snippet: value: float = driver.sbus.qspi.ioOne.scale.get(serialBus = repcap.SerialBus.Default) \n
		Set the vertical scale of the IO1 signal. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: quad_spi_io_1_scale: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:IOONe:SCALe?')
		return Conversions.str_to_float(response)
