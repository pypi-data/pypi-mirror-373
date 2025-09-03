from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StopCls:
	"""Stop commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("stop", core, parent)

	def set(self, stop_acq: enums.TriggerAction, maskTest=repcap.MaskTest.Default) -> None:
		"""MTESt<*>:ONViolation:STOP \n
		Snippet: driver.mtest.onViolation.stop.set(stop_acq = enums.TriggerAction.NOACtion, maskTest = repcap.MaskTest.Default) \n
		Stops the running acquisition if the command is set to SUCCess or VIOLation. \n
			:param stop_acq: No help available
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
		"""
		param = Conversions.enum_scalar_to_str(stop_acq, enums.TriggerAction)
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:ONViolation:STOP {param}')

	# noinspection PyTypeChecker
	def get(self, maskTest=repcap.MaskTest.Default) -> enums.TriggerAction:
		"""MTESt<*>:ONViolation:STOP \n
		Snippet: value: enums.TriggerAction = driver.mtest.onViolation.stop.get(maskTest = repcap.MaskTest.Default) \n
		Stops the running acquisition if the command is set to SUCCess or VIOLation. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:return: stop_acq: No help available"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:ONViolation:STOP?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerAction)
