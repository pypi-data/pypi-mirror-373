from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, source: enums.Source, maskTest=repcap.MaskTest.Default) -> None:
		"""MTESt<*>:SOURce \n
		Snippet: driver.mtest.source.set(source = enums.Source.C1, maskTest = repcap.MaskTest.Default) \n
		Selects the waveform to be tested against the mask. \n
			:param source: No help available
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
		"""
		param = Conversions.enum_scalar_to_str(source, enums.Source)
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, maskTest=repcap.MaskTest.Default) -> enums.Source:
		"""MTESt<*>:SOURce \n
		Snippet: value: enums.Source = driver.mtest.source.get(maskTest = repcap.MaskTest.Default) \n
		Selects the waveform to be tested against the mask. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:return: source: No help available"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		response = self._core.io.query_str(f'MTESt{maskTest_cmd_val}:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.Source)
