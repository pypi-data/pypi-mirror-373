from typing import List

from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CanCls:
	"""Can commands group definition. 29 total commands, 2 Subgroups, 15 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("can", core, parent)

	@property
	def fdata(self):
		"""fdata commands group. 0 Sub-classes, 4 commands."""
		if not hasattr(self, '_fdata'):
			from .Fdata import FdataCls
			self._fdata = FdataCls(self._core, self._cmd_group)
		return self._fdata

	@property
	def xdata(self):
		"""xdata commands group. 3 Sub-classes, 1 commands."""
		if not hasattr(self, '_xdata'):
			from .Xdata import XdataCls
			self._xdata = XdataCls(self._core, self._cmd_group)
		return self._xdata

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.SbusCanTriggerType:
		"""TRIGger:SBHW:CAN:TYPE \n
		Snippet: value: enums.SbusCanTriggerType = driver.trigger.sbhw.can.get_type_py() \n
		Selects the trigger type for CAN analysis. \n
			:return: type_py:
				- STOF: STart of Frame: triggers on the first edge of the dominant SOF bit (synchronization bit) .
				- FTYP: Frame type: triggers on a specified frame type and on the identifier format.
				- ID: Identifier: Sets the trigger to one specific identifier or an identifier range.To set the identifier, use TRIGger:SBHW:CAN:ICONdition, TRIGger:SBHW:CAN:IMAX, and TRIGger:SBHW:CAN:IMIN.
				- IDDT: Identifier and data: Combination of identifier and data conditions. To set the identifier condition, use TRIGger:SBHW:CAN:ICONdition, TRIGger:SBHW:CAN:IMIN, and TRIGger:SBHW:CAN:IMAX.To set the data condition, use TRIGger:SBHW:CAN:DCONdition and TRIGger:SBHW:CAN:DMIN.
				- ERRC: Error condition: Define the error types with:TRIGger:SBHW:CAN:ACKerrorTRIGger:SBHW:CAN:BITSterrorTRIGger:SBHW:CAN:CRCerrorTRIGger:SBHW:CAN:FORMerrorTRIGger:SBHW:CAN:FDATa:SCERror"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SbusCanTriggerType)

	def set_type_py(self, type_py: enums.SbusCanTriggerType) -> None:
		"""TRIGger:SBHW:CAN:TYPE \n
		Snippet: driver.trigger.sbhw.can.set_type_py(type_py = enums.SbusCanTriggerType.EDOF) \n
		Selects the trigger type for CAN analysis. \n
			:param type_py:
				- STOF: STart of Frame: triggers on the first edge of the dominant SOF bit (synchronization bit) .
				- FTYP: Frame type: triggers on a specified frame type and on the identifier format.
				- ID: Identifier: Sets the trigger to one specific identifier or an identifier range.To set the identifier, use TRIGger:SBHW:CAN:ICONdition, TRIGger:SBHW:CAN:IMAX, and TRIGger:SBHW:CAN:IMIN.
				- IDDT: Identifier and data: Combination of identifier and data conditions. To set the identifier condition, use TRIGger:SBHW:CAN:ICONdition, TRIGger:SBHW:CAN:IMIN, and TRIGger:SBHW:CAN:IMAX.To set the data condition, use TRIGger:SBHW:CAN:DCONdition and TRIGger:SBHW:CAN:DMIN.
				- ERRC: Error condition: Define the error types with:TRIGger:SBHW:CAN:ACKerrorTRIGger:SBHW:CAN:BITSterrorTRIGger:SBHW:CAN:CRCerrorTRIGger:SBHW:CAN:FORMerrorTRIGger:SBHW:CAN:FDATa:SCERror"""
		param = Conversions.enum_scalar_to_str(type_py, enums.SbusCanTriggerType)
		self._core.io.write(f'TRIGger:SBHW:CAN:TYPE {param}')

	# noinspection PyTypeChecker
	def get_ftype(self) -> enums.SbusCanFrameType:
		"""TRIGger:SBHW:CAN:FTYPe \n
		Snippet: value: enums.SbusCanFrameType = driver.trigger.sbhw.can.get_ftype() \n
		Sets the CAN frame type. \n
			:return: frame_type: CBFF: classical base frame format data CBFR: classical base frame format remote CEFF: classical extended frame format data CEFR: classical extended frame format remote FBFF: FD base frame format FEFF: FD extended frame format XLFF: XL frame format ERR: error OVLD: overload
		"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:FTYPe?')
		return Conversions.str_to_scalar_enum(response, enums.SbusCanFrameType)

	def set_ftype(self, frame_type: enums.SbusCanFrameType) -> None:
		"""TRIGger:SBHW:CAN:FTYPe \n
		Snippet: driver.trigger.sbhw.can.set_ftype(frame_type = enums.SbusCanFrameType.CBFF) \n
		Sets the CAN frame type. \n
			:param frame_type: CBFF: classical base frame format data CBFR: classical base frame format remote CEFF: classical extended frame format data CEFR: classical extended frame format remote FBFF: FD base frame format FEFF: FD extended frame format XLFF: XL frame format ERR: error OVLD: overload
		"""
		param = Conversions.enum_scalar_to_str(frame_type, enums.SbusCanFrameType)
		self._core.io.write(f'TRIGger:SBHW:CAN:FTYPe {param}')

	# noinspection PyTypeChecker
	def get_itype(self) -> enums.SbusCanIdentifierType:
		"""TRIGger:SBHW:CAN:ITYPe \n
		Snippet: value: enums.SbusCanIdentifierType = driver.trigger.sbhw.can.get_itype() \n
		Selects the format of data and remote frames. Remote frames are not available in the CAN FD protocol. \n
			:return: identifier_type:
				- B11: 11-bit identifier (standard format) . The instrument triggers on the sample point of the IDE bit.
				- B29: 29-bit identifier (extended format) . The instrument triggers on the sample point of the RTR bit."""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:ITYPe?')
		return Conversions.str_to_scalar_enum(response, enums.SbusCanIdentifierType)

	def set_itype(self, identifier_type: enums.SbusCanIdentifierType) -> None:
		"""TRIGger:SBHW:CAN:ITYPe \n
		Snippet: driver.trigger.sbhw.can.set_itype(identifier_type = enums.SbusCanIdentifierType.B11) \n
		Selects the format of data and remote frames. Remote frames are not available in the CAN FD protocol. \n
			:param identifier_type:
				- B11: 11-bit identifier (standard format) . The instrument triggers on the sample point of the IDE bit.
				- B29: 29-bit identifier (extended format) . The instrument triggers on the sample point of the RTR bit."""
		param = Conversions.enum_scalar_to_str(identifier_type, enums.SbusCanIdentifierType)
		self._core.io.write(f'TRIGger:SBHW:CAN:ITYPe {param}')

	# noinspection PyTypeChecker
	def get_icondition(self) -> enums.OperatorB:
		"""TRIGger:SBHW:CAN:ICONdition \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.can.get_icondition() \n
		Sets the operator to set a specific identifier or an identifier range. \n
			:return: id_operator:
				- EQUal | NEQual | LTHan | LETHan | GTHan | GETHan: Equal, not equal, less than, less or equal than, greater than, greater or equal than. These conditions require one identifier pattern to be set with TRIGger:SBHW:CAN:IMIN.
				- INRange | OORange: In range / out of range: Set the minimum and maximum value of the range with TRIGger:SBHW:CAN:IMIN and TRIGger:SBHW:CAN:IMAX."""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:ICONdition?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_icondition(self, id_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:CAN:ICONdition \n
		Snippet: driver.trigger.sbhw.can.set_icondition(id_operator = enums.OperatorB.EQUal) \n
		Sets the operator to set a specific identifier or an identifier range. \n
			:param id_operator:
				- EQUal | NEQual | LTHan | LETHan | GTHan | GETHan: Equal, not equal, less than, less or equal than, greater than, greater or equal than. These conditions require one identifier pattern to be set with TRIGger:SBHW:CAN:IMIN.
				- INRange | OORange: In range / out of range: Set the minimum and maximum value of the range with TRIGger:SBHW:CAN:IMIN and TRIGger:SBHW:CAN:IMAX."""
		param = Conversions.enum_scalar_to_str(id_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:CAN:ICONdition {param}')

	def get_imin(self) -> List[int]:
		"""TRIGger:SBHW:CAN:IMIN \n
		Snippet: value: List[int] = driver.trigger.sbhw.can.get_imin() \n
		Specifies a message identifier pattern, or sets the start value of an identifier range. \n
			:return: id_pattern: No help available
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:CAN:IMIN?')
		return response

	def set_imin(self, id_pattern: List[int]) -> None:
		"""TRIGger:SBHW:CAN:IMIN \n
		Snippet: driver.trigger.sbhw.can.set_imin(id_pattern = [1, 2, 3]) \n
		Specifies a message identifier pattern, or sets the start value of an identifier range. \n
			:param id_pattern: No help available
		"""
		param = Conversions.list_to_csv_str(id_pattern)
		self._core.io.write(f'TRIGger:SBHW:CAN:IMIN {param}')

	def get_imax(self) -> List[int]:
		"""TRIGger:SBHW:CAN:IMAX \n
		Snippet: value: List[int] = driver.trigger.sbhw.can.get_imax() \n
		Sets the end value of an identifier range if method RsMxo.Trigger.Sbhw.Can.icondition is set to INRange or OORange. \n
			:return: id_pattern: List of comma separated values
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:CAN:IMAX?')
		return response

	def set_imax(self, id_pattern: List[int]) -> None:
		"""TRIGger:SBHW:CAN:IMAX \n
		Snippet: driver.trigger.sbhw.can.set_imax(id_pattern = [1, 2, 3]) \n
		Sets the end value of an identifier range if method RsMxo.Trigger.Sbhw.Can.icondition is set to INRange or OORange. \n
			:param id_pattern: List of comma separated values
		"""
		param = Conversions.list_to_csv_str(id_pattern)
		self._core.io.write(f'TRIGger:SBHW:CAN:IMAX {param}')

	# noinspection PyTypeChecker
	def get_dcondition(self) -> enums.OperatorB:
		"""TRIGger:SBHW:CAN:DCONdition \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.can.get_dcondition() \n
		Sets the operator to set a specific data pattern or a data pattern range. \n
			:return: data_operator:
				- EQUal | NEQual | LTHan | LETHan | GTHan | GETHan: Equal, not equal, less than, less or equal than, greater than, greater or equal than. These conditions require one data pattern to be set with TRIGger:SBHW:CAN:DMIN."""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:DCONdition?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_dcondition(self, data_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:CAN:DCONdition \n
		Snippet: driver.trigger.sbhw.can.set_dcondition(data_operator = enums.OperatorB.EQUal) \n
		Sets the operator to set a specific data pattern or a data pattern range. \n
			:param data_operator:
				- EQUal | NEQual | LTHan | LETHan | GTHan | GETHan: Equal, not equal, less than, less or equal than, greater than, greater or equal than. These conditions require one data pattern to be set with TRIGger:SBHW:CAN:DMIN."""
		param = Conversions.enum_scalar_to_str(data_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:CAN:DCONdition {param}')

	def get_dmin(self) -> List[int]:
		"""TRIGger:SBHW:CAN:DMIN \n
		Snippet: value: List[int] = driver.trigger.sbhw.can.get_dmin() \n
		Sets a data pattern, or sets the start value of a data pattern range. \n
			:return: data_pattern: List of comma separated values
		"""
		response = self._core.io.query_bin_or_ascii_int_list('TRIGger:SBHW:CAN:DMIN?')
		return response

	def set_dmin(self, data_pattern: List[int]) -> None:
		"""TRIGger:SBHW:CAN:DMIN \n
		Snippet: driver.trigger.sbhw.can.set_dmin(data_pattern = [1, 2, 3]) \n
		Sets a data pattern, or sets the start value of a data pattern range. \n
			:param data_pattern: List of comma separated values
		"""
		param = Conversions.list_to_csv_str(data_pattern)
		self._core.io.write(f'TRIGger:SBHW:CAN:DMIN {param}')

	# noinspection PyTypeChecker
	def get_border(self) -> enums.Endianness:
		"""TRIGger:SBHW:CAN:BORDer \n
		Snippet: value: enums.Endianness = driver.trigger.sbhw.can.get_border() \n
		Sets the byte order (endianness) of the data transfer. Only for CAN protocol. \n
			:return: endianness:
				- BENDian: Big endian, data is analyzed and evaluated in the order of reception.
				- LENDian: Little endian, the instrument reads the complete data, reverses the byte order of the data, and compares it with the specified data word."""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:BORDer?')
		return Conversions.str_to_scalar_enum(response, enums.Endianness)

	def set_border(self, endianness: enums.Endianness) -> None:
		"""TRIGger:SBHW:CAN:BORDer \n
		Snippet: driver.trigger.sbhw.can.set_border(endianness = enums.Endianness.BENDian) \n
		Sets the byte order (endianness) of the data transfer. Only for CAN protocol. \n
			:param endianness:
				- BENDian: Big endian, data is analyzed and evaluated in the order of reception.
				- LENDian: Little endian, the instrument reads the complete data, reverses the byte order of the data, and compares it with the specified data word."""
		param = Conversions.enum_scalar_to_str(endianness, enums.Endianness)
		self._core.io.write(f'TRIGger:SBHW:CAN:BORDer {param}')

	def get_crc_error(self) -> bool:
		"""TRIGger:SBHW:CAN:CRCerror \n
		Snippet: value: bool = driver.trigger.sbhw.can.get_crc_error() \n
		Triggers on CRC errors. A CRC error occurs when the CRC calculated by the receiver differs from the received value in the
		CRC sequence. Available, if method RsMxo.Trigger.Sbhw.Can.typePy is set to ERRC. \n
			:return: checksum_error: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:CRCerror?')
		return Conversions.str_to_bool(response)

	def set_crc_error(self, checksum_error: bool) -> None:
		"""TRIGger:SBHW:CAN:CRCerror \n
		Snippet: driver.trigger.sbhw.can.set_crc_error(checksum_error = False) \n
		Triggers on CRC errors. A CRC error occurs when the CRC calculated by the receiver differs from the received value in the
		CRC sequence. Available, if method RsMxo.Trigger.Sbhw.Can.typePy is set to ERRC. \n
			:param checksum_error: No help available
		"""
		param = Conversions.bool_to_str(checksum_error)
		self._core.io.write(f'TRIGger:SBHW:CAN:CRCerror {param}')

	def get_bitst_error(self) -> bool:
		"""TRIGger:SBHW:CAN:BITSterror \n
		Snippet: value: bool = driver.trigger.sbhw.can.get_bitst_error() \n
		Triggers if a stuff error occurs - when the 6th consecutive equal bit level in the mentioned fields is detected.
		Available, if method RsMxo.Trigger.Sbhw.Can.typePy is set to ERRC. \n
			:return: bit_stuff_error: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:BITSterror?')
		return Conversions.str_to_bool(response)

	def set_bitst_error(self, bit_stuff_error: bool) -> None:
		"""TRIGger:SBHW:CAN:BITSterror \n
		Snippet: driver.trigger.sbhw.can.set_bitst_error(bit_stuff_error = False) \n
		Triggers if a stuff error occurs - when the 6th consecutive equal bit level in the mentioned fields is detected.
		Available, if method RsMxo.Trigger.Sbhw.Can.typePy is set to ERRC. \n
			:param bit_stuff_error: No help available
		"""
		param = Conversions.bool_to_str(bit_stuff_error)
		self._core.io.write(f'TRIGger:SBHW:CAN:BITSterror {param}')

	def get_form_error(self) -> bool:
		"""TRIGger:SBHW:CAN:FORMerror \n
		Snippet: value: bool = driver.trigger.sbhw.can.get_form_error() \n
		Triggers when a fixed-form bit field contains one or more illegal bits. Available, if method RsMxo.Trigger.Sbhw.Can.
		typePy is set to ERRC. \n
			:return: form_error: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:FORMerror?')
		return Conversions.str_to_bool(response)

	def set_form_error(self, form_error: bool) -> None:
		"""TRIGger:SBHW:CAN:FORMerror \n
		Snippet: driver.trigger.sbhw.can.set_form_error(form_error = False) \n
		Triggers when a fixed-form bit field contains one or more illegal bits. Available, if method RsMxo.Trigger.Sbhw.Can.
		typePy is set to ERRC. \n
			:param form_error: No help available
		"""
		param = Conversions.bool_to_str(form_error)
		self._core.io.write(f'TRIGger:SBHW:CAN:FORMerror {param}')

	def get_ack_error(self) -> bool:
		"""TRIGger:SBHW:CAN:ACKerror \n
		Snippet: value: bool = driver.trigger.sbhw.can.get_ack_error() \n
		Triggers when the transmitter does not receive an acknowledgment - a dominant bit during the ACK Slot. Available, if
		method RsMxo.Trigger.Sbhw.Can.typePy is set to ERRC. \n
			:return: ack_error: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:ACKerror?')
		return Conversions.str_to_bool(response)

	def set_ack_error(self, ack_error: bool) -> None:
		"""TRIGger:SBHW:CAN:ACKerror \n
		Snippet: driver.trigger.sbhw.can.set_ack_error(ack_error = False) \n
		Triggers when the transmitter does not receive an acknowledgment - a dominant bit during the ACK Slot. Available, if
		method RsMxo.Trigger.Sbhw.Can.typePy is set to ERRC. \n
			:param ack_error: No help available
		"""
		param = Conversions.bool_to_str(ack_error)
		self._core.io.write(f'TRIGger:SBHW:CAN:ACKerror {param}')

	def get_dlc(self) -> int:
		"""TRIGger:SBHW:CAN:DLC \n
		Snippet: value: int = driver.trigger.sbhw.can.get_dlc() \n
		Sets the data length code, the number of data bytes to be found. For complete definition, set also the operator with
		method RsMxo.Trigger.Sbhw.Can.dlcCondition. \n
			:return: dlc: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:DLC?')
		return Conversions.str_to_int(response)

	def set_dlc(self, dlc: int) -> None:
		"""TRIGger:SBHW:CAN:DLC \n
		Snippet: driver.trigger.sbhw.can.set_dlc(dlc = 1) \n
		Sets the data length code, the number of data bytes to be found. For complete definition, set also the operator with
		method RsMxo.Trigger.Sbhw.Can.dlcCondition. \n
			:param dlc: No help available
		"""
		param = Conversions.decimal_value_to_str(dlc)
		self._core.io.write(f'TRIGger:SBHW:CAN:DLC {param}')

	# noinspection PyTypeChecker
	def get_dlc_condition(self) -> enums.OperatorB:
		"""TRIGger:SBHW:CAN:DLCCondition \n
		Snippet: value: enums.OperatorB = driver.trigger.sbhw.can.get_dlc_condition() \n
		Operator to set the data length code. The number of data bytes to be found is set with method RsMxo.Trigger.Sbhw.Can.dlc. \n
			:return: dlc_operator: For little endian transfer direction, EQUal must be set.
		"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:DLCCondition?')
		return Conversions.str_to_scalar_enum(response, enums.OperatorB)

	def set_dlc_condition(self, dlc_operator: enums.OperatorB) -> None:
		"""TRIGger:SBHW:CAN:DLCCondition \n
		Snippet: driver.trigger.sbhw.can.set_dlc_condition(dlc_operator = enums.OperatorB.EQUal) \n
		Operator to set the data length code. The number of data bytes to be found is set with method RsMxo.Trigger.Sbhw.Can.dlc. \n
			:param dlc_operator: For little endian transfer direction, EQUal must be set.
		"""
		param = Conversions.enum_scalar_to_str(dlc_operator, enums.OperatorB)
		self._core.io.write(f'TRIGger:SBHW:CAN:DLCCondition {param}')

	def clone(self) -> 'CanCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = CanCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
