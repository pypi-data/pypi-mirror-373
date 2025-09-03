from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AutoCls:
	"""Auto commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("auto", core, parent)

	def set(self, auto_rbw: bool, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:FREQuency:BANDwidth[:RESolution]:AUTO \n
		Snippet: driver.calculate.spectrum.frequency.bandwidth.resolution.auto.set(auto_rbw = False, spectrum = repcap.Spectrum.Default) \n
		Couples the frequency span to the RBW setting. \n
			:param auto_rbw: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.bool_to_str(auto_rbw)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:FREQuency:BANDwidth:RESolution:AUTO {param}')

	def get(self, spectrum=repcap.Spectrum.Default) -> bool:
		"""CALCulate:SPECtrum<*>:FREQuency:BANDwidth[:RESolution]:AUTO \n
		Snippet: value: bool = driver.calculate.spectrum.frequency.bandwidth.resolution.auto.get(spectrum = repcap.Spectrum.Default) \n
		Couples the frequency span to the RBW setting. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: auto_rbw: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:FREQuency:BANDwidth:RESolution:AUTO?')
		return Conversions.str_to_bool(response)
