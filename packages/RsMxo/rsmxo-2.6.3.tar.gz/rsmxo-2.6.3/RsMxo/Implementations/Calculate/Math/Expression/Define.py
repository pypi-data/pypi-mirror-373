from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DefineCls:
	"""Define commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("define", core, parent)

	def set(self, expression: str, math=repcap.Math.Default) -> None:
		"""CALCulate:MATH<*>[:EXPRession][:DEFine] \n
		Snippet: driver.calculate.math.expression.define.set(expression = 'abc', math = repcap.Math.Default) \n
		Defines the math expression to be calculated for the specified math channel.
			Table Header: Operation / <Expression> / Comment \n
			- Addition / 'C1+C2'
			- Subtraction / 'C1-C2'
			- Multiplication / 'C1*C2'
			- Division / 'C1/C2' / 0/0 = 0 +1 / 0 = Clip+ -1 / 0 = Clip
			- Inverting / '-C1'
			- Absolute value / 'Abs(C1) '
			- Derivation / 'Derivation(C1,NoiseReject) ' / NoiseReject can get any value between 1 and 5000 points Default = 50
			- Integral / 'Integral(C1) '
			- Logarithm (based on 10) / 'Log(C1) ' / Uses the absolute value of the source in calculation. Log(0) = Clip
			- Natural logarithm (based on e) / 'Ln(C1) ' / Uses the absolute value of the source in calculation. Log(0) = Clip
			- Binary logarithm (based on 2) / 'Ld(C1) ' / Uses the absolute value of the source in calculation. Log(0) = Clip
			- Square / 'Pow(C1) '
			- Square root / 'Sqrt(C1) ' / Uses the absolute value of the source in calculation.
			- Rescale / 'Rescale(C1,a,b) ' / a = scale, default = 1 b = offset, default = 0
			- FIR / 'FIR(Type,C1,Cut-Off,Characteristics) ' Examples: 'FIR(highpass,C1,10000000,Gaussian) ' 'FIR(lowpass,C1,10000000,rectangle) ' / Type = lowpass, highpass Cut-Off = limit frequency Characteristics = Gaussian, rectangle Cut-Off can get any value between 4 GHz and 1 kHz \n
			:param expression: String with regular expression for calculation
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
		"""
		param = Conversions.value_to_quoted_str(expression)
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		self._core.io.write(f'CALCulate:MATH{math_cmd_val}:EXPRession:DEFine {param}')

	def get(self, math=repcap.Math.Default) -> str:
		"""CALCulate:MATH<*>[:EXPRession][:DEFine] \n
		Snippet: value: str = driver.calculate.math.expression.define.get(math = repcap.Math.Default) \n
		Defines the math expression to be calculated for the specified math channel.
			Table Header: Operation / <Expression> / Comment \n
			- Addition / 'C1+C2'
			- Subtraction / 'C1-C2'
			- Multiplication / 'C1*C2'
			- Division / 'C1/C2' / 0/0 = 0 +1 / 0 = Clip+ -1 / 0 = Clip
			- Inverting / '-C1'
			- Absolute value / 'Abs(C1) '
			- Derivation / 'Derivation(C1,NoiseReject) ' / NoiseReject can get any value between 1 and 5000 points Default = 50
			- Integral / 'Integral(C1) '
			- Logarithm (based on 10) / 'Log(C1) ' / Uses the absolute value of the source in calculation. Log(0) = Clip
			- Natural logarithm (based on e) / 'Ln(C1) ' / Uses the absolute value of the source in calculation. Log(0) = Clip
			- Binary logarithm (based on 2) / 'Ld(C1) ' / Uses the absolute value of the source in calculation. Log(0) = Clip
			- Square / 'Pow(C1) '
			- Square root / 'Sqrt(C1) ' / Uses the absolute value of the source in calculation.
			- Rescale / 'Rescale(C1,a,b) ' / a = scale, default = 1 b = offset, default = 0
			- FIR / 'FIR(Type,C1,Cut-Off,Characteristics) ' Examples: 'FIR(highpass,C1,10000000,Gaussian) ' 'FIR(lowpass,C1,10000000,rectangle) ' / Type = lowpass, highpass Cut-Off = limit frequency Characteristics = Gaussian, rectangle Cut-Off can get any value between 4 GHz and 1 kHz \n
			:param math: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Math')
			:return: expression: String with regular expression for calculation"""
		math_cmd_val = self._cmd_group.get_repcap_cmd_value(math, repcap.Math)
		response = self._core.io.query_str(f'CALCulate:MATH{math_cmd_val}:EXPRession:DEFine?')
		return trim_str_response(response)
