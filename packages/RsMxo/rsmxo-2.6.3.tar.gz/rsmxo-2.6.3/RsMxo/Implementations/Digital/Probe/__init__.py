from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ProbeCls:
	"""Probe commands group definition. 1 total commands, 1 Subgroups, 0 group commands
	Repeated Capability: ProbeDigital, default value after init: ProbeDigital.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("probe", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_probeDigital_get', 'repcap_probeDigital_set', repcap.ProbeDigital.Nr1)

	def repcap_probeDigital_set(self, probeDigital: repcap.ProbeDigital) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to ProbeDigital.Default.
		Default value after init: ProbeDigital.Nr1"""
		self._cmd_group.set_repcap_enum_value(probeDigital)

	def repcap_probeDigital_get(self) -> repcap.ProbeDigital:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def enable(self):
		"""enable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_enable'):
			from .Enable import EnableCls
			self._enable = EnableCls(self._core, self._cmd_group)
		return self._enable

	def clone(self) -> 'ProbeCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ProbeCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
