from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StopCls:
	"""Stop commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("stop", core, parent)

	def get(self, spectrum=repcap.Spectrum.Default) -> float:
		"""CALCulate:SPECtrum<*>:GATE:USED:STOP \n
		Snippet: value: float = driver.calculate.spectrum.gate.used.stop.get(spectrum = repcap.Spectrum.Default) \n
		No command help available \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: stop: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:GATE:USED:STOP?')
		return Conversions.str_to_float(response)
