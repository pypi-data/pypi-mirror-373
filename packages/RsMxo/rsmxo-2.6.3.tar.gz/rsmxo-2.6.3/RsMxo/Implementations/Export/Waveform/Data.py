from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DataCls:
	"""Data commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("data", core, parent)

	def get_values(self) -> bytes:
		"""EXPort:WAVeform:DATA[:VALues] \n
		Snippet: value: bytes = driver.export.waveform.data.get_values() \n
		Starts a fast export of the selected waveforms for use in automated analysis systems. There is no corresponding ...
		:DATA:HEADer command. Offset and length parameters are not available. Select the waveforms for export with method RsMxo.
		Export.Waveform.Source.set, and the data scope with method RsMxo.Export.Waveform.scope. The data stream contains the pure
		data of the exported sources. The order of the sources can be read with method RsMxo.Export.Waveform.Source.set.
		The order is predefined and independent of the setting order to ensure the same order for the same selection of waveforms.
		Fast export is possible at low record length, depending on the instrument and active functionality. If fast export is not
		possible, you can export the single signals. \n
			:return: data: No help available
		"""
		response = self._core.io.query_bin_block('EXPort:WAVeform:DATA:VALues?')
		return response
