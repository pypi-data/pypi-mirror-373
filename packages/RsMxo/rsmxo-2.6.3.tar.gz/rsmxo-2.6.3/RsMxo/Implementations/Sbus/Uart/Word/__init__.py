from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class WordCls:
	"""Word commands group definition. 7 total commands, 7 Subgroups, 0 group commands
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
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

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
	def txValue(self):
		"""txValue commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_txValue'):
			from .TxValue import TxValueCls
			self._txValue = TxValueCls(self._core, self._cmd_group)
		return self._txValue

	@property
	def rxValue(self):
		"""rxValue commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rxValue'):
			from .RxValue import RxValueCls
			self._rxValue = RxValueCls(self._core, self._cmd_group)
		return self._rxValue

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
