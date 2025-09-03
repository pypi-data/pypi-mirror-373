from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FdataCls:
	"""Fdata commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fdata", core, parent)

	# noinspection PyTypeChecker
	def get_brs(self) -> enums.SbusBitState:
		"""TRIGger:SBHW:CAN:FDATa:BRS \n
		Snippet: value: enums.SbusBitState = driver.trigger.sbhw.can.fdata.get_brs() \n
		Sets the bit rate switch bit. \n
			:return: brs_bit: ONE: the bit rate switches from the bit rate of the arbitration phase to the faster data rate.
		"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:FDATa:BRS?')
		return Conversions.str_to_scalar_enum(response, enums.SbusBitState)

	def set_brs(self, brs_bit: enums.SbusBitState) -> None:
		"""TRIGger:SBHW:CAN:FDATa:BRS \n
		Snippet: driver.trigger.sbhw.can.fdata.set_brs(brs_bit = enums.SbusBitState.DC) \n
		Sets the bit rate switch bit. \n
			:param brs_bit: ONE: the bit rate switches from the bit rate of the arbitration phase to the faster data rate.
		"""
		param = Conversions.enum_scalar_to_str(brs_bit, enums.SbusBitState)
		self._core.io.write(f'TRIGger:SBHW:CAN:FDATa:BRS {param}')

	# noinspection PyTypeChecker
	def get_esi(self) -> enums.SbusBitState:
		"""TRIGger:SBHW:CAN:FDATa:ESI \n
		Snippet: value: enums.SbusBitState = driver.trigger.sbhw.can.fdata.get_esi() \n
		Sets the error state indicator bit. \n
			:return: esi_bit: DC: do not care, bit is nor relevant.
		"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:FDATa:ESI?')
		return Conversions.str_to_scalar_enum(response, enums.SbusBitState)

	def set_esi(self, esi_bit: enums.SbusBitState) -> None:
		"""TRIGger:SBHW:CAN:FDATa:ESI \n
		Snippet: driver.trigger.sbhw.can.fdata.set_esi(esi_bit = enums.SbusBitState.DC) \n
		Sets the error state indicator bit. \n
			:param esi_bit: DC: do not care, bit is nor relevant.
		"""
		param = Conversions.enum_scalar_to_str(esi_bit, enums.SbusBitState)
		self._core.io.write(f'TRIGger:SBHW:CAN:FDATa:ESI {param}')

	def get_dposition(self) -> int:
		"""TRIGger:SBHW:CAN:FDATa:DPOSition \n
		Snippet: value: int = driver.trigger.sbhw.can.fdata.get_dposition() \n
		Defines the number of the first data byte at which the data pattern may start. \n
			:return: data_position: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:FDATa:DPOSition?')
		return Conversions.str_to_int(response)

	def set_dposition(self, data_position: int) -> None:
		"""TRIGger:SBHW:CAN:FDATa:DPOSition \n
		Snippet: driver.trigger.sbhw.can.fdata.set_dposition(data_position = 1) \n
		Defines the number of the first data byte at which the data pattern may start. \n
			:param data_position: No help available
		"""
		param = Conversions.decimal_value_to_str(data_position)
		self._core.io.write(f'TRIGger:SBHW:CAN:FDATa:DPOSition {param}')

	def get_sc_error(self) -> bool:
		"""TRIGger:SBHW:CAN:FDATa:SCERror \n
		Snippet: value: bool = driver.trigger.sbhw.can.fdata.get_sc_error() \n
		Triggers on stuff count errors. A stuff bit error occurs if more than five consecutive bits of the same level occur on
		the bus. Available, if method RsMxo.Trigger.Sbhw.Can.typePy is set to ERRor. \n
			:return: stuff_cnt_err: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:FDATa:SCERror?')
		return Conversions.str_to_bool(response)

	def set_sc_error(self, stuff_cnt_err: bool) -> None:
		"""TRIGger:SBHW:CAN:FDATa:SCERror \n
		Snippet: driver.trigger.sbhw.can.fdata.set_sc_error(stuff_cnt_err = False) \n
		Triggers on stuff count errors. A stuff bit error occurs if more than five consecutive bits of the same level occur on
		the bus. Available, if method RsMxo.Trigger.Sbhw.Can.typePy is set to ERRor. \n
			:param stuff_cnt_err: No help available
		"""
		param = Conversions.bool_to_str(stuff_cnt_err)
		self._core.io.write(f'TRIGger:SBHW:CAN:FDATa:SCERror {param}')
