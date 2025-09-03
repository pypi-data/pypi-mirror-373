from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ScreenshotCls:
	"""Screenshot commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("screenshot", core, parent)

	def set(self, save_screenshot: enums.TriggerAction, maskTest=repcap.MaskTest.Default) -> None:
		"""MTESt<*>:ONViolation:SCReenshot \n
		Snippet: driver.mtest.onViolation.screenshot.set(save_screenshot = enums.TriggerAction.NOACtion, maskTest = repcap.MaskTest.Default) \n
		Saves the waveform data to file if the command is set to SUCCess or VIOLation. To configure the screenshot settings, use
		the commands described in 'Screenshots'. \n
			:param save_screenshot: No help available
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
		"""
		param = Conversions.enum_scalar_to_str(save_screenshot, enums.TriggerAction)
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:ONViolation:SCReenshot {param}')

	# noinspection PyTypeChecker
	def get(self, maskTest=repcap.MaskTest.Default) -> enums.TriggerAction:
		"""MTESt<*>:ONViolation:SCReenshot \n
		Snippet: value: enums.TriggerAction = driver.mtest.onViolation.screenshot.get(maskTest = repcap.MaskTest.Default) \n
		Saves the waveform data to file if the command is set to SUCCess or VIOLation. To configure the screenshot settings, use
		the commands described in 'Screenshots'. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:return: save_screenshot: No help available"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:ONViolation:SCReenshot?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerAction)
