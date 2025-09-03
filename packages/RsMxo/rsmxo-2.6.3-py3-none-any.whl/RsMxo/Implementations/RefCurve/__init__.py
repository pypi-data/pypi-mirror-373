from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RefCurveCls:
	"""RefCurve commands group definition. 25 total commands, 14 Subgroups, 4 group commands
	Repeated Capability: RefCurve, default value after init: RefCurve.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("refCurve", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_refCurve_get', 'repcap_refCurve_set', repcap.RefCurve.Nr1)

	def repcap_refCurve_set(self, refCurve: repcap.RefCurve) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to RefCurve.Default.
		Default value after init: RefCurve.Nr1"""
		self._cmd_group.set_repcap_enum_value(refCurve)

	def repcap_refCurve_get(self) -> repcap.RefCurve:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def data(self):
		"""data commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_data'):
			from .Data import DataCls
			self._data = DataCls(self._core, self._cmd_group)
		return self._data

	@property
	def hmode(self):
		"""hmode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_hmode'):
			from .Hmode import HmodeCls
			self._hmode = HmodeCls(self._core, self._cmd_group)
		return self._hmode

	@property
	def name(self):
		"""name commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_name'):
			from .Name import NameCls
			self._name = NameCls(self._core, self._cmd_group)
		return self._name

	@property
	def offset(self):
		"""offset commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_offset'):
			from .Offset import OffsetCls
			self._offset = OffsetCls(self._core, self._cmd_group)
		return self._offset

	@property
	def position(self):
		"""position commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_position'):
			from .Position import PositionCls
			self._position = PositionCls(self._core, self._cmd_group)
		return self._position

	@property
	def restore(self):
		"""restore commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_restore'):
			from .Restore import RestoreCls
			self._restore = RestoreCls(self._core, self._cmd_group)
		return self._restore

	@property
	def scale(self):
		"""scale commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_scale'):
			from .Scale import ScaleCls
			self._scale = ScaleCls(self._core, self._cmd_group)
		return self._scale

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
	def update(self):
		"""update commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_update'):
			from .Update import UpdateCls
			self._update = UpdateCls(self._core, self._cmd_group)
		return self._update

	@property
	def vmode(self):
		"""vmode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_vmode'):
			from .Vmode import VmodeCls
			self._vmode = VmodeCls(self._core, self._cmd_group)
		return self._vmode

	@property
	def toOriginal(self):
		"""toOriginal commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_toOriginal'):
			from .ToOriginal import ToOriginalCls
			self._toOriginal = ToOriginalCls(self._core, self._cmd_group)
		return self._toOriginal

	@property
	def axis(self):
		"""axis commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_axis'):
			from .Axis import AxisCls
			self._axis = AxisCls(self._core, self._cmd_group)
		return self._axis

	@property
	def rescale(self):
		"""rescale commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_rescale'):
			from .Rescale import RescaleCls
			self._rescale = RescaleCls(self._core, self._cmd_group)
		return self._rescale

	def clear(self, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:CLEar \n
		Snippet: driver.refCurve.clear(refCurve = repcap.RefCurve.Default) \n
		The selected reference waveform disappears, its memory is deleted. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
		"""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:CLEar')

	def clear_and_wait(self, refCurve=repcap.RefCurve.Default, opc_timeout_ms: int = -1) -> None:
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		"""REFCurve<*>:CLEar \n
		Snippet: driver.refCurve.clear_and_wait(refCurve = repcap.RefCurve.Default) \n
		The selected reference waveform disappears, its memory is deleted. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'REFCurve{refCurve_cmd_val}:CLEar', opc_timeout_ms)

	def save(self, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:SAVE \n
		Snippet: driver.refCurve.save(refCurve = repcap.RefCurve.Default) \n
		Saves the reference waveform to the file selected by method RsMxo.RefCurve.Name.set. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
		"""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:SAVE')

	def save_and_wait(self, refCurve=repcap.RefCurve.Default, opc_timeout_ms: int = -1) -> None:
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		"""REFCurve<*>:SAVE \n
		Snippet: driver.refCurve.save_and_wait(refCurve = repcap.RefCurve.Default) \n
		Saves the reference waveform to the file selected by method RsMxo.RefCurve.Name.set. \n
		Same as save, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'REFCurve{refCurve_cmd_val}:SAVE', opc_timeout_ms)

	def open(self, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:OPEN \n
		Snippet: driver.refCurve.open(refCurve = repcap.RefCurve.Default) \n
		Loads the reference waveform file selected by method RsMxo.RefCurve.Name.set. Note that reference waveforms can be loaded
		only from .ref files. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
		"""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:OPEN')

	def open_and_wait(self, refCurve=repcap.RefCurve.Default, opc_timeout_ms: int = -1) -> None:
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		"""REFCurve<*>:OPEN \n
		Snippet: driver.refCurve.open_and_wait(refCurve = repcap.RefCurve.Default) \n
		Loads the reference waveform file selected by method RsMxo.RefCurve.Name.set. Note that reference waveforms can be loaded
		only from .ref files. \n
		Same as open, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'REFCurve{refCurve_cmd_val}:OPEN', opc_timeout_ms)

	def abort(self, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:ABORt \n
		Snippet: driver.refCurve.abort(refCurve = repcap.RefCurve.Default) \n
		Aborts a running reference waveform export, which was started with method RsMxo.RefCurve.save, or a running reference
		waveform update, which was started with method RsMxo.RefCurve.Update.set. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
		"""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:ABORt')

	def abort_and_wait(self, refCurve=repcap.RefCurve.Default, opc_timeout_ms: int = -1) -> None:
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		"""REFCurve<*>:ABORt \n
		Snippet: driver.refCurve.abort_and_wait(refCurve = repcap.RefCurve.Default) \n
		Aborts a running reference waveform export, which was started with method RsMxo.RefCurve.save, or a running reference
		waveform update, which was started with method RsMxo.RefCurve.Update.set. \n
		Same as abort, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'REFCurve{refCurve_cmd_val}:ABORt', opc_timeout_ms)

	def clone(self) -> 'RefCurveCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = RefCurveCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
