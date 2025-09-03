from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SetupCls:
	"""Setup commands group definition. 5 total commands, 1 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("setup", core, parent)

	@property
	def attenuation(self):
		"""attenuation commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_attenuation'):
			from .Attenuation import AttenuationCls
			self._attenuation = AttenuationCls(self._core, self._cmd_group)
		return self._attenuation

	def get_name(self) -> str:
		"""TRPRobe:SETup:NAME \n
		Snippet: value: str = driver.trProbe.setup.get_name() \n
		Returns the name of the probe that is connected to the external trigger input. \n
			:return: name: String parameter
		"""
		response = self._core.io.query_str('TRPRobe:SETup:NAME?')
		return trim_str_response(response)

	# noinspection PyTypeChecker
	def get_state(self) -> enums.Detection:
		"""TRPRobe:SETup:STATe \n
		Snippet: value: enums.Detection = driver.trProbe.setup.get_state() \n
		Returns the state of the probe that is connected to the external trigger input. \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('TRPRobe:SETup:STATe?')
		return Conversions.str_to_scalar_enum(response, enums.Detection)

	def get_type_py(self) -> str:
		"""TRPRobe:SETup:TYPE \n
		Snippet: value: str = driver.trProbe.setup.get_type_py() \n
		Returns the type of the probe that is connected to the external trigger input. \n
			:return: type_py: String parameter
		"""
		response = self._core.io.query_str('TRPRobe:SETup:TYPE?')
		return trim_str_response(response)

	def clone(self) -> 'SetupCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SetupCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
