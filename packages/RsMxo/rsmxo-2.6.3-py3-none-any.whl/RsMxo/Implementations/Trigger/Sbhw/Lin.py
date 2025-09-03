from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LinCls:
	"""Lin commands group definition. 11 total commands, 0 Subgroups, 11 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("lin", core, parent)

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.SbusLinTriggerType:
		"""TRIGger:SBHW:LIN:TYPE \n
		Snippet: value: enums.SbusLinTriggerType = driver.trigger.sbhw.lin.get_type_py() \n
		Selects the trigger type for LIN analysis. \n
			:return: type_py:
				- STARtframe: Start of the frame. Triggers on the stop bit of the sync field.
				- ID: Sets the trigger to one specific identifier or an identifier range.
				- IDDT: Combination of identifier and data conditions.
				- WKFR: Wake-up frame.
				- ERRC: Error condition. Define the error types with:TRIGger:SBHW:LIN:CHKSerrorTRIGger:SBHW:LIN:IPERrorTRIGger:SBHW:LIN:SYERror"""
		response = self._core.io.query_str('TRIGger:SBHW:LIN:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusLinTriggerType)

	def set_type_py(self, type_py: enums.SbusLinTriggerType) -> None:
		"""TRIGger:SBHW:LIN:TYPE \n
		Snippet: driver.trigger.sbhw.lin.set_type_py(type_py = enums.SbusLinTriggerType.ERRC) \n
		Selects the trigger type for LIN analysis. \n
			:param type_py:
				- STARtframe: Start of the frame. Triggers on the stop bit of the sync field.
				- ID: Sets the trigger to one specific identifier or an identifier range.
				- IDDT: Combination of identifier and data conditions.
				- WKFR: Wake-up frame.
				- ERRC: Error condition. Define the error types with:TRIGger:SBHW:LIN:CHKSerrorTRIGger:SBHW:LIN:IPERrorTRIGger:SBHW:LIN:SYERror"""
		param = Conversions.enum_scalar_to_str(type_py, enums.SbusLinTriggerType)
		self._core.io.write(f'TRIGger:SBHW:LIN:TYPE {param}')

	# noinspection PyTypeChecker
	def get_icondition(self) -> enums.OperatorB:
		"""TRIGger:SBHW:LIN:ICONdition \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.lin.get_icondition() \n
		Sets the operator to set a specific identifier or an identifier range. \n
			:return: id_operator:
				- EQUal | NEQual | LTHan | LETHan | GTHan | GETHan: Equal, not equal, less than, less or equal than, greater than, greater or equal than. These conditions require one identifier pattern to be set with TRIGger:SBHW:LIN:IMIN.
				- INRange | OORange: In range / out of range: Set the minimum and maximum value of the range with TRIGger:SBHW:LIN:IMIN and TRIGger:SBHW:LIN:IMAX."""
		response = self._core.io.query_str('TRIGger:SBHW:LIN:ICONdition?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_icondition(self, id_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:LIN:ICONdition \n
		Snippet: driver.trigger.sbhw.lin.set_icondition(id_operator = enums.OperatorB.EQUal) \n
		Sets the operator to set a specific identifier or an identifier range. \n
			:param id_operator:
				- EQUal | NEQual | LTHan | LETHan | GTHan | GETHan: Equal, not equal, less than, less or equal than, greater than, greater or equal than. These conditions require one identifier pattern to be set with TRIGger:SBHW:LIN:IMIN.
				- INRange | OORange: In range / out of range: Set the minimum and maximum value of the range with TRIGger:SBHW:LIN:IMIN and TRIGger:SBHW:LIN:IMAX."""
		param = Conversions.enum_scalar_to_str(id_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:LIN:ICONdition {param}')

	def get_imin(self) -> List[int]:
		"""TRIGger:SBHW:LIN:IMIN \n
		Snippet: value: List[int] = driver.trigger.sbhw.lin.get_imin() \n
		Specifies a secondary identifier pattern, or sets the start value of an identifier range. \n
			:return: id_pattern: No help available
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:LIN:IMIN?')
		return response

	def set_imin(self, id_pattern: List[int]) -> None:
		"""TRIGger:SBHW:LIN:IMIN \n
		Snippet: driver.trigger.sbhw.lin.set_imin(id_pattern = [1, 2, 3]) \n
		Specifies a secondary identifier pattern, or sets the start value of an identifier range. \n
			:param id_pattern: No help available
		"""
		param = Conversions.list_to_csv_str(id_pattern)
		self._core.io.write(f'TRIGger:SBHW:LIN:IMIN {param}')

	def get_imax(self) -> List[int]:
		"""TRIGger:SBHW:LIN:IMAX \n
		Snippet: value: List[int] = driver.trigger.sbhw.lin.get_imax() \n
		Sets the end value of an identifier range if method RsMxo.Trigger.Sbhw.Lin.icondition is set to INRange or OORange. \n
			:return: id_pattern: No help available
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:LIN:IMAX?')
		return response

	def set_imax(self, id_pattern: List[int]) -> None:
		"""TRIGger:SBHW:LIN:IMAX \n
		Snippet: driver.trigger.sbhw.lin.set_imax(id_pattern = [1, 2, 3]) \n
		Sets the end value of an identifier range if method RsMxo.Trigger.Sbhw.Lin.icondition is set to INRange or OORange. \n
			:param id_pattern: No help available
		"""
		param = Conversions.list_to_csv_str(id_pattern)
		self._core.io.write(f'TRIGger:SBHW:LIN:IMAX {param}')

	# noinspection PyTypeChecker
	def get_dcondition(self) -> enums.OperatorB:
		"""TRIGger:SBHW:LIN:DCONdition \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.lin.get_dcondition() \n
		Sets the operator to set a specific data pattern or a data pattern range. \n
			:return: data_operator: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:LIN:DCONdition?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_dcondition(self, data_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:LIN:DCONdition \n
		Snippet: driver.trigger.sbhw.lin.set_dcondition(data_operator = enums.OperatorB.EQUal) \n
		Sets the operator to set a specific data pattern or a data pattern range. \n
			:param data_operator: No help available
		"""
		param = Conversions.enum_scalar_to_str(data_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:LIN:DCONdition {param}')

	def get_dmin(self) -> List[int]:
		"""TRIGger:SBHW:LIN:DMIN \n
		Snippet: value: List[int] = driver.trigger.sbhw.lin.get_dmin() \n
		Specifies a data pattern, or sets the start value of a data pattern range. \n
			:return: data_pattern: No help available
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:LIN:DMIN?')
		return response

	def set_dmin(self, data_pattern: List[int]) -> None:
		"""TRIGger:SBHW:LIN:DMIN \n
		Snippet: driver.trigger.sbhw.lin.set_dmin(data_pattern = [1, 2, 3]) \n
		Specifies a data pattern, or sets the start value of a data pattern range. \n
			:param data_pattern: No help available
		"""
		param = Conversions.list_to_csv_str(data_pattern)
		self._core.io.write(f'TRIGger:SBHW:LIN:DMIN {param}')

	def get_chks_error(self) -> bool:
		"""TRIGger:SBHW:LIN:CHKSerror \n
		Snippet: value: bool = driver.trigger.sbhw.lin.get_chks_error() \n
		Triggers on checksum errors. Available, if method RsMxo.Trigger.Sbhw.Lin.typePy is set to ERRC. \n
			:return: checksum_error: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:LIN:CHKSerror?')
		return Conversions.str_to_bool(response)

	def set_chks_error(self, checksum_error: bool) -> None:
		"""TRIGger:SBHW:LIN:CHKSerror \n
		Snippet: driver.trigger.sbhw.lin.set_chks_error(checksum_error = False) \n
		Triggers on checksum errors. Available, if method RsMxo.Trigger.Sbhw.Lin.typePy is set to ERRC. \n
			:param checksum_error: No help available
		"""
		param = Conversions.bool_to_str(checksum_error)
		self._core.io.write(f'TRIGger:SBHW:LIN:CHKSerror {param}')

	def get_ip_error(self) -> bool:
		"""TRIGger:SBHW:LIN:IPERror \n
		Snippet: value: bool = driver.trigger.sbhw.lin.get_ip_error() \n
		Triggers if an error occurs in the identifier parity bits. The parity bits are the bits 6 and 7 of the identifier.
		Available, if method RsMxo.Trigger.Sbhw.Lin.typePy is set to ERRC. \n
			:return: id_parity_error: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:LIN:IPERror?')
		return Conversions.str_to_bool(response)

	def set_ip_error(self, id_parity_error: bool) -> None:
		"""TRIGger:SBHW:LIN:IPERror \n
		Snippet: driver.trigger.sbhw.lin.set_ip_error(id_parity_error = False) \n
		Triggers if an error occurs in the identifier parity bits. The parity bits are the bits 6 and 7 of the identifier.
		Available, if method RsMxo.Trigger.Sbhw.Lin.typePy is set to ERRC. \n
			:param id_parity_error: No help available
		"""
		param = Conversions.bool_to_str(id_parity_error)
		self._core.io.write(f'TRIGger:SBHW:LIN:IPERror {param}')

	def get_sy_error(self) -> bool:
		"""TRIGger:SBHW:LIN:SYERror \n
		Snippet: value: bool = driver.trigger.sbhw.lin.get_sy_error() \n
		Triggers if a synchronization error occurs. Available, if method RsMxo.Trigger.Sbhw.Lin.typePy is set to ERRC. \n
			:return: sync_error: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:LIN:SYERror?')
		return Conversions.str_to_bool(response)

	def set_sy_error(self, sync_error: bool) -> None:
		"""TRIGger:SBHW:LIN:SYERror \n
		Snippet: driver.trigger.sbhw.lin.set_sy_error(sync_error = False) \n
		Triggers if a synchronization error occurs. Available, if method RsMxo.Trigger.Sbhw.Lin.typePy is set to ERRC. \n
			:param sync_error: No help available
		"""
		param = Conversions.bool_to_str(sync_error)
		self._core.io.write(f'TRIGger:SBHW:LIN:SYERror {param}')

	def get_dposition(self) -> int:
		"""TRIGger:SBHW:LIN:DPOSition \n
		Snippet: value: int = driver.trigger.sbhw.lin.get_dposition() \n
		Sets the number of data events that are ignored, before trigger condition check of the data starts. \n
			:return: data_position: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:LIN:DPOSition?')
		return Conversions.str_to_int(response)

	def set_dposition(self, data_position: int) -> None:
		"""TRIGger:SBHW:LIN:DPOSition \n
		Snippet: driver.trigger.sbhw.lin.set_dposition(data_position = 1) \n
		Sets the number of data events that are ignored, before trigger condition check of the data starts. \n
			:param data_position: No help available
		"""
		param = Conversions.decimal_value_to_str(data_position)
		self._core.io.write(f'TRIGger:SBHW:LIN:DPOSition {param}')

	def get_dlength(self) -> int:
		"""TRIGger:SBHW:LIN:DLENgth \n
		Snippet: value: int = driver.trigger.sbhw.lin.get_dlength() \n
		No command help available \n
			:return: data_length: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:LIN:DLENgth?')
		return Conversions.str_to_int(response)

	def set_dlength(self, data_length: int) -> None:
		"""TRIGger:SBHW:LIN:DLENgth \n
		Snippet: driver.trigger.sbhw.lin.set_dlength(data_length = 1) \n
		No command help available \n
			:param data_length: No help available
		"""
		param = Conversions.decimal_value_to_str(data_length)
		self._core.io.write(f'TRIGger:SBHW:LIN:DLENgth {param}')
