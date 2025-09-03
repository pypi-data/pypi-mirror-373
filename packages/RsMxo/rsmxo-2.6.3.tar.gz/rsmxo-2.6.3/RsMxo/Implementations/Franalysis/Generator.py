from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GeneratorCls:
	"""Generator commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("generator", core, parent)

	# noinspection PyTypeChecker
	def get_channel(self) -> enums.GeneratorChannel:
		"""FRANalysis:GENerator[:CHANnel] \n
		Snippet: value: enums.GeneratorChannel = driver.franalysis.generator.get_channel() \n
		Selects the built-in generator to start a frequency sweep for a defined frequency range. \n
			:return: gen_ch: No help available
		"""
		response = self._core.io.query_str('FRANalysis:GENerator:CHANnel?')
		return Conversions.str_to_scalar_enum(response, enums.GeneratorChannel)

	def set_channel(self, gen_ch: enums.GeneratorChannel) -> None:
		"""FRANalysis:GENerator[:CHANnel] \n
		Snippet: driver.franalysis.generator.set_channel(gen_ch = enums.GeneratorChannel.GEN1) \n
		Selects the built-in generator to start a frequency sweep for a defined frequency range. \n
			:param gen_ch: No help available
		"""
		param = Conversions.enum_scalar_to_str(gen_ch, enums.GeneratorChannel)
		self._core.io.write(f'FRANalysis:GENerator:CHANnel {param}')

	def get_amplitude(self) -> float:
		"""FRANalysis:GENerator:AMPLitude \n
		Snippet: value: float = driver.franalysis.generator.get_amplitude() \n
		Sets a fixed amplitude for the frequency response analysis. \n
			:return: gen_amplitude: No help available
		"""
		response = self._core.io.query_str('FRANalysis:GENerator:AMPLitude?')
		return Conversions.str_to_float(response)

	def set_amplitude(self, gen_amplitude: float) -> None:
		"""FRANalysis:GENerator:AMPLitude \n
		Snippet: driver.franalysis.generator.set_amplitude(gen_amplitude = 1.0) \n
		Sets a fixed amplitude for the frequency response analysis. \n
			:param gen_amplitude: No help available
		"""
		param = Conversions.decimal_value_to_str(gen_amplitude)
		self._core.io.write(f'FRANalysis:GENerator:AMPLitude {param}')

	# noinspection PyTypeChecker
	def get_load(self) -> enums.WgenLoad:
		"""FRANalysis:GENerator:LOAD \n
		Snippet: value: enums.WgenLoad = driver.franalysis.generator.get_load() \n
		Selects the generator voltage display for 50Ω or high impedance load. \n
			:return: gen_load: HIZ: high input impedance
		"""
		response = self._core.io.query_str('FRANalysis:GENerator:LOAD?')
		return Conversions.str_to_scalar_enum(response, enums.WgenLoad)

	def set_load(self, gen_load: enums.WgenLoad) -> None:
		"""FRANalysis:GENerator:LOAD \n
		Snippet: driver.franalysis.generator.set_load(gen_load = enums.WgenLoad.FIFTy) \n
		Selects the generator voltage display for 50Ω or high impedance load. \n
			:param gen_load: HIZ: high input impedance
		"""
		param = Conversions.enum_scalar_to_str(gen_load, enums.WgenLoad)
		self._core.io.write(f'FRANalysis:GENerator:LOAD {param}')
