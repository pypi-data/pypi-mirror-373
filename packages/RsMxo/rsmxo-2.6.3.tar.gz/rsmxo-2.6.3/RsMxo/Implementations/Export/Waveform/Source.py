from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, export_sources: List[enums.ExportSource]) -> None:
		"""EXPort:WAVeform:SOURce \n
		Snippet: driver.export.waveform.source.set(export_sources = [ExportSource.C1, ExportSource.SPECNORM4]) \n
		Selects the waveform or waveforms to be exported to file. \n
			:param export_sources: Possible waveform sources are: Analog signals: C1,C2,C3,C4,C5,C6,C7,C8 Digital signals: D0,D1,D2,D3,D4,D5,D6,D7,D8,D9,D10,D11,D12,D13,D14,D15 Math waveforms: M1,M2,M3,M4,M5 Reference waveforms: R1,R2,R3,R4 Spectrum traces: SPECMAXH1,SPECMINH1,SPECNORM1,SPECAVER1,SPECMAXH2,SPECMINH2,SPECNORM2,SPECAVER2,SPECMAXH3,SPECMINH3,SPECNORM3,SPECAVER3,SPECMAXH4,SPECMINH4,SPECNORM4,SPECAVER4 Tracks: TRK1,TRK2,TRK3, ...,TRK24
		"""
		param = Conversions.enum_list_to_str(export_sources, enums.ExportSource)
		self._core.io.write(f'EXPort:WAVeform:SOURce {param}')
