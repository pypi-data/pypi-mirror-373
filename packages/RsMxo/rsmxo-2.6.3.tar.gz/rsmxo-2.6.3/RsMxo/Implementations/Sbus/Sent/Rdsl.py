from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RdslCls:
	"""Rdsl commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rdsl", core, parent)

	def set(self, ress_disp_sel: enums.SbusSentResultDisplay, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SENT:RDSL \n
		Snippet: driver.sbus.sent.rdsl.set(ress_disp_sel = enums.SbusSentResultDisplay.ALL, serialBus = repcap.SerialBus.Default) \n
		Selects the results to be displayed. \n
			:param ress_disp_sel: TRSQ: transmission sequence SMSG: serial messages
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(ress_disp_sel, enums.SbusSentResultDisplay)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SENT:RDSL {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusSentResultDisplay:
		"""SBUS<*>:SENT:RDSL \n
		Snippet: value: enums.SbusSentResultDisplay = driver.sbus.sent.rdsl.get(serialBus = repcap.SerialBus.Default) \n
		Selects the results to be displayed. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: ress_disp_sel: TRSQ: transmission sequence SMSG: serial messages"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SENT:RDSL?')
		return Conversions.str_to_scalar_enum(response, enums.SbusSentResultDisplay)
