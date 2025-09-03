from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SequenceCls:
	"""Sequence commands group definition. 5 total commands, 3 Subgroups, 0 group commands
	Repeated Capability: Sequence, default value after init: Sequence.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sequence", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_sequence_get', 'repcap_sequence_set', repcap.Sequence.Nr1)

	def repcap_sequence_set(self, sequence: repcap.Sequence) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Sequence.Default.
		Default value after init: Sequence.Nr1"""
		self._cmd_group.set_repcap_enum_value(sequence)

	def repcap_sequence_get(self) -> repcap.Sequence:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def count(self):
		"""count commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_count'):
			from .Count import CountCls
			self._count = CountCls(self._core, self._cmd_group)
		return self._count

	@property
	def delay(self):
		"""delay commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_delay'):
			from .Delay import DelayCls
			self._delay = DelayCls(self._core, self._cmd_group)
		return self._delay

	@property
	def reset(self):
		"""reset commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_reset'):
			from .Reset import ResetCls
			self._reset = ResetCls(self._core, self._cmd_group)
		return self._reset

	def clone(self) -> 'SequenceCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SequenceCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
