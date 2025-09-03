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

	def set(self, source: enums.Source, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:SOURce \n
		Snippet: driver.treference.source.set(source = enums.Source.C1, timingReference = repcap.TimingReference.Default) \n
		Selects the clock source if method RsMxo.Treference.TypePy.set is set. Sets the data source for clock data recovery if
		method RsMxo.Treference.TypePy.set is set for the indicated measurement. \n
			:param source: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.enum_scalar_to_str(source, enums.Source)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, timingReference=repcap.TimingReference.Default) -> enums.Source:
		"""TREFerence<*>:SOURce \n
		Snippet: value: enums.Source = driver.treference.source.get(timingReference = repcap.TimingReference.Default) \n
		Selects the clock source if method RsMxo.Treference.TypePy.set is set. Sets the data source for clock data recovery if
		method RsMxo.Treference.TypePy.set is set for the indicated measurement. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: source: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.Source)
