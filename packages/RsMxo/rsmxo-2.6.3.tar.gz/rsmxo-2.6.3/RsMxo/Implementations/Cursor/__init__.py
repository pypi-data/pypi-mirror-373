from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CursorCls:
	"""Cursor commands group definition. 34 total commands, 28 Subgroups, 0 group commands
	Repeated Capability: Cursor, default value after init: Cursor.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cursor", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_cursor_get', 'repcap_cursor_set', repcap.Cursor.Nr1)

	def repcap_cursor_set(self, cursor: repcap.Cursor) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Cursor.Default.
		Default value after init: Cursor.Nr1"""
		self._cmd_group.set_repcap_enum_value(cursor)

	def repcap_cursor_get(self) -> repcap.Cursor:
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
	def aoff(self):
		"""aoff commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_aoff'):
			from .Aoff import AoffCls
			self._aoff = AoffCls(self._core, self._cmd_group)
		return self._aoff

	@property
	def siad(self):
		"""siad commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_siad'):
			from .Siad import SiadCls
			self._siad = SiadCls(self._core, self._cmd_group)
		return self._siad

	@property
	def function(self):
		"""function commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_function'):
			from .Function import FunctionCls
			self._function = FunctionCls(self._core, self._cmd_group)
		return self._function

	@property
	def pexcursion(self):
		"""pexcursion commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_pexcursion'):
			from .Pexcursion import PexcursionCls
			self._pexcursion = PexcursionCls(self._core, self._cmd_group)
		return self._pexcursion

	@property
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def ssource(self):
		"""ssource commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ssource'):
			from .Ssource import SsourceCls
			self._ssource = SsourceCls(self._core, self._cmd_group)
		return self._ssource

	@property
	def usSource(self):
		"""usSource commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_usSource'):
			from .UsSource import UsSourceCls
			self._usSource = UsSourceCls(self._core, self._cmd_group)
		return self._usSource

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def x1Envelope(self):
		"""x1Envelope commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_x1Envelope'):
			from .X1Envelope import X1EnvelopeCls
			self._x1Envelope = X1EnvelopeCls(self._core, self._cmd_group)
		return self._x1Envelope

	@property
	def x1Position(self):
		"""x1Position commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_x1Position'):
			from .X1Position import X1PositionCls
			self._x1Position = X1PositionCls(self._core, self._cmd_group)
		return self._x1Position

	@property
	def x2Envelope(self):
		"""x2Envelope commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_x2Envelope'):
			from .X2Envelope import X2EnvelopeCls
			self._x2Envelope = X2EnvelopeCls(self._core, self._cmd_group)
		return self._x2Envelope

	@property
	def x2Position(self):
		"""x2Position commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_x2Position'):
			from .X2Position import X2PositionCls
			self._x2Position = X2PositionCls(self._core, self._cmd_group)
		return self._x2Position

	@property
	def xcoupling(self):
		"""xcoupling commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_xcoupling'):
			from .Xcoupling import XcouplingCls
			self._xcoupling = XcouplingCls(self._core, self._cmd_group)
		return self._xcoupling

	@property
	def y1Position(self):
		"""y1Position commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_y1Position'):
			from .Y1Position import Y1PositionCls
			self._y1Position = Y1PositionCls(self._core, self._cmd_group)
		return self._y1Position

	@property
	def y2Position(self):
		"""y2Position commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_y2Position'):
			from .Y2Position import Y2PositionCls
			self._y2Position = Y2PositionCls(self._core, self._cmd_group)
		return self._y2Position

	@property
	def label(self):
		"""label commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_label'):
			from .Label import LabelCls
			self._label = LabelCls(self._core, self._cmd_group)
		return self._label

	@property
	def style(self):
		"""style commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_style'):
			from .Style import StyleCls
			self._style = StyleCls(self._core, self._cmd_group)
		return self._style

	@property
	def ycoupling(self):
		"""ycoupling commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ycoupling'):
			from .Ycoupling import YcouplingCls
			self._ycoupling = YcouplingCls(self._core, self._cmd_group)
		return self._ycoupling

	@property
	def sscreen(self):
		"""sscreen commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sscreen'):
			from .Sscreen import SscreenCls
			self._sscreen = SscreenCls(self._core, self._cmd_group)
		return self._sscreen

	@property
	def vertical(self):
		"""vertical commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_vertical'):
			from .Vertical import VerticalCls
			self._vertical = VerticalCls(self._core, self._cmd_group)
		return self._vertical

	@property
	def horizontal(self):
		"""horizontal commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_horizontal'):
			from .Horizontal import HorizontalCls
			self._horizontal = HorizontalCls(self._core, self._cmd_group)
		return self._horizontal

	@property
	def maximum(self):
		"""maximum commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_maximum'):
			from .Maximum import MaximumCls
			self._maximum = MaximumCls(self._core, self._cmd_group)
		return self._maximum

	@property
	def tracking(self):
		"""tracking commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_tracking'):
			from .Tracking import TrackingCls
			self._tracking = TrackingCls(self._core, self._cmd_group)
		return self._tracking

	@property
	def xdelta(self):
		"""xdelta commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_xdelta'):
			from .Xdelta import XdeltaCls
			self._xdelta = XdeltaCls(self._core, self._cmd_group)
		return self._xdelta

	@property
	def ydelta(self):
		"""ydelta commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_ydelta'):
			from .Ydelta import YdeltaCls
			self._ydelta = YdeltaCls(self._core, self._cmd_group)
		return self._ydelta

	@property
	def fft(self):
		"""fft commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_fft'):
			from .Fft import FftCls
			self._fft = FftCls(self._core, self._cmd_group)
		return self._fft

	@property
	def display(self):
		"""display commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_display'):
			from .Display import DisplayCls
			self._display = DisplayCls(self._core, self._cmd_group)
		return self._display

	def clone(self) -> 'CursorCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = CursorCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
