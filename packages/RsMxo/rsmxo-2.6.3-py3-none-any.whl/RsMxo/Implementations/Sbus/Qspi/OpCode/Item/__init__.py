from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal.RepeatedCapability import RepeatedCapability
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ItemCls:
	"""Item commands group definition. 9 total commands, 9 Subgroups, 0 group commands
	Repeated Capability: Item, default value after init: Item.Ix1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("item", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_item_get', 'repcap_item_set', repcap.Item.Ix1)

	def repcap_item_set(self, item: repcap.Item) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Item.Default.
		Default value after init: Item.Ix1"""
		self._cmd_group.set_repcap_enum_value(item)

	def repcap_item_get(self) -> repcap.Item:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def code(self):
		"""code commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_code'):
			from .Code import CodeCls
			self._code = CodeCls(self._core, self._cmd_group)
		return self._code

	@property
	def name(self):
		"""name commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_name'):
			from .Name import NameCls
			self._name = NameCls(self._core, self._cmd_group)
		return self._name

	@property
	def ddr(self):
		"""ddr commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ddr'):
			from .Ddr import DdrCls
			self._ddr = DdrCls(self._core, self._cmd_group)
		return self._ddr

	@property
	def adBytes(self):
		"""adBytes commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_adBytes'):
			from .AdBytes import AdBytesCls
			self._adBytes = AdBytesCls(self._core, self._cmd_group)
		return self._adBytes

	@property
	def adLanes(self):
		"""adLanes commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_adLanes'):
			from .AdLanes import AdLanesCls
			self._adLanes = AdLanesCls(self._core, self._cmd_group)
		return self._adLanes

	@property
	def alt(self):
		"""alt commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_alt'):
			from .Alt import AltCls
			self._alt = AltCls(self._core, self._cmd_group)
		return self._alt

	@property
	def dmCycles(self):
		"""dmCycles commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dmCycles'):
			from .DmCycles import DmCyclesCls
			self._dmCycles = DmCyclesCls(self._core, self._cmd_group)
		return self._dmCycles

	@property
	def data(self):
		"""data commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_data'):
			from .Data import DataCls
			self._data = DataCls(self._core, self._cmd_group)
		return self._data

	@property
	def dtLanes(self):
		"""dtLanes commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dtLanes'):
			from .DtLanes import DtLanesCls
			self._dtLanes = DtLanesCls(self._core, self._cmd_group)
		return self._dtLanes

	def clone(self) -> 'ItemCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ItemCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
