from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SkewCls:
	"""Skew commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("skew", core, parent)

	def set(self, skew: float, pwrBus=repcap.PwrBus.Default, bit=repcap.Bit.Default) -> None:
		"""PBUS<*>:BIT<*>:SKEW \n
		Snippet: driver.pbus.bit.skew.set(skew = 1.0, pwrBus = repcap.PwrBus.Default, bit = repcap.Bit.Default) \n
		Sets an individual delay for each digital channel to time-align it with other digital channels.
		The skew value compensates delays that are known from the circuit specifics or caused by the different length of cables.
		The skew between the probe boxes of the digital channels and the probe connectors of the analog channels is automatically
		aligned by the instrument. \n
			:param skew: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:param bit: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Bit')
		"""
		param = Conversions.decimal_value_to_str(skew)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		bit_cmd_val = self._cmd_group.get_repcap_cmd_value(bit, repcap.Bit)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:BIT{bit_cmd_val}:SKEW {param}')

	def get(self, pwrBus=repcap.PwrBus.Default, bit=repcap.Bit.Default) -> float:
		"""PBUS<*>:BIT<*>:SKEW \n
		Snippet: value: float = driver.pbus.bit.skew.get(pwrBus = repcap.PwrBus.Default, bit = repcap.Bit.Default) \n
		Sets an individual delay for each digital channel to time-align it with other digital channels.
		The skew value compensates delays that are known from the circuit specifics or caused by the different length of cables.
		The skew between the probe boxes of the digital channels and the probe connectors of the analog channels is automatically
		aligned by the instrument. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:param bit: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Bit')
			:return: skew: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		bit_cmd_val = self._cmd_group.get_repcap_cmd_value(bit, repcap.Bit)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:BIT{bit_cmd_val}:SKEW?')
		return Conversions.str_to_float(response)
