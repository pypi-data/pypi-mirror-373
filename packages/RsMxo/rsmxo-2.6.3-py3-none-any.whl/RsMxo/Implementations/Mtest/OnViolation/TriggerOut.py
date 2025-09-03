from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TriggerOutCls:
	"""TriggerOut commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("triggerOut", core, parent)

	def set(self, trig_out_pls: enums.TriggerAction, maskTest=repcap.MaskTest.Default) -> None:
		"""MTESt<*>:ONViolation:TRIGgerout \n
		Snippet: driver.mtest.onViolation.triggerOut.set(trig_out_pls = enums.TriggerAction.NOACtion, maskTest = repcap.MaskTest.Default) \n
		Sends an outgoing pulse to the Trigger Out connector if the command is set to SUCCess or VIOLation.
			INTRO_CMD_HELP: To configure the pulse, user the following commands: \n
			- method RsMxo.Trigger.Actions.Out.source
			- method RsMxo.Trigger.Actions.Out.polarity
			- method RsMxo.Trigger.Actions.Out.delay
			- method RsMxo.Trigger.Actions.Out.plength  \n
			:param trig_out_pls: No help available
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
		"""
		param = Conversions.enum_scalar_to_str(trig_out_pls, enums.TriggerAction)
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:ONViolation:TRIGgerout {param}')

	# noinspection PyTypeChecker
	def get(self, maskTest=repcap.MaskTest.Default) -> enums.TriggerAction:
		"""MTESt<*>:ONViolation:TRIGgerout \n
		Snippet: value: enums.TriggerAction = driver.mtest.onViolation.triggerOut.get(maskTest = repcap.MaskTest.Default) \n
		Sends an outgoing pulse to the Trigger Out connector if the command is set to SUCCess or VIOLation.
			INTRO_CMD_HELP: To configure the pulse, user the following commands: \n
			- method RsMxo.Trigger.Actions.Out.source
			- method RsMxo.Trigger.Actions.Out.polarity
			- method RsMxo.Trigger.Actions.Out.delay
			- method RsMxo.Trigger.Actions.Out.plength  \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:return: trig_out_pls: No help available"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:ONViolation:TRIGgerout?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerAction)
