from typing import List

from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValueCls:
	"""Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("value", core, parent)

	def get(self, spectrum=repcap.Spectrum.Default) -> List[float]:
		"""CALCulate:SPECtrum<*>:PLISt:RESult[:VALue] \n
		Snippet: value: List[float] = driver.calculate.spectrum.plist.result.value.get(spectrum = repcap.Spectrum.Default) \n
		Returns the current peak list measurement results. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: value: Comma-separated list of results"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_bin_or_ascii_float_list(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:RESult:VALue?')
		return response
