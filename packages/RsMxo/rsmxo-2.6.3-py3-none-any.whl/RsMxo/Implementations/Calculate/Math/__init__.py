from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MathCls:
	"""Math commands group definition. 13 total commands, 8 Subgroups, 0 group commands
	Repeated Capability: Math, default value after init: Math.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("math", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_math_get', 'repcap_math_set', repcap.Math.Nr1)

	def repcap_math_set(self, math: repcap.Math) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Math.Default.
		Default value after init: Math.Nr1"""
		self._cmd_group.set_repcap_enum_value(math)

	def repcap_math_get(self) -> repcap.Math:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def data(self):
		"""data commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_data'):
			from .Data import DataCls
			self._data = DataCls(self._core, self._cmd_group)
		return self._data

	@property
	def arithmetics(self):
		"""arithmetics commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_arithmetics'):
			from .Arithmetics import ArithmeticsCls
			self._arithmetics = ArithmeticsCls(self._core, self._cmd_group)
		return self._arithmetics

	@property
	def envSelection(self):
		"""envSelection commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_envSelection'):
			from .EnvSelection import EnvSelectionCls
			self._envSelection = EnvSelectionCls(self._core, self._cmd_group)
		return self._envSelection

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def expression(self):
		"""expression commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_expression'):
			from .Expression import ExpressionCls
			self._expression = ExpressionCls(self._core, self._cmd_group)
		return self._expression

	@property
	def vertical(self):
		"""vertical commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_vertical'):
			from .Vertical import VerticalCls
			self._vertical = VerticalCls(self._core, self._cmd_group)
		return self._vertical

	@property
	def label(self):
		"""label commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_label'):
			from .Label import LabelCls
			self._label = LabelCls(self._core, self._cmd_group)
		return self._label

	@property
	def unit(self):
		"""unit commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_unit'):
			from .Unit import UnitCls
			self._unit = UnitCls(self._core, self._cmd_group)
		return self._unit

	def clone(self) -> 'MathCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = MathCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
