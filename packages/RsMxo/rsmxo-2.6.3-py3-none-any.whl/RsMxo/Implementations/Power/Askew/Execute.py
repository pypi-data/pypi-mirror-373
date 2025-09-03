from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ExecuteCls:
	"""Execute commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("execute", core, parent)

	def set(self, power=repcap.Power.Default, opc_timeout_ms: int = -1) -> None:
		"""POWer<*>:ASKew[:EXECute] \n
		Snippet: driver.power.askew.execute.set(power = repcap.Power.Default) \n
		Performs auto deskew adjustment. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write_with_opc(f'POWer{power_cmd_val}:ASKew:EXECute', opc_timeout_ms)
		# OpcSyncAllowed = true
