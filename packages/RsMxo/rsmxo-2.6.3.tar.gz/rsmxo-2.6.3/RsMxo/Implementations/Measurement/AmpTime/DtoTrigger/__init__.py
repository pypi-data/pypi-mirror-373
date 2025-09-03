from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DtoTriggerCls:
	"""DtoTrigger commands group definition. 1 total commands, 1 Subgroups, 0 group commands
	Repeated Capability: DtoTrigger, default value after init: DtoTrigger.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dtoTrigger", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_dtoTrigger_get', 'repcap_dtoTrigger_set', repcap.DtoTrigger.Nr1)

	def repcap_dtoTrigger_set(self, dtoTrigger: repcap.DtoTrigger) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to DtoTrigger.Default.
		Default value after init: DtoTrigger.Nr1"""
		self._cmd_group.set_repcap_enum_value(dtoTrigger)

	def repcap_dtoTrigger_get(self) -> repcap.DtoTrigger:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def slope(self):
		"""slope commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_slope'):
			from .Slope import SlopeCls
			self._slope = SlopeCls(self._core, self._cmd_group)
		return self._slope

	def clone(self) -> 'DtoTriggerCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = DtoTriggerCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
