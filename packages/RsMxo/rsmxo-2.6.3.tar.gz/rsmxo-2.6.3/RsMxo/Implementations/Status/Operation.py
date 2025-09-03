from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OperationCls:
	"""Operation commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("operation", core, parent)

	def get_event(self) -> int:
		"""STATus:OPERation[:EVENt] \n
		Snippet: value: int = driver.status.operation.get_event() \n
		The CONDition command returns information on actions the instrument is currently executing. The contents of the register
		is retained. The EVENt command returns information on actions the instrument has executed since the last reading. Reading
		the EVENt register deletes its contents.
			INTRO_CMD_HELP: Bits: \n
			- 0 = ALIGnment
			- 2 = AUToset
			- 4= MEASuring
			- 5= WTRIgger (wait for trigger)
			- 6= TRIggered  \n
			:return: value: No help available
		"""
		response = self._core.io.query_str('STATus:OPERation:EVENt?')
		return Conversions.str_to_int(response)

	def get_condition(self) -> str:
		"""STATus:OPERation:CONDition \n
		Snippet: value: str = driver.status.operation.get_condition() \n
		No command help available \n
			:return: value: No help available
		"""
		response = self._core.io.query_str('STATus:OPERation:CONDition?')
		return trim_str_response(response)

	def get_ptransition(self) -> int:
		"""STATus:OPERation:PTRansition \n
		Snippet: value: int = driver.status.operation.get_ptransition() \n
		The command sets the bits of the PTRansition part of the STATus:OPERation register. A bit set in the PTRansition register
		causes a bit transition from 0 to 1 in the CONDition register to produce an entry in the EVENt register. Reading the
		information does not clear the register. \n
			:return: value: No help available
		"""
		response = self._core.io.query_str('STATus:OPERation:PTRansition?')
		return Conversions.str_to_int(response)

	def set_ptransition(self, value: int) -> None:
		"""STATus:OPERation:PTRansition \n
		Snippet: driver.status.operation.set_ptransition(value = 1) \n
		The command sets the bits of the PTRansition part of the STATus:OPERation register. A bit set in the PTRansition register
		causes a bit transition from 0 to 1 in the CONDition register to produce an entry in the EVENt register. Reading the
		information does not clear the register. \n
			:param value: No help available
		"""
		param = Conversions.decimal_value_to_str(value)
		self._core.io.write(f'STATus:OPERation:PTRansition {param}')

	def get_ntransition(self) -> int:
		"""STATus:OPERation:NTRansition \n
		Snippet: value: int = driver.status.operation.get_ntransition() \n
		The command sets the bits of the NTRansition part of the STATus:OPERation register. A bit set in the NTRansition register
		causes a bit transition from 1 to 0 in the CONDition register to produce an entry in the EVENt register. Reading the
		information does not clear the register. \n
			:return: value: No help available
		"""
		response = self._core.io.query_str('STATus:OPERation:NTRansition?')
		return Conversions.str_to_int(response)

	def set_ntransition(self, value: int) -> None:
		"""STATus:OPERation:NTRansition \n
		Snippet: driver.status.operation.set_ntransition(value = 1) \n
		The command sets the bits of the NTRansition part of the STATus:OPERation register. A bit set in the NTRansition register
		causes a bit transition from 1 to 0 in the CONDition register to produce an entry in the EVENt register. Reading the
		information does not clear the register. \n
			:param value: No help available
		"""
		param = Conversions.decimal_value_to_str(value)
		self._core.io.write(f'STATus:OPERation:NTRansition {param}')
