from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, enable: bool, error=repcap.Error.Default) -> None:
		"""TRIGger:SBSW:I2C:ERRor<*>:ENABle \n
		Snippet: driver.trigger.sbsw.i2C.error.enable.set(enable = False, error = repcap.Error.Default) \n
		Defines the error type for the software trigger. \n
			:param enable: No help available
			:param error: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Error')
		"""
		param = Conversions.bool_to_str(enable)
		error_cmd_val = self._cmd_group.get_repcap_cmd_value(error, repcap.Error)
		self._core.io.write(f'TRIGger:SBSW:I2C:ERRor{error_cmd_val}:ENABle {param}')

	def get(self, error=repcap.Error.Default) -> bool:
		"""TRIGger:SBSW:I2C:ERRor<*>:ENABle \n
		Snippet: value: bool = driver.trigger.sbsw.i2C.error.enable.get(error = repcap.Error.Default) \n
		Defines the error type for the software trigger. \n
			:param error: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Error')
			:return: enable: No help available"""
		error_cmd_val = self._cmd_group.get_repcap_cmd_value(error, repcap.Error)
		response = self._core.io.query_str(f'TRIGger:SBSW:I2C:ERRor{error_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)
