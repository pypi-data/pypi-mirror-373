from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class WfmSaveCls:
	"""WfmSave commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("wfmSave", core, parent)

	def set(self, save_wfm: enums.TriggerAction, maskTest=repcap.MaskTest.Default) -> None:
		"""MTESt<*>:ONViolation:WFMSave \n
		Snippet: driver.mtest.onViolation.wfmSave.set(save_wfm = enums.TriggerAction.NOACtion, maskTest = repcap.MaskTest.Default) \n
		Saves the waveform data to file if the command is set to SUCCess or VIOLation.
			INTRO_CMD_HELP: To define the path and file names, use the EXPort:WAVeform:AUTonaming:* commands: \n
			- method RsMxo.Export.Waveform.AutoNaming.name
			- method RsMxo.Export.Waveform.AutoNaming.path
			- method RsMxo.Export.Waveform.AutoNaming.typePy  \n
			:param save_wfm: No help available
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
		"""
		param = Conversions.enum_scalar_to_str(save_wfm, enums.TriggerAction)
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:ONViolation:WFMSave {param}')

	# noinspection PyTypeChecker
	def get(self, maskTest=repcap.MaskTest.Default) -> enums.TriggerAction:
		"""MTESt<*>:ONViolation:WFMSave \n
		Snippet: value: enums.TriggerAction = driver.mtest.onViolation.wfmSave.get(maskTest = repcap.MaskTest.Default) \n
		Saves the waveform data to file if the command is set to SUCCess or VIOLation.
			INTRO_CMD_HELP: To define the path and file names, use the EXPort:WAVeform:AUTonaming:* commands: \n
			- method RsMxo.Export.Waveform.AutoNaming.name
			- method RsMxo.Export.Waveform.AutoNaming.path
			- method RsMxo.Export.Waveform.AutoNaming.typePy  \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:return: save_wfm: No help available"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:ONViolation:WFMSave?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerAction)
