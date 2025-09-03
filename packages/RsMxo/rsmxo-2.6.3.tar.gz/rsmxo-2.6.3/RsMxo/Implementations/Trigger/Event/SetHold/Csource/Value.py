from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValueCls:
	"""Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("value", core, parent)

	def set(self, clock_source: enums.SourceDetailed, evnt=repcap.Evnt.Default) -> None:
		"""TRIGger:EVENt<*>:SETHold:CSOurce[:VALue] \n
		Snippet: driver.trigger.event.setHold.csource.value.set(clock_source = enums.SourceDetailed.C1, evnt = repcap.Evnt.Default) \n
		Selects the input channel of the clock signal. \n
			:param clock_source: The following values are also accepted: C1 = CHAN1 = CHANnel1, C2 = CHAN2 = CHANnel2, C3 = CHAN3 = CHANnel3, C4 = CHAN4 = CHANnel4
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
		"""
		param = Conversions.enum_scalar_to_str(clock_source, enums.SourceDetailed)
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		self._core.io.write(f'TRIGger:EVENt{evnt_cmd_val}:SETHold:CSOurce:VALue {param}')

	# noinspection PyTypeChecker
	def get(self, evnt=repcap.Evnt.Default) -> enums.SourceDetailed:
		"""TRIGger:EVENt<*>:SETHold:CSOurce[:VALue] \n
		Snippet: value: enums.SourceDetailed = driver.trigger.event.setHold.csource.value.get(evnt = repcap.Evnt.Default) \n
		Selects the input channel of the clock signal. \n
			:param evnt: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Event')
			:return: clock_source: The following values are also accepted: C1 = CHAN1 = CHANnel1, C2 = CHAN2 = CHANnel2, C3 = CHAN3 = CHANnel3, C4 = CHAN4 = CHANnel4"""
		evnt_cmd_val = self._cmd_group.get_repcap_cmd_value(evnt, repcap.Evnt)
		response = self._core.io.query_str(f'TRIGger:EVENt{evnt_cmd_val}:SETHold:CSOurce:VALue?')
		return Conversions.str_to_scalar_enum(response, enums.SourceDetailed)
