from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StypeCls:
	"""Stype commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("stype", core, parent)

	# noinspection PyTypeChecker
	def get(self, math=repcap.Math.Default) -> enums.MathSignalType:
		"""CALCulate:MATH<m>:DATA:STYPe \n
		Snippet: value: enums.MathSignalType = driver.calculate.math.data.stype.get(math = repcap.Math.Default) \n
		Returns the signal type of the source of the math waveform. \n
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
			:return: signal_type: SOURce = normal signal CORRelation = correlated signal, specific math signal MEAsurement = result of a measurement NONE = undefined"""
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		response = self._core.io.query_str(f'CALCulate:MATH{math_cmd_val}:DATA:STYPe?')
		return Conversions.str_to_scalar_enum(response, enums.MathSignalType)
