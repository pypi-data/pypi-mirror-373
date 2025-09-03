from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ProfileCls:
	"""Profile commands group definition. 7 total commands, 3 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("profile", core, parent)

	@property
	def sort(self):
		"""sort commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sort'):
			from .Sort import SortCls
			self._sort = SortCls(self._core, self._cmd_group)
		return self._sort

	@property
	def apoint(self):
		"""apoint commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_apoint'):
			from .Apoint import ApointCls
			self._apoint = ApointCls(self._core, self._cmd_group)
		return self._apoint

	@property
	def point(self):
		"""point commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_point'):
			from .Point import PointCls
			self._point = PointCls(self._core, self._cmd_group)
		return self._point

	def get_count(self) -> int:
		"""FRANalysis:AMPLitude:PROFile:COUNt \n
		Snippet: value: int = driver.franalysis.amplitude.profile.get_count() \n
		Returns the number of defined points for the amplitude profile. \n
			:return: value: No help available
		"""
		response = self._core.io.query_str('FRANalysis:AMPLitude:PROFile:COUNt?')
		return Conversions.str_to_int(response)

	def set_count(self, value: int) -> None:
		"""FRANalysis:AMPLitude:PROFile:COUNt \n
		Snippet: driver.franalysis.amplitude.profile.set_count(value = 1) \n
		Returns the number of defined points for the amplitude profile. \n
			:param value: No help available
		"""
		param = Conversions.decimal_value_to_str(value)
		self._core.io.write(f'FRANalysis:AMPLitude:PROFile:COUNt {param}')

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.AmplitudeProfileVoltageChange:
		"""FRANalysis:AMPLitude:PROFile:MODE \n
		Snippet: value: enums.AmplitudeProfileVoltageChange = driver.franalysis.amplitude.profile.get_mode() \n
		Selects if the voltage change is done as a single step or as a ramp. \n
			:return: amplitude_profile_voltage_change: No help available
		"""
		response = self._core.io.query_str('FRANalysis:AMPLitude:PROFile:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AmplitudeProfileVoltageChange)

	def set_mode(self, amplitude_profile_voltage_change: enums.AmplitudeProfileVoltageChange) -> None:
		"""FRANalysis:AMPLitude:PROFile:MODE \n
		Snippet: driver.franalysis.amplitude.profile.set_mode(amplitude_profile_voltage_change = enums.AmplitudeProfileVoltageChange.RAMP) \n
		Selects if the voltage change is done as a single step or as a ramp. \n
			:param amplitude_profile_voltage_change: No help available
		"""
		param = Conversions.enum_scalar_to_str(amplitude_profile_voltage_change, enums.AmplitudeProfileVoltageChange)
		self._core.io.write(f'FRANalysis:AMPLitude:PROFile:MODE {param}')

	def clone(self) -> 'ProfileCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ProfileCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
