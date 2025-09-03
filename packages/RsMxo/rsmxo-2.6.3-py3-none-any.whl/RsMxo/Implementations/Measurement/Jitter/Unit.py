from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UnitCls:
	"""Unit commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("unit", core, parent)

	def set(self, unit: enums.Unit, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:JITTer:UNIT \n
		Snippet: driver.measurement.jitter.unit.set(unit = enums.Unit.A, measIndex = repcap.MeasIndex.Default) \n
		Sets the unit for data rate measurements. \n
			:param unit: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.enum_scalar_to_str(unit, enums.Unit)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:JITTer:UNIT {param}')

	# noinspection PyTypeChecker
	def get(self, measIndex=repcap.MeasIndex.Default) -> enums.Unit:
		"""MEASurement<*>:JITTer:UNIT \n
		Snippet: value: enums.Unit = driver.measurement.jitter.unit.get(measIndex = repcap.MeasIndex.Default) \n
		Sets the unit for data rate measurements. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: unit: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:JITTer:UNIT?')
		return Conversions.str_to_scalar_enum(response, enums.Unit)
