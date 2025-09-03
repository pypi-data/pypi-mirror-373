from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SbhwCls:
	"""Sbhw commands group definition. 63 total commands, 5 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sbhw", core, parent)

	@property
	def can(self):
		"""can commands group. 2 Sub-classes, 15 commands."""
		if not hasattr(self, '_can'):
			from .Can import CanCls
			self._can = CanCls(self._core, self._cmd_group)
		return self._can

	@property
	def i2C(self):
		"""i2C commands group. 0 Sub-classes, 12 commands."""
		if not hasattr(self, '_i2C'):
			from .I2C import I2CCls
			self._i2C = I2CCls(self._core, self._cmd_group)
		return self._i2C

	@property
	def lin(self):
		"""lin commands group. 0 Sub-classes, 11 commands."""
		if not hasattr(self, '_lin'):
			from .Lin import LinCls
			self._lin = LinCls(self._core, self._cmd_group)
		return self._lin

	@property
	def spi(self):
		"""spi commands group. 0 Sub-classes, 5 commands."""
		if not hasattr(self, '_spi'):
			from .Spi import SpiCls
			self._spi = SpiCls(self._core, self._cmd_group)
		return self._spi

	@property
	def uart(self):
		"""uart commands group. 0 Sub-classes, 6 commands."""
		if not hasattr(self, '_uart'):
			from .Uart import UartCls
			self._uart = UartCls(self._core, self._cmd_group)
		return self._uart

	def clone(self) -> 'SbhwCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SbhwCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
