from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class WordCls:
	"""Word commands group definition. 10 total commands, 10 Subgroups, 0 group commands
	Repeated Capability: Word, default value after init: Word.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("word", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_word_get', 'repcap_word_set', repcap.Word.Nr1)

	def repcap_word_set(self, word: repcap.Word) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Word.Default.
		Default value after init: Word.Nr1"""
		self._cmd_group.set_repcap_enum_value(word)

	def repcap_word_get(self) -> repcap.Word:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def start(self):
		"""start commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_start'):
			from .Start import StartCls
			self._start = StartCls(self._core, self._cmd_group)
		return self._start

	@property
	def stop(self):
		"""stop commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_stop'):
			from .Stop import StopCls
			self._stop = StopCls(self._core, self._cmd_group)
		return self._stop

	@property
	def sdi(self):
		"""sdi commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sdi'):
			from .Sdi import SdiCls
			self._sdi = SdiCls(self._core, self._cmd_group)
		return self._sdi

	@property
	def label(self):
		"""label commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_label'):
			from .Label import LabelCls
			self._label = LabelCls(self._core, self._cmd_group)
		return self._label

	@property
	def symbol(self):
		"""symbol commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_symbol'):
			from .Symbol import SymbolCls
			self._symbol = SymbolCls(self._core, self._cmd_group)
		return self._symbol

	@property
	def ssm(self):
		"""ssm commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ssm'):
			from .Ssm import SsmCls
			self._ssm = SsmCls(self._core, self._cmd_group)
		return self._ssm

	@property
	def data(self):
		"""data commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_data'):
			from .Data import DataCls
			self._data = DataCls(self._core, self._cmd_group)
		return self._data

	@property
	def pattern(self):
		"""pattern commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_pattern'):
			from .Pattern import PatternCls
			self._pattern = PatternCls(self._core, self._cmd_group)
		return self._pattern

	@property
	def bitrate(self):
		"""bitrate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bitrate'):
			from .Bitrate import BitrateCls
			self._bitrate = BitrateCls(self._core, self._cmd_group)
		return self._bitrate

	def clone(self) -> 'WordCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = WordCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
