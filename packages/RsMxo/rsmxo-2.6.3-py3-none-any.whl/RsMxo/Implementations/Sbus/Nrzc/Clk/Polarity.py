from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PolarityCls:
	"""Polarity commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("polarity", core, parent)

	def set(self, clk_polarity: enums.Edge, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:NRZC:CLK:POLarity \n
		Snippet: driver.sbus.nrzc.clk.polarity.set(clk_polarity = enums.Edge.BOTH, serialBus = repcap.SerialBus.Default) \n
		Sets the polarity for the data line. \n
			:param clk_polarity:
				- RISE: Data is sampled at the rising edges of the clock signal.
				- FALL: Data is sampled at the falling edges of the clock signal.
				- BOTH: Data is sampled at the rising and falling edges of the clock signal.
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')"""
		param = Conversions.enum_scalar_to_str(clk_polarity, enums.Edge)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZC:CLK:POLarity {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.Edge:
		"""SBUS<*>:NRZC:CLK:POLarity \n
		Snippet: value: enums.Edge = driver.sbus.nrzc.clk.polarity.get(serialBus = repcap.SerialBus.Default) \n
		Sets the polarity for the data line. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: clk_polarity:
				- RISE: Data is sampled at the rising edges of the clock signal.
				- FALL: Data is sampled at the falling edges of the clock signal.
				- BOTH: Data is sampled at the rising and falling edges of the clock signal."""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZC:CLK:POLarity?')
		return Conversions.str_to_scalar_enum(response, enums.Edge)
