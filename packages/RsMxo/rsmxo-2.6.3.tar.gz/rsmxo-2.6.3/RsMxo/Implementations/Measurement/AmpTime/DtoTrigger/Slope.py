from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SlopeCls:
	"""Slope commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("slope", core, parent)

	def set(self, dly_trig_slp: enums.PulseSlope, measIndex=repcap.MeasIndex.Default, dtoTrigger=repcap.DtoTrigger.Default) -> None:
		"""MEASurement<*>:AMPTime:DTOTrigger<*>:SLOPe \n
		Snippet: driver.measurement.ampTime.dtoTrigger.slope.set(dly_trig_slp = enums.PulseSlope.EITHer, measIndex = repcap.MeasIndex.Default, dtoTrigger = repcap.DtoTrigger.Default) \n
		Sets the edge direction to be used for delay measurement. \n
			:param dly_trig_slp: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param dtoTrigger: optional repeated capability selector. Default value: Nr1 (settable in the interface 'DtoTrigger')
		"""
		param = Conversions.enum_scalar_to_str(dly_trig_slp, enums.PulseSlope)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		dtoTrigger_cmd_val = self._cmd_group.get_repcap_cmd_value(dtoTrigger, repcap.DtoTrigger)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:AMPTime:DTOTrigger{dtoTrigger_cmd_val}:SLOPe {param}')

	# noinspection PyTypeChecker
	def get(self, measIndex=repcap.MeasIndex.Default, dtoTrigger=repcap.DtoTrigger.Default) -> enums.PulseSlope:
		"""MEASurement<*>:AMPTime:DTOTrigger<*>:SLOPe \n
		Snippet: value: enums.PulseSlope = driver.measurement.ampTime.dtoTrigger.slope.get(measIndex = repcap.MeasIndex.Default, dtoTrigger = repcap.DtoTrigger.Default) \n
		Sets the edge direction to be used for delay measurement. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param dtoTrigger: optional repeated capability selector. Default value: Nr1 (settable in the interface 'DtoTrigger')
			:return: dly_trig_slp: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		dtoTrigger_cmd_val = self._cmd_group.get_repcap_cmd_value(dtoTrigger, repcap.DtoTrigger)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:AMPTime:DTOTrigger{dtoTrigger_cmd_val}:SLOPe?')
		return Conversions.str_to_scalar_enum(response, enums.PulseSlope)
