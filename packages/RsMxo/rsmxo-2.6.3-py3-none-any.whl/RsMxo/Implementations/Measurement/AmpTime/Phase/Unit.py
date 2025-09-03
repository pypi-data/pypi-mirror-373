from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UnitCls:
	"""Unit commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("unit", core, parent)

	def set(self, phase_mode: enums.PhaseMode, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:AMPTime:PHASe:UNIT \n
		Snippet: driver.measurement.ampTime.phase.unit.set(phase_mode = enums.PhaseMode.DEGRees, measIndex = repcap.MeasIndex.Default) \n
		No command help available \n
			:param phase_mode: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.enum_scalar_to_str(phase_mode, enums.PhaseMode)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:AMPTime:PHASe:UNIT {param}')

	# noinspection PyTypeChecker
	def get(self, measIndex=repcap.MeasIndex.Default) -> enums.PhaseMode:
		"""MEASurement<*>:AMPTime:PHASe:UNIT \n
		Snippet: value: enums.PhaseMode = driver.measurement.ampTime.phase.unit.get(measIndex = repcap.MeasIndex.Default) \n
		No command help available \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: phase_mode: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:AMPTime:PHASe:UNIT?')
		return Conversions.str_to_scalar_enum(response, enums.PhaseMode)
