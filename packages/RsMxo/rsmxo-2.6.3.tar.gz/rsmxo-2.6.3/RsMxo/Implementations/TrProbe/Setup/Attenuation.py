from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AttenuationCls:
	"""Attenuation commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("attenuation", core, parent)

	def get_auto(self) -> float:
		"""TRPRobe:SETup:ATTenuation[:AUTO] \n
		Snippet: value: float = driver.trProbe.setup.attenuation.get_auto() \n
		Returns the attenuation of the probe that is connected to the external trigger input. \n
			:return: prb_att_md_auto: No help available
		"""
		response = self._core.io.query_str('TRPRobe:SETup:ATTenuation:AUTO?')
		return Conversions.str_to_float(response)

	# noinspection PyTypeChecker
	def get_unit(self) -> enums.ProbeAttUnits:
		"""TRPRobe:SETup:ATTenuation:UNIT \n
		Snippet: value: enums.ProbeAttUnits = driver.trProbe.setup.attenuation.get_unit() \n
		Returns the unit of the probe that is connected to the external trigger input. \n
			:return: prb_att_unt: No help available
		"""
		response = self._core.io.query_str('TRPRobe:SETup:ATTenuation:UNIT?')
		return Conversions.str_to_scalar_enum(response, enums.ProbeAttUnits)
