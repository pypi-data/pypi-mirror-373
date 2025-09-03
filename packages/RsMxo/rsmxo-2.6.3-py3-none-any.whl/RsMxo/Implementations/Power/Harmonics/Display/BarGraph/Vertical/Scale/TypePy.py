from ........Internal.Core import Core
from ........Internal.CommandsGroup import CommandsGroup
from ........Internal import Conversions
from ........ import enums
from ........ import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	def set(self, scaling: enums.AxisMode, power=repcap.Power.Default) -> None:
		"""POWer<*>:HARMonics:DISPlay:BARGraph:VERTical:SCALe:TYPE \n
		Snippet: driver.power.harmonics.display.barGraph.vertical.scale.typePy.set(scaling = enums.AxisMode.LIN, power = repcap.Power.Default) \n
		Selects a logarithmic or linear scale for the display for the harmonics bargraph. \n
			:param scaling: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(scaling, enums.AxisMode)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:DISPlay:BARGraph:VERTical:SCALe:TYPE {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.AxisMode:
		"""POWer<*>:HARMonics:DISPlay:BARGraph:VERTical:SCALe:TYPE \n
		Snippet: value: enums.AxisMode = driver.power.harmonics.display.barGraph.vertical.scale.typePy.get(power = repcap.Power.Default) \n
		Selects a logarithmic or linear scale for the display for the harmonics bargraph. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: scaling: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:DISPlay:BARGraph:VERTical:SCALe:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.AxisMode)
