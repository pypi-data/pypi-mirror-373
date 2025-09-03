from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StatusCls:
	"""Status commands group definition. 5 total commands, 0 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("status", core, parent)

	def get_condition(self) -> bool:
		"""TRIGger:ANEDge:OVERload:STATus:CONDition \n
		Snippet: value: bool = driver.trigger.anEdge.overload.status.get_condition() \n
		Returns the contents of the CONDition part of the status register to check for questionable instrument or measurement
		states. This part contains information on the action currently being performed in the instrument. Reading the CONDition
		registers does not delete the contents since it indicates the current hardware status. \n
			:return: value: No help available
		"""
		response = self._core.io.query_str('TRIGger:ANEDge:OVERload:STATus:CONDition?')
		return Conversions.str_to_bool(response)

	def get_enable(self) -> bool:
		"""TRIGger:ANEDge:OVERload:STATus:ENABle \n
		Snippet: value: bool = driver.trigger.anEdge.overload.status.get_enable() \n
		Sets the ENABle part that allows true conditions in the EVENt part to be reported for the summary bit in the status byte.
		These events can be used for a service request. If a bit in the ENABle part is 1, and the corresponding EVENt bit is true,
		a positive transition occurs in the summary bit. This transition is reported to the next higher level. See Table 'Source
		values for STATus:QUEStionable:...:[:EVENt] and STATus:QUEStionable:...:[:ENABLe]' for a list of the return values. \n
			:return: value: No help available
		"""
		response = self._core.io.query_str('TRIGger:ANEDge:OVERload:STATus:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, value: bool) -> None:
		"""TRIGger:ANEDge:OVERload:STATus:ENABle \n
		Snippet: driver.trigger.anEdge.overload.status.set_enable(value = False) \n
		Sets the ENABle part that allows true conditions in the EVENt part to be reported for the summary bit in the status byte.
		These events can be used for a service request. If a bit in the ENABle part is 1, and the corresponding EVENt bit is true,
		a positive transition occurs in the summary bit. This transition is reported to the next higher level. See Table 'Source
		values for STATus:QUEStionable:...:[:EVENt] and STATus:QUEStionable:...:[:ENABLe]' for a list of the return values. \n
			:param value: No help available
		"""
		param = Conversions.bool_to_str(value)
		self._core.io.write(f'TRIGger:ANEDge:OVERload:STATus:ENABle {param}')

	def get_event(self) -> bool:
		"""TRIGger:ANEDge:OVERload:STATus[:EVENt] \n
		Snippet: value: bool = driver.trigger.anEdge.overload.status.get_event() \n
		Returns the contents of the EVENt part of the status register to check if an event has occurred since the last reading.
		Reading an EVENt register deletes its contents. \n
			:return: value: No help available
		"""
		response = self._core.io.query_str('TRIGger:ANEDge:OVERload:STATus:EVENt?')
		return Conversions.str_to_bool(response)

	def set_event(self, value: bool) -> None:
		"""TRIGger:ANEDge:OVERload:STATus[:EVENt] \n
		Snippet: driver.trigger.anEdge.overload.status.set_event(value = False) \n
		Returns the contents of the EVENt part of the status register to check if an event has occurred since the last reading.
		Reading an EVENt register deletes its contents. \n
			:param value: No help available
		"""
		param = Conversions.bool_to_str(value)
		self._core.io.write(f'TRIGger:ANEDge:OVERload:STATus:EVENt {param}')

	def get_ntransition(self) -> bool:
		"""TRIGger:ANEDge:OVERload:STATus:NTRansition \n
		Snippet: value: bool = driver.trigger.anEdge.overload.status.get_ntransition() \n
		Sets the negative transition filter. If a bit is set, a transition from 1 to 0 in the condition part causes an entry to
		be made in the corresponding bit of the EVENt part of the register. \n
			:return: value: No help available
		"""
		response = self._core.io.query_str('TRIGger:ANEDge:OVERload:STATus:NTRansition?')
		return Conversions.str_to_bool(response)

	def set_ntransition(self, value: bool) -> None:
		"""TRIGger:ANEDge:OVERload:STATus:NTRansition \n
		Snippet: driver.trigger.anEdge.overload.status.set_ntransition(value = False) \n
		Sets the negative transition filter. If a bit is set, a transition from 1 to 0 in the condition part causes an entry to
		be made in the corresponding bit of the EVENt part of the register. \n
			:param value: No help available
		"""
		param = Conversions.bool_to_str(value)
		self._core.io.write(f'TRIGger:ANEDge:OVERload:STATus:NTRansition {param}')

	def get_ptransition(self) -> bool:
		"""TRIGger:ANEDge:OVERload:STATus:PTRansition \n
		Snippet: value: bool = driver.trigger.anEdge.overload.status.get_ptransition() \n
		Sets the positive transition filter. If a bit is set, a transition from 0 to 1 in the condition part causes an entry to
		be made in the corresponding bit of the EVENt part of the register. \n
			:return: value: No help available
		"""
		response = self._core.io.query_str('TRIGger:ANEDge:OVERload:STATus:PTRansition?')
		return Conversions.str_to_bool(response)

	def set_ptransition(self, value: bool) -> None:
		"""TRIGger:ANEDge:OVERload:STATus:PTRansition \n
		Snippet: driver.trigger.anEdge.overload.status.set_ptransition(value = False) \n
		Sets the positive transition filter. If a bit is set, a transition from 0 to 1 in the condition part causes an entry to
		be made in the corresponding bit of the EVENt part of the register. \n
			:param value: No help available
		"""
		param = Conversions.bool_to_str(value)
		self._core.io.write(f'TRIGger:ANEDge:OVERload:STATus:PTRansition {param}')
