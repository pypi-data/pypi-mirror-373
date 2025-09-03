from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CutoffCls:
	"""Cutoff commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cutoff", core, parent)

	# noinspection PyTypeChecker
	def get_lowpass(self) -> enums.AnalogCutoffFreq:
		"""TRIGger:ANEDge:CUToff:LOWPass \n
		Snippet: value: enums.AnalogCutoffFreq = driver.trigger.anEdge.cutoff.get_lowpass() \n
		Frequencies higher than the cutoff frequency are rejected, lower frequencies pass the filter. \n
			:return: analog_cutoff_lp: No help available
		"""
		response = self._core.io.query_str('TRIGger:ANEDge:CUToff:LOWPass?')
		return Conversions.str_to_scalar_enum(response, enums.AnalogCutoffFreq)

	def set_lowpass(self, analog_cutoff_lp: enums.AnalogCutoffFreq) -> None:
		"""TRIGger:ANEDge:CUToff:LOWPass \n
		Snippet: driver.trigger.anEdge.cutoff.set_lowpass(analog_cutoff_lp = enums.AnalogCutoffFreq.KHZ5) \n
		Frequencies higher than the cutoff frequency are rejected, lower frequencies pass the filter. \n
			:param analog_cutoff_lp: KHZ50 = 50 kHz MHZ50 = 50 MHz
		"""
		param = Conversions.enum_scalar_to_str(analog_cutoff_lp, enums.AnalogCutoffFreq)
		self._core.io.write(f'TRIGger:ANEDge:CUToff:LOWPass {param}')

	# noinspection PyTypeChecker
	def get_highpass(self) -> enums.AnalogCutoffFreq:
		"""TRIGger:ANEDge:CUToff:HIGHpass \n
		Snippet: value: enums.AnalogCutoffFreq = driver.trigger.anEdge.cutoff.get_highpass() \n
		Frequencies below the cutoff frequency are rejected, higher frequencies pass the filter. \n
			:return: analog_cutoff_hp: No help available
		"""
		response = self._core.io.query_str('TRIGger:ANEDge:CUToff:HIGHpass?')
		return Conversions.str_to_scalar_enum(response, enums.AnalogCutoffFreq)

	def set_highpass(self, analog_cutoff_hp: enums.AnalogCutoffFreq) -> None:
		"""TRIGger:ANEDge:CUToff:HIGHpass \n
		Snippet: driver.trigger.anEdge.cutoff.set_highpass(analog_cutoff_hp = enums.AnalogCutoffFreq.KHZ5) \n
		Frequencies below the cutoff frequency are rejected, higher frequencies pass the filter. \n
			:param analog_cutoff_hp: KHZ5 = 5 kHz KHZ50 = 50 kHz
		"""
		param = Conversions.enum_scalar_to_str(analog_cutoff_hp, enums.AnalogCutoffFreq)
		self._core.io.write(f'TRIGger:ANEDge:CUToff:HIGHpass {param}')
