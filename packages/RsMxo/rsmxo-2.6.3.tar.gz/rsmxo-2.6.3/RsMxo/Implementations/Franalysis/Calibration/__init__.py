from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CalibrationCls:
	"""Calibration commands group definition. 3 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("calibration", core, parent)

	@property
	def calibration(self):
		"""calibration commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_calibration'):
			from .Calibration import CalibrationCls
			self._calibration = CalibrationCls(self._core, self._cmd_group)
		return self._calibration

	def get_state(self) -> bool:
		"""FRANalysis:CALibration:STATe \n
		Snippet: value: bool = driver.franalysis.calibration.get_state() \n
		If ON, the user calibration data is used for the frequency response analysis. \n
			:return: use_calibration_dat: No help available
		"""
		response = self._core.io.query_str('FRANalysis:CALibration:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, use_calibration_dat: bool) -> None:
		"""FRANalysis:CALibration:STATe \n
		Snippet: driver.franalysis.calibration.set_state(use_calibration_dat = False) \n
		If ON, the user calibration data is used for the frequency response analysis. \n
			:param use_calibration_dat: No help available
		"""
		param = Conversions.bool_to_str(use_calibration_dat)
		self._core.io.write(f'FRANalysis:CALibration:STATe {param}')

	# noinspection PyTypeChecker
	def get_result(self) -> enums.FrAnalysisCalStates:
		"""FRANalysis:CALibration:RESult \n
		Snippet: value: enums.FrAnalysisCalStates = driver.franalysis.calibration.get_result() \n
		Returns the result of the calibration. \n
			:return: states: PASS: the calibration is successful. FAIL: the calibration failed. RUN: a calibration cycle is running. NOAL: no active calibration.
		"""
		response = self._core.io.query_str('FRANalysis:CALibration:RESult?')
		return Conversions.str_to_scalar_enum(response, enums.FrAnalysisCalStates)

	def clone(self) -> 'CalibrationCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = CalibrationCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
