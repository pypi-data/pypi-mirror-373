from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValuesCls:
	"""Values commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("values", core, parent)

	def get(self, pwrBus=repcap.PwrBus.Default) -> bytes:
		"""PBUS<*>:DATA[:VALues] \n
		Snippet: value: bytes = driver.pbus.data.values.get(pwrBus = repcap.PwrBus.Default) \n
		Returns the data of the indicated logic. Without parameters, the complete waveform is retrieved. Using the offset and
		length parameters, data can be retrieved in smaller portions, which makes the command faster. If you send only one
		parameter, it is interpreted as offset, and the data is retrieved from offset to the end of the waveform.
			INTRO_CMD_HELP: Requirements: \n
			- method RsMxo.Pbus.State.set is set to ON.
			- method RsMxo.Pbus.Display.Shbu.set is set to ON.
			- A number format is set with method RsMxo.Pbus.Data.FormatPy.set.  \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: data: List of values according to the format and content settings."""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_bin_block_ERROR(f'PBUS{pwrBus_cmd_val}:DATA:VALues?')
		return response
