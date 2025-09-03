from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SystemCls:
	"""System commands group definition. 12 total commands, 7 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("system", core, parent)

	@property
	def time(self):
		"""time commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_time'):
			from .Time import TimeCls
			self._time = TimeCls(self._core, self._cmd_group)
		return self._time

	@property
	def date(self):
		"""date commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_date'):
			from .Date import DateCls
			self._date = DateCls(self._core, self._cmd_group)
		return self._date

	@property
	def exit(self):
		"""exit commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_exit'):
			from .Exit import ExitCls
			self._exit = ExitCls(self._core, self._cmd_group)
		return self._exit

	@property
	def shutdown(self):
		"""shutdown commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_shutdown'):
			from .Shutdown import ShutdownCls
			self._shutdown = ShutdownCls(self._core, self._cmd_group)
		return self._shutdown

	@property
	def communicate(self):
		"""communicate commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_communicate'):
			from .Communicate import CommunicateCls
			self._communicate = CommunicateCls(self._core, self._cmd_group)
		return self._communicate

	@property
	def display(self):
		"""display commands group. 1 Sub-classes, 1 commands."""
		if not hasattr(self, '_display'):
			from .Display import DisplayCls
			self._display = DisplayCls(self._core, self._cmd_group)
		return self._display

	@property
	def fw(self):
		"""fw commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_fw'):
			from .Fw import FwCls
			self._fw = FwCls(self._core, self._cmd_group)
		return self._fw

	def preset(self, opc_timeout_ms: int = -1) -> None:
		"""SYSTem:PRESet \n
		Snippet: driver.system.preset() \n
		Resets the instrument to the default state, has the same effect as *RST. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SYSTem:PRESet', opc_timeout_ms)
		# OpcSyncAllowed = true

	def get_apup(self) -> bool:
		"""SYSTem:APUP \n
		Snippet: value: bool = driver.system.get_apup() \n
		If enabled, the instrument powers up automatically when it is connected to the mains voltage. \n
			:return: auto_power_up: No help available
		"""
		response = self._core.io.query_str('SYSTem:APUP?')
		return Conversions.str_to_bool(response)

	def set_apup(self, auto_power_up: bool) -> None:
		"""SYSTem:APUP \n
		Snippet: driver.system.set_apup(auto_power_up = False) \n
		If enabled, the instrument powers up automatically when it is connected to the mains voltage. \n
			:param auto_power_up: No help available
		"""
		param = Conversions.bool_to_str(auto_power_up)
		self._core.io.write(f'SYSTem:APUP {param}')

	def clone(self) -> 'SystemCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SystemCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
