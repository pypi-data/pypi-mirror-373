from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UartCls:
	"""Uart commands group definition. 6 total commands, 0 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("uart", core, parent)

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.SbusUartTriggerType:
		"""TRIGger:SBHW:UART:TYPE \n
		Snippet: value: enums.SbusUartTriggerType = driver.trigger.sbhw.uart.get_type_py() \n
		Selects the trigger type condition. \n
			:return: type_py: STBT: Start bit PCKS: Packet start DATA: Serial pattern PRER: Parity error BRKC: Break condition STPerror: Stop error
		"""
		response = self._core.io.query_str('TRIGger:SBHW:UART:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusUartTriggerType)

	def set_type_py(self, type_py: enums.SbusUartTriggerType) -> None:
		"""TRIGger:SBHW:UART:TYPE \n
		Snippet: driver.trigger.sbhw.uart.set_type_py(type_py = enums.SbusUartTriggerType.BRKC) \n
		Selects the trigger type condition. \n
			:param type_py: STBT: Start bit PCKS: Packet start DATA: Serial pattern PRER: Parity error BRKC: Break condition STPerror: Stop error
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.SbusUartTriggerType)
		self._core.io.write(f'TRIGger:SBHW:UART:TYPE {param}')

	# noinspection PyTypeChecker
	def get_source(self) -> enums.TxRx:
		"""TRIGger:SBHW:UART:SOURce \n
		Snippet: value: enums.TxRx = driver.trigger.sbhw.uart.get_source() \n
		Selects the transmitter or receiver line as trigger source. \n
			:return: source: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:UART:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.TxRx)

	def set_source(self, source: enums.TxRx) -> None:
		"""TRIGger:SBHW:UART:SOURce \n
		Snippet: driver.trigger.sbhw.uart.set_source(source = enums.TxRx.RX) \n
		Selects the transmitter or receiver line as trigger source. \n
			:param source: No help available
		"""
		param = Conversions.enum_scalar_to_str(source, enums.TxRx)
		self._core.io.write(f'TRIGger:SBHW:UART:SOURce {param}')

	def get_data(self) -> List[int]:
		"""TRIGger:SBHW:UART:DATA \n
		Snippet: value: List[int] = driver.trigger.sbhw.uart.get_data() \n
		Specifies the data pattern to be found on the specified trigger source. Enter the words in MSB first bit order. \n
			:return: data_pattern: No help available
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:UART:DATA?')
		return response

	def set_data(self, data_pattern: List[int]) -> None:
		"""TRIGger:SBHW:UART:DATA \n
		Snippet: driver.trigger.sbhw.uart.set_data(data_pattern = [1, 2, 3]) \n
		Specifies the data pattern to be found on the specified trigger source. Enter the words in MSB first bit order. \n
			:param data_pattern: No help available
		"""
		param = Conversions.list_to_csv_str(data_pattern)
		self._core.io.write(f'TRIGger:SBHW:UART:DATA {param}')

	# noinspection PyTypeChecker
	def get_operator(self) -> enums.OperatorB:
		"""TRIGger:SBHW:UART:OPERator \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.uart.get_operator() \n
		Sets the operator for the data pattern in the selected field of the selected frame. \n
			:return: data_operator: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:UART:OPERator?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_operator(self, data_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:UART:OPERator \n
		Snippet: driver.trigger.sbhw.uart.set_operator(data_operator = enums.OperatorB.EQUal) \n
		Sets the operator for the data pattern in the selected field of the selected frame. \n
			:param data_operator: No help available
		"""
		param = Conversions.enum_scalar_to_str(data_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:UART:OPERator {param}')

	def get_dposition(self) -> int:
		"""TRIGger:SBHW:UART:DPOSition \n
		Snippet: value: int = driver.trigger.sbhw.uart.get_dposition() \n
		Sets the number of words before the first word of interest. These offset words are ignored. \n
			:return: data_position: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:UART:DPOSition?')
		return Conversions.str_to_int(response)

	def set_dposition(self, data_position: int) -> None:
		"""TRIGger:SBHW:UART:DPOSition \n
		Snippet: driver.trigger.sbhw.uart.set_dposition(data_position = 1) \n
		Sets the number of words before the first word of interest. These offset words are ignored. \n
			:param data_position: No help available
		"""
		param = Conversions.decimal_value_to_str(data_position)
		self._core.io.write(f'TRIGger:SBHW:UART:DPOSition {param}')

	# noinspection PyTypeChecker
	def get_fcondition(self) -> enums.OperatorB:
		"""TRIGger:SBHW:UART:FCONdition \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.uart.get_fcondition() \n
		Selects the operator for the Data pattern. \n
			:return: data_operator: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:UART:FCONdition?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_fcondition(self, data_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:UART:FCONdition \n
		Snippet: driver.trigger.sbhw.uart.set_fcondition(data_operator = enums.OperatorB.EQUal) \n
		Selects the operator for the Data pattern. \n
			:param data_operator: No help available
		"""
		param = Conversions.enum_scalar_to_str(data_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:UART:FCONdition {param}')
