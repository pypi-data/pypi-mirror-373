from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class InstructionCls:
	"""Instruction commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("instruction", core, parent)

	def set(self, instruction: enums.SbusQspiInstruction, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:QSPI:INSTruction \n
		Snippet: driver.sbus.qspi.instruction.set(instruction = enums.SbusQspiInstruction.DUAL, serialBus = repcap.SerialBus.Default) \n
		Selects the instruction mode that defines how many lanes are used to transmit data. \n
			:param instruction: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.enum_scalar_to_str(instruction, enums.SbusQspiInstruction)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:INSTruction {param}')

	# noinspection PyTypeChecker
	def get(self, serialBus=repcap.SerialBus.Default) -> enums.SbusQspiInstruction:
		"""SBUS<*>:QSPI:INSTruction \n
		Snippet: value: enums.SbusQspiInstruction = driver.sbus.qspi.instruction.get(serialBus = repcap.SerialBus.Default) \n
		Selects the instruction mode that defines how many lanes are used to transmit data. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: instruction: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:INSTruction?')
		return Conversions.str_to_scalar_enum(response, enums.SbusQspiInstruction)
