from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SoftwareCls:
	"""Software commands group definition. 8 total commands, 6 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("software", core, parent)

	@property
	def algorithm(self):
		"""algorithm commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_algorithm'):
			from .Algorithm import AlgorithmCls
			self._algorithm = AlgorithmCls(self._core, self._cmd_group)
		return self._algorithm

	@property
	def bandwidth(self):
		"""bandwidth commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bandwidth'):
			from .Bandwidth import BandwidthCls
			self._bandwidth = BandwidthCls(self._core, self._cmd_group)
		return self._bandwidth

	@property
	def relBwidth(self):
		"""relBwidth commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_relBwidth'):
			from .RelBwidth import RelBwidthCls
			self._relBwidth = RelBwidthCls(self._core, self._cmd_group)
		return self._relBwidth

	@property
	def selResults(self):
		"""selResults commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_selResults'):
			from .SelResults import SelResultsCls
			self._selResults = SelResultsCls(self._core, self._cmd_group)
		return self._selResults

	@property
	def cfrequency(self):
		"""cfrequency commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_cfrequency'):
			from .Cfrequency import CfrequencyCls
			self._cfrequency = CfrequencyCls(self._core, self._cmd_group)
		return self._cfrequency

	@property
	def pll(self):
		"""pll commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_pll'):
			from .Pll import PllCls
			self._pll = PllCls(self._core, self._cmd_group)
		return self._pll

	def clone(self) -> 'SoftwareCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SoftwareCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
