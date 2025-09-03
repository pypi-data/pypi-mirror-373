from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnvSelectionCls:
	"""EnvSelection commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("envSelection", core, parent)

	def set(self, envelope_curve: enums.EnvelopeCurve, math=repcap.Math.Default) -> None:
		"""CALCulate:MATH<*>:ENVSelection \n
		Snippet: driver.calculate.math.envSelection.set(envelope_curve = enums.EnvelopeCurve.BOTH, math = repcap.Math.Default) \n
		Selects the upper or lower part of the input waveform for mathematic calculation, or a combination of both. \n
			:param envelope_curve: No help available
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
		"""
		param = Conversions.enum_scalar_to_str(envelope_curve, enums.EnvelopeCurve)
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		self._core.io.write(f'CALCulate:MATH{math_cmd_val}:ENVSelection {param}')

	# noinspection PyTypeChecker
	def get(self, math=repcap.Math.Default) -> enums.EnvelopeCurve:
		"""CALCulate:MATH<*>:ENVSelection \n
		Snippet: value: enums.EnvelopeCurve = driver.calculate.math.envSelection.get(math = repcap.Math.Default) \n
		Selects the upper or lower part of the input waveform for mathematic calculation, or a combination of both. \n
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
			:return: envelope_curve: No help available"""
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		response = self._core.io.query_str(f'CALCulate:MATH{math_cmd_val}:ENVSelection?')
		return Conversions.str_to_scalar_enum(response, enums.EnvelopeCurve)
