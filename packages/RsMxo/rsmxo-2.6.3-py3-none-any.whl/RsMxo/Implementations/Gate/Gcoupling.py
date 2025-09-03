from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GcouplingCls:
	"""Gcoupling commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gcoupling", core, parent)

	def set(self, coupling_mode: enums.CouplingMode, gate=repcap.Gate.Default) -> None:
		"""GATE<*>:GCOupling \n
		Snippet: driver.gate.gcoupling.set(coupling_mode = enums.CouplingMode.CURSor, gate = repcap.Gate.Default) \n
		The gate coupling mode selects how the gate area is defined. \n
			:param coupling_mode:
				- MANual: Manually define the gate with a user-defined start and stop values.
				- CURSor: Cursor coupling is available if a cursor is defined. The gate area is defined by the cursor lines of an active cursor measurement.
				- ZOOM: Zoom coupling is available if a zoom is defined. The gate area is defined identically to the zoom area - if you change the zoom, the gate changes as well.
				- SPECtrum: Spectrum coupling is available if a spectrum is enabled.
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')"""
		param = Conversions.enum_scalar_to_str(coupling_mode, enums.CouplingMode)
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		self._core.io.write(f'GATE{gate_cmd_val}:GCOupling {param}')

	# noinspection PyTypeChecker
	def get(self, gate=repcap.Gate.Default) -> enums.CouplingMode:
		"""GATE<*>:GCOupling \n
		Snippet: value: enums.CouplingMode = driver.gate.gcoupling.get(gate = repcap.Gate.Default) \n
		The gate coupling mode selects how the gate area is defined. \n
			:param gate: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Gate')
			:return: coupling_mode:
				- MANual: Manually define the gate with a user-defined start and stop values.
				- CURSor: Cursor coupling is available if a cursor is defined. The gate area is defined by the cursor lines of an active cursor measurement.
				- ZOOM: Zoom coupling is available if a zoom is defined. The gate area is defined identically to the zoom area - if you change the zoom, the gate changes as well.
				- SPECtrum: Spectrum coupling is available if a spectrum is enabled."""
		gate_cmd_val = self._cmd_group.get_repcap_cmd_value(gate, repcap.Gate)
		response = self._core.io.query_str(f'GATE{gate_cmd_val}:GCOupling?')
		return Conversions.str_to_scalar_enum(response, enums.CouplingMode)
