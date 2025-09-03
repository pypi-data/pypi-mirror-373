from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CslopeCls:
	"""Cslope commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cslope", core, parent)

	def set(self, set_hold_clk_slp: enums.PulseSlope, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:AMPTime:CSLope \n
		Snippet: driver.measurement.ampTime.cslope.set(set_hold_clk_slp = enums.PulseSlope.EITHer, measIndex = repcap.MeasIndex.Default) \n
		Sets the edge of the clock from which the setup and hold times are measured. \n
			:param set_hold_clk_slp: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.enum_scalar_to_str(set_hold_clk_slp, enums.PulseSlope)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:AMPTime:CSLope {param}')

	# noinspection PyTypeChecker
	def get(self, measIndex=repcap.MeasIndex.Default) -> enums.PulseSlope:
		"""MEASurement<*>:AMPTime:CSLope \n
		Snippet: value: enums.PulseSlope = driver.measurement.ampTime.cslope.get(measIndex = repcap.MeasIndex.Default) \n
		Sets the edge of the clock from which the setup and hold times are measured. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: set_hold_clk_slp: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:AMPTime:CSLope?')
		return Conversions.str_to_scalar_enum(response, enums.PulseSlope)
