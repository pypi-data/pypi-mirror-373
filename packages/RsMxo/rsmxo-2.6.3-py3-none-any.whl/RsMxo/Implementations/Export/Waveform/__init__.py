from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class WaveformCls:
	"""Waveform commands group definition. 13 total commands, 3 Subgroups, 8 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("waveform", core, parent)

	@property
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def autoNaming(self):
		"""autoNaming commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_autoNaming'):
			from .AutoNaming import AutoNamingCls
			self._autoNaming = AutoNamingCls(self._core, self._cmd_group)
		return self._autoNaming

	@property
	def data(self):
		"""data commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_data'):
			from .Data import DataCls
			self._data = DataCls(self._core, self._cmd_group)
		return self._data

	# noinspection PyTypeChecker
	def get_scope(self) -> enums.ExportScope:
		"""EXPort:WAVeform:SCOPe \n
		Snippet: value: enums.ExportScope = driver.export.waveform.get_scope() \n
		Defines the part of the waveform record that has to be stored. \n
			:return: scope:
				- DISPlay: Waveform data that is displayed in the diagram.
				- ALL: Complete waveform, which is usually longer than the displayed waveform.
				- CURSor: Data between the cursor lines if a cursor measurement is defined for the source waveform.
				- GATE: Data included in the measurement gate if a gated measurement is defined for the source waveform.
				- MANual: Saves the data between user-defined start and stop values to be set with EXPort:WAVeform:STARt and EXPort:WAVeform:STOP."""
		response = self._core.io.query_str('EXPort:WAVeform:SCOPe?')
		return Conversions.str_to_scalar_enum(response, enums.ExportScope)

	def set_scope(self, scope: enums.ExportScope) -> None:
		"""EXPort:WAVeform:SCOPe \n
		Snippet: driver.export.waveform.set_scope(scope = enums.ExportScope.ALL) \n
		Defines the part of the waveform record that has to be stored. \n
			:param scope:
				- DISPlay: Waveform data that is displayed in the diagram.
				- ALL: Complete waveform, which is usually longer than the displayed waveform.
				- CURSor: Data between the cursor lines if a cursor measurement is defined for the source waveform.
				- GATE: Data included in the measurement gate if a gated measurement is defined for the source waveform.
				- MANual: Saves the data between user-defined start and stop values to be set with EXPort:WAVeform:STARt and EXPort:WAVeform:STOP."""
		param = Conversions.enum_scalar_to_str(scope, enums.ExportScope)
		self._core.io.write(f'EXPort:WAVeform:SCOPe {param}')

	# noinspection PyTypeChecker
	def get_cursorset(self) -> enums.Cursor:
		"""EXPort:WAVeform:CURSorset \n
		Snippet: value: enums.Cursor = driver.export.waveform.get_cursorset() \n
		Sets the cursor set to be used for limited data export if method RsMxo.Export.Waveform.scope is set to CURSor. \n
			:return: cursor_set: No help available
		"""
		response = self._core.io.query_str('EXPort:WAVeform:CURSorset?')
		return Conversions.str_to_scalar_enum(response, enums.Cursor)

	def set_cursorset(self, cursor_set: enums.Cursor) -> None:
		"""EXPort:WAVeform:CURSorset \n
		Snippet: driver.export.waveform.set_cursorset(cursor_set = enums.Cursor.CURSOR1) \n
		Sets the cursor set to be used for limited data export if method RsMxo.Export.Waveform.scope is set to CURSor. \n
			:param cursor_set: No help available
		"""
		param = Conversions.enum_scalar_to_str(cursor_set, enums.Cursor)
		self._core.io.write(f'EXPort:WAVeform:CURSorset {param}')

	def get_gate(self) -> float:
		"""EXPort:WAVeform:GATE \n
		Snippet: value: float = driver.export.waveform.get_gate() \n
		Selects the gate to be used for limited data export if method RsMxo.Export.Waveform.scope is set to GATE. \n
			:return: meas_gate: No help available
		"""
		response = self._core.io.query_str('EXPort:WAVeform:GATE?')
		return Conversions.str_to_float(response)

	def set_gate(self, meas_gate: float) -> None:
		"""EXPort:WAVeform:GATE \n
		Snippet: driver.export.waveform.set_gate(meas_gate = 1.0) \n
		Selects the gate to be used for limited data export if method RsMxo.Export.Waveform.scope is set to GATE. \n
			:param meas_gate: No help available
		"""
		param = Conversions.decimal_value_to_str(meas_gate)
		self._core.io.write(f'EXPort:WAVeform:GATE {param}')

	def get_start(self) -> float:
		"""EXPort:WAVeform:STARt \n
		Snippet: value: float = driver.export.waveform.get_start() \n
		Sets the start time value of the waveform section for export, if method RsMxo.Export.Waveform.scope is set to Manual. \n
			:return: start: No help available
		"""
		response = self._core.io.query_str('EXPort:WAVeform:STARt?')
		return Conversions.str_to_float(response)

	def set_start(self, start: float) -> None:
		"""EXPort:WAVeform:STARt \n
		Snippet: driver.export.waveform.set_start(start = 1.0) \n
		Sets the start time value of the waveform section for export, if method RsMxo.Export.Waveform.scope is set to Manual. \n
			:param start: No help available
		"""
		param = Conversions.decimal_value_to_str(start)
		self._core.io.write(f'EXPort:WAVeform:STARt {param}')

	def get_stop(self) -> float:
		"""EXPort:WAVeform:STOP \n
		Snippet: value: float = driver.export.waveform.get_stop() \n
		Sets the end time value of the waveform section for export, if method RsMxo.Export.Waveform.scope is set to Manual. \n
			:return: stop: No help available
		"""
		response = self._core.io.query_str('EXPort:WAVeform:STOP?')
		return Conversions.str_to_float(response)

	def set_stop(self, stop: float) -> None:
		"""EXPort:WAVeform:STOP \n
		Snippet: driver.export.waveform.set_stop(stop = 1.0) \n
		Sets the end time value of the waveform section for export, if method RsMxo.Export.Waveform.scope is set to Manual. \n
			:param stop: No help available
		"""
		param = Conversions.decimal_value_to_str(stop)
		self._core.io.write(f'EXPort:WAVeform:STOP {param}')

	def save(self) -> None:
		"""EXPort:WAVeform:SAVE \n
		Snippet: driver.export.waveform.save() \n
		Saves the waveform to the file specified with method RsMxo.Export.Waveform.name. \n
		"""
		self._core.io.write(f'EXPort:WAVeform:SAVE')

	def save_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""EXPort:WAVeform:SAVE \n
		Snippet: driver.export.waveform.save_and_wait() \n
		Saves the waveform to the file specified with method RsMxo.Export.Waveform.name. \n
		Same as save, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'EXPort:WAVeform:SAVE', opc_timeout_ms)

	def abort(self) -> None:
		"""EXPort:WAVeform:ABORt \n
		Snippet: driver.export.waveform.abort() \n
		Aborts a running waveform export, which was started with method RsMxo.Export.Waveform.save. \n
		"""
		self._core.io.write(f'EXPort:WAVeform:ABORt')

	def abort_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""EXPort:WAVeform:ABORt \n
		Snippet: driver.export.waveform.abort_and_wait() \n
		Aborts a running waveform export, which was started with method RsMxo.Export.Waveform.save. \n
		Same as abort, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'EXPort:WAVeform:ABORt', opc_timeout_ms)

	def get_name(self) -> str:
		"""EXPort:WAVeform:NAME \n
		Snippet: value: str = driver.export.waveform.get_name() \n
		Sets the path, the filename and the file format of the export file. The setting is used for save-as operations that do
		not use the autonaming settings. \n
			:return: name: String with path and filename with extension .ref, .csv, .zip, or .h5. Extension .ref is provided for single waveform export only, while .zip is for export of multiple waveforms in REF format. CSV can be used for export of single waveforms, and multiple analog channels. For local storage, the path is always /home/storage/userData.
		"""
		response = self._core.io.query_str('EXPort:WAVeform:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""EXPort:WAVeform:NAME \n
		Snippet: driver.export.waveform.set_name(name = 'abc') \n
		Sets the path, the filename and the file format of the export file. The setting is used for save-as operations that do
		not use the autonaming settings. \n
			:param name: String with path and filename with extension .ref, .csv, .zip, or .h5. Extension .ref is provided for single waveform export only, while .zip is for export of multiple waveforms in REF format. CSV can be used for export of single waveforms, and multiple analog channels. For local storage, the path is always /home/storage/userData.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'EXPort:WAVeform:NAME {param}')

	def clone(self) -> 'WaveformCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = WaveformCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
