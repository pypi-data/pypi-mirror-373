from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LoadCls:
	"""Load commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("load", core, parent)

	def set(self, load: enums.WgenLoad, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:OUTPut[:LOAD] \n
		Snippet: driver.wgenerator.output.load.set(load = enums.WgenLoad.FIFTy, waveformGen = repcap.WaveformGen.Default) \n
		Select the user load, the load of the DUT at its connection. \n
			:param load: FIFTy: 50Ω HIZ: High-Z (high input impedance)
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.enum_scalar_to_str(load, enums.WgenLoad)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:OUTPut:LOAD {param}')

	# noinspection PyTypeChecker
	def get(self, waveformGen=repcap.WaveformGen.Default) -> enums.WgenLoad:
		"""WGENerator<*>:OUTPut[:LOAD] \n
		Snippet: value: enums.WgenLoad = driver.wgenerator.output.load.get(waveformGen = repcap.WaveformGen.Default) \n
		Select the user load, the load of the DUT at its connection. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: load: FIFTy: 50Ω HIZ: High-Z (high input impedance)"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:OUTPut:LOAD?')
		return Conversions.str_to_scalar_enum(response, enums.WgenLoad)
