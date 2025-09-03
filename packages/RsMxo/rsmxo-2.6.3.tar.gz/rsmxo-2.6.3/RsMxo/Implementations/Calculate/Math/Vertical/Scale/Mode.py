from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, vertical_scale_mode: enums.AutoManualMode, math=repcap.Math.Default) -> None:
		"""CALCulate:MATH<*>:VERTical:SCALe:MODE \n
		Snippet: driver.calculate.math.vertical.scale.mode.set(vertical_scale_mode = enums.AutoManualMode.AUTO, math = repcap.Math.Default) \n
		Sets how the vertical scale is adapted to the current measurement results. By default, scaling is done automatically to
		provide an optimal display. However, if necessary, you can define scaling values manually to suit your requirements. \n
			:param vertical_scale_mode: No help available
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
		"""
		param = Conversions.enum_scalar_to_str(vertical_scale_mode, enums.AutoManualMode)
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		self._core.io.write(f'CALCulate:MATH{math_cmd_val}:VERTical:SCALe:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, math=repcap.Math.Default) -> enums.AutoManualMode:
		"""CALCulate:MATH<*>:VERTical:SCALe:MODE \n
		Snippet: value: enums.AutoManualMode = driver.calculate.math.vertical.scale.mode.get(math = repcap.Math.Default) \n
		Sets how the vertical scale is adapted to the current measurement results. By default, scaling is done automatically to
		provide an optimal display. However, if necessary, you can define scaling values manually to suit your requirements. \n
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
			:return: vertical_scale_mode: No help available"""
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		response = self._core.io.query_str(f'CALCulate:MATH{math_cmd_val}:VERTical:SCALe:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AutoManualMode)
