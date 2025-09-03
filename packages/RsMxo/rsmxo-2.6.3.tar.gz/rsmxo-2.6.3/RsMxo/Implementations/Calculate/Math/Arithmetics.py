from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ArithmeticsCls:
	"""Arithmetics commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("arithmetics", core, parent)

	def set(self, arithmetics: enums.Arithmetics, math=repcap.Math.Default) -> None:
		"""CALCulate:MATH<*>:ARIThmetics \n
		Snippet: driver.calculate.math.arithmetics.set(arithmetics = enums.Arithmetics.AVERage, math = repcap.Math.Default) \n
		No command help available \n
			:param arithmetics: No help available
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
		"""
		param = Conversions.enum_scalar_to_str(arithmetics, enums.Arithmetics)
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		self._core.io.write(f'CALCulate:MATH{math_cmd_val}:ARIThmetics {param}')

	# noinspection PyTypeChecker
	def get(self, math=repcap.Math.Default) -> enums.Arithmetics:
		"""CALCulate:MATH<*>:ARIThmetics \n
		Snippet: value: enums.Arithmetics = driver.calculate.math.arithmetics.get(math = repcap.Math.Default) \n
		No command help available \n
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
			:return: arithmetics: No help available"""
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		response = self._core.io.query_str(f'CALCulate:MATH{math_cmd_val}:ARIThmetics?')
		return Conversions.str_to_scalar_enum(response, enums.Arithmetics)
