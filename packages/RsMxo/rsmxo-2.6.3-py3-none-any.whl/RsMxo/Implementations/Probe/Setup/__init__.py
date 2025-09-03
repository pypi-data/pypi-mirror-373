from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SetupCls:
	"""Setup commands group definition. 49 total commands, 26 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("setup", core, parent)

	@property
	def bandwidth(self):
		"""bandwidth commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bandwidth'):
			from .Bandwidth import BandwidthCls
			self._bandwidth = BandwidthCls(self._core, self._cmd_group)
		return self._bandwidth

	@property
	def capacitance(self):
		"""capacitance commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_capacitance'):
			from .Capacitance import CapacitanceCls
			self._capacitance = CapacitanceCls(self._core, self._cmd_group)
		return self._capacitance

	@property
	def displayDiff(self):
		"""displayDiff commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_displayDiff'):
			from .DisplayDiff import DisplayDiffCls
			self._displayDiff = DisplayDiffCls(self._core, self._cmd_group)
		return self._displayDiff

	@property
	def impedance(self):
		"""impedance commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_impedance'):
			from .Impedance import ImpedanceCls
			self._impedance = ImpedanceCls(self._core, self._cmd_group)
		return self._impedance

	@property
	def mode(self):
		"""mode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_mode'):
			from .Mode import ModeCls
			self._mode = ModeCls(self._core, self._cmd_group)
		return self._mode

	@property
	def prMode(self):
		"""prMode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_prMode'):
			from .PrMode import PrModeCls
			self._prMode = PrModeCls(self._core, self._cmd_group)
		return self._prMode

	@property
	def name(self):
		"""name commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_name'):
			from .Name import NameCls
			self._name = NameCls(self._core, self._cmd_group)
		return self._name

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def typePy(self):
		"""typePy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_typePy'):
			from .TypePy import TypePyCls
			self._typePy = TypePyCls(self._core, self._cmd_group)
		return self._typePy

	@property
	def adapter(self):
		"""adapter commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_adapter'):
			from .Adapter import AdapterCls
			self._adapter = AdapterCls(self._core, self._cmd_group)
		return self._adapter

	@property
	def cmOffset(self):
		"""cmOffset commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_cmOffset'):
			from .CmOffset import CmOffsetCls
			self._cmOffset = CmOffsetCls(self._core, self._cmd_group)
		return self._cmOffset

	@property
	def dmOffset(self):
		"""dmOffset commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dmOffset'):
			from .DmOffset import DmOffsetCls
			self._dmOffset = DmOffsetCls(self._core, self._cmd_group)
		return self._dmOffset

	@property
	def poffset(self):
		"""poffset commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_poffset'):
			from .Poffset import PoffsetCls
			self._poffset = PoffsetCls(self._core, self._cmd_group)
		return self._poffset

	@property
	def noffset(self):
		"""noffset commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_noffset'):
			from .Noffset import NoffsetCls
			self._noffset = NoffsetCls(self._core, self._cmd_group)
		return self._noffset

	@property
	def zaxv(self):
		"""zaxv commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_zaxv'):
			from .Zaxv import ZaxvCls
			self._zaxv = ZaxvCls(self._core, self._cmd_group)
		return self._zaxv

	@property
	def degauss(self):
		"""degauss commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_degauss'):
			from .Degauss import DegaussCls
			self._degauss = DegaussCls(self._core, self._cmd_group)
		return self._degauss

	@property
	def acCoupling(self):
		"""acCoupling commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_acCoupling'):
			from .AcCoupling import AcCouplingCls
			self._acCoupling = AcCouplingCls(self._core, self._cmd_group)
		return self._acCoupling

	@property
	def dcRange(self):
		"""dcRange commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_dcRange'):
			from .DcRange import DcRangeCls
			self._dcRange = DcRangeCls(self._core, self._cmd_group)
		return self._dcRange

	@property
	def alignment(self):
		"""alignment commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_alignment'):
			from .Alignment import AlignmentCls
			self._alignment = AlignmentCls(self._core, self._cmd_group)
		return self._alignment

	@property
	def offset(self):
		"""offset commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_offset'):
			from .Offset import OffsetCls
			self._offset = OffsetCls(self._core, self._cmd_group)
		return self._offset

	@property
	def attenuation(self):
		"""attenuation commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_attenuation'):
			from .Attenuation import AttenuationCls
			self._attenuation = AttenuationCls(self._core, self._cmd_group)
		return self._attenuation

	@property
	def gain(self):
		"""gain commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_gain'):
			from .Gain import GainCls
			self._gain = GainCls(self._core, self._cmd_group)
		return self._gain

	@property
	def term(self):
		"""term commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_term'):
			from .Term import TermCls
			self._term = TermCls(self._core, self._cmd_group)
		return self._term

	@property
	def advanced(self):
		"""advanced commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_advanced'):
			from .Advanced import AdvancedCls
			self._advanced = AdvancedCls(self._core, self._cmd_group)
		return self._advanced

	@property
	def laser(self):
		"""laser commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_laser'):
			from .Laser import LaserCls
			self._laser = LaserCls(self._core, self._cmd_group)
		return self._laser

	@property
	def tipModel(self):
		"""tipModel commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_tipModel'):
			from .TipModel import TipModelCls
			self._tipModel = TipModelCls(self._core, self._cmd_group)
		return self._tipModel

	def clone(self) -> 'SetupCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SetupCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
