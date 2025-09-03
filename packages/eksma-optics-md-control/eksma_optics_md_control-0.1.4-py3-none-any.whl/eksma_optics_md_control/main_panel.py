from __future__ import annotations

import math
import traceback
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

import wx
import wx.dataview
from eksma_optics_motorized_devices.command import IdentificationValue, PresetValue, SystemFlagsValue
from eksma_optics_motorized_devices.control import Control
from eksma_optics_motorized_devices.transport import SerialTransport
from serial.tools.list_ports import comports

from eksma_optics_md_control._gui_base import MainPanel as _MainPanel
from eksma_optics_md_control.task import schedule_task

if TYPE_CHECKING:
    from eksma_optics_motorized_devices.decimal_with_dimension import DecimalWithDimension
    from serial.tools.list_ports_common import ListPortInfo

import logging

logger = logging.getLogger(__name__)


BUTTON_LABEL_CONNECT = "Connect"
BUTTON_LABEL_DISCONNECT = "Disconnect"
MENU_ITEM_LABEL_CONNECT = f"{BUTTON_LABEL_CONNECT}\tCtrl+K"
MENU_ITEM_LABEL_DISCONNECT = f"{BUTTON_LABEL_DISCONNECT}\tCtrl+K"
PRESET_COLUMN_MAGNIFICATION = "Magnification"
PRESET_COLUMN_COLLIMATION = "Collimation"

MAGNIFICATION_DEFAULT = 0
MAGNIFICATION_STEP_LARGE = 1.0
MAGNIFICATION_STEP_SMALL = 0.1

COLLIMATION_DEFAULT = 0
COLLIMATION_STEP = 1

CONTROL_ERROR = "control error"

COLOR_DARK_BLUE = (0x00, 0x42, 0x7A)
COLOR_WHITE = (0xFF, 0xFF, 0xFF)


class ControlError(TypeError):
    pass


class DeviceParametersError(TypeError):
    pass


@dataclass
class DeviceParameters:
    identification: IdentificationValue
    magnification_range: tuple[float, float]
    magnification: float
    collimation_range: tuple[int, int]
    collimation: int
    wavelengths: list[DecimalWithDimension]
    wavelength: DecimalWithDimension
    presets: list[PresetValue]
    preset_remaining: int
    flags: SystemFlagsValue


class State(str, Enum):
    DISCONNECTED = "DISCONNECTED"
    IDLE = "IDLE"
    PROCESSING_HOMING = "PROCESSING_HOMING"
    PROCESSING_MOVING = "PROCESSING_MOVING"


class MainPanel(_MainPanel):
    def __init__(self, parent: wx.Frame) -> None:
        super().__init__(parent)

        self._state = State.DISCONNECTED

        self._serial_ports: list[ListPortInfo] = []
        self._update_serial_ports()

        self._control: Control | None = None
        self._device_parameters: DeviceParameters | None = None

        self.dv_presets.AppendTextColumn(PRESET_COLUMN_MAGNIFICATION, flags=0)
        self.dv_presets.AppendTextColumn(PRESET_COLUMN_COLLIMATION, flags=0)

        self.SetBackgroundColour(COLOR_DARK_BLUE)

        self.label_serial_port.SetForegroundColour(COLOR_WHITE)
        self.label_wavelength.SetForegroundColour(COLOR_WHITE)
        self.label_magnification.SetForegroundColour(COLOR_WHITE)
        self.label_collimation.SetForegroundColour(COLOR_WHITE)

        self.label_line_wavelength.SetBackgroundColour(COLOR_WHITE)
        self.label_line_magnification.SetBackgroundColour(COLOR_WHITE)
        self.label_line_collimation.SetBackgroundColour(COLOR_WHITE)

        self.label_magnification_min.SetForegroundColour(COLOR_WHITE)
        self.label_magnification_max.SetForegroundColour(COLOR_WHITE)
        self.label_collimation_min.SetForegroundColour(COLOR_WHITE)
        self.label_collimation_max.SetForegroundColour(COLOR_WHITE)

        platform_information: wx.PlatformInformation = wx.PlatformInformation.Get()
        if platform_information.GetOperatingSystemId() == wx.OS_WINDOWS_NT:
            font: wx.Font = self.label_serial_port.GetFont()
            font.SetWeight(wx.FONTWEIGHT_SEMIBOLD)

            self.label_serial_port.SetFont(font)
            self.label_wavelength.SetFont(font)
            self.label_magnification.SetFont(font)
            self.label_collimation.SetFont(font)

            self.label_magnification_min.SetFont(font)
            self.label_magnification_max.SetFont(font)
            self.label_collimation_min.SetFont(font)
            self.label_collimation_max.SetFont(font)

    # MARK: Update UI

    def on_menu_update_ui(self, event: wx.UpdateUIEvent) -> None:
        enabled = self._state == State.IDLE
        event.Enable(enabled)

    def on_magnification_min_update_ui(self, event: wx.UpdateUIEvent) -> None:
        enabled = self._state != State.DISCONNECTED
        event.Enable(enabled)

        if self._device_parameters is None:
            event.SetText(str(MAGNIFICATION_DEFAULT))
            return

        event.SetText(str(self._device_parameters.magnification_range[0]))

    def on_magnification_max_update_ui(self, event: wx.UpdateUIEvent) -> None:
        enabled = self._state != State.DISCONNECTED
        event.Enable(enabled)

        if self._device_parameters is None:
            event.SetText(str(MAGNIFICATION_DEFAULT))
            return

        event.SetText(str(self._device_parameters.magnification_range[1]))

    def on_collimation_min_update_ui(self, event: wx.UpdateUIEvent) -> None:
        enabled = self._state != State.DISCONNECTED
        event.Enable(enabled)

        if self._device_parameters is None:
            event.SetText(str(COLLIMATION_DEFAULT))
            return

        event.SetText(str(self._device_parameters.collimation_range[0]))

    def on_collimation_max_update_ui(self, event: wx.UpdateUIEvent) -> None:
        enabled = self._state != State.DISCONNECTED
        event.Enable(enabled)

        if self._device_parameters is None:
            event.SetText(str(COLLIMATION_DEFAULT))
            return

        event.SetText(str(self._device_parameters.collimation_range[1]))

    def on_magnification_update_ui(self, event: wx.UpdateUIEvent) -> None:
        enabled = self._state != State.DISCONNECTED
        event.Enable(enabled)

        if self._device_parameters is None:
            event.SetText(str(COLLIMATION_DEFAULT))
            return

        event_object: wx.TextCtrl = event.GetEventObject()
        if event_object.IsModified():
            return

        event_object.SetValue(str(self._device_parameters.magnification))
        event_object.SetModified(modified=False)

    def on_collimation_update_ui(self, event: wx.UpdateUIEvent) -> None:
        enabled = self._state != State.DISCONNECTED
        event.Enable(enabled)

        if self._device_parameters is None:
            event.SetText(str(COLLIMATION_DEFAULT))
            return

        event_object: wx.TextCtrl = event.GetEventObject()
        if event_object.IsModified():
            return

        event_object.SetValue(str(self._device_parameters.collimation))
        event_object.SetModified(modified=False)

    def on_wavelength_update_ui(self, event: wx.UpdateUIEvent) -> None:
        enabled = self._state != State.DISCONNECTED
        event.Enable(enabled)

        event_object: wx.Choice = event.GetEventObject()

        if self._device_parameters is None:
            event_object.Clear()
            return

        wavelengths = self._device_parameters.wavelengths
        current_value = str(self._device_parameters.wavelength)

        if event_object.GetCount() != len(wavelengths):
            event_object.Clear()
            for wavelength in wavelengths:
                event_object.Append(str(wavelength), wavelength)

        if event_object.GetStringSelection() != current_value:
            event_object.SetStringSelection(current_value)

    def on_presets_update_ui(self, event: wx.UpdateUIEvent) -> None:
        enabled = self._state != State.DISCONNECTED
        event.Enable(enabled)

        # event.GetEventObject() on Windows is broken
        event_object = self.dv_presets
        item_count = event_object.GetItemCount()

        if self._device_parameters is None:
            if item_count > 0:
                event_object.DeleteAllItems()
            return

        presets = self._device_parameters.presets

        needs_refresh = False
        if item_count != len(presets):
            needs_refresh = True
        else:
            for i, preset in enumerate(presets):
                current_magnification = event_object.GetTextValue(i, 0)
                current_collimation = event_object.GetTextValue(i, 1)
                if current_magnification != str(preset.magnification) or current_collimation != str(preset.collimation):
                    needs_refresh = True
                    break

        if needs_refresh:
            event_object.DeleteAllItems()
            for preset in presets:
                event_object.AppendItem((str(preset.magnification), str(preset.collimation)), preset.id)

    def on_preset_add_update_ui(self, event: wx.UpdateUIEvent) -> None:
        enabled = self._state != State.DISCONNECTED

        if self._device_parameters is not None:
            enabled = enabled and self._device_parameters.preset_remaining > 0
        else:
            enabled = False

        event.Enable(enabled)

    def on_preset_remove_update_ui(self, event: wx.UpdateUIEvent) -> None:
        enabled = self._state != State.DISCONNECTED

        if self._device_parameters is not None:
            index = self.dv_presets.GetSelectedRow()
            enabled = index != wx.NOT_FOUND
        else:
            enabled = False

        event.Enable(enabled)

    def on_update_ui(self, event: wx.UpdateUIEvent) -> None:
        enabled = self._state != State.DISCONNECTED
        event.Enable(enabled)

    def on_timer(self, _event: wx.TimerEvent) -> None:
        self._update_serial_ports()

        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        if self._device_parameters is None:
            return

        schedule_task(self._update_flags_command_task, self._task_error, self._update_flags_command_resume)

    # MARK: Flags

    def _update_flags_command_task(self) -> SystemFlagsValue:
        if self._control is None:
            raise ControlError

        return self._control.get_flags()

    def _update_flags_command_resume(self, value: SystemFlagsValue) -> None:
        if self._device_parameters is None:
            raise DeviceParametersError

        self._device_parameters.flags = value

        if self._device_parameters.flags & SystemFlagsValue.STATE_CHANGED:
            self._state = State.PROCESSING_MOVING

            schedule_task(self._update_device_parameters_task, self._task_error, self._update_device_parameters_resume)

    # MARK: Connect

    def on_connect_click(self, _event: wx.CommandEvent) -> None:
        if self._state == State.DISCONNECTED:
            self._connect()
        else:
            self._disconnect()

    def on_connect_update_ui(self, event: wx.UpdateUIEvent) -> None:
        connected = self._state != State.DISCONNECTED

        if isinstance(event.GetEventObject(), wx.Menu):
            text = MENU_ITEM_LABEL_DISCONNECT if connected else MENU_ITEM_LABEL_CONNECT
        elif connected:
            text = BUTTON_LABEL_DISCONNECT
        else:
            text = BUTTON_LABEL_CONNECT

        event.SetText(text)

    def _update_serial_ports(self) -> None:
        new_ports = comports()
        current_port: ListPortInfo | None = get_item_client_data(self.choice_serial_port)

        try:
            if all(a == b for a, b in zip(self._serial_ports, new_ports, strict=True)):
                return
        except ValueError:
            pass

        self._serial_ports = new_ports
        self.choice_serial_port.Clear()

        is_connected = False
        for i, port in enumerate(self._serial_ports):
            label = port_info_label(port)
            self.choice_serial_port.Append(label, port)

            if i == 0:
                self.choice_serial_port.SetSelection(0)

            if port == current_port:
                is_connected = True
                self.choice_serial_port.SetSelection(i)

        if not is_connected:
            self._disconnect()

    def _connect(self) -> None:
        self._state = State.PROCESSING_MOVING

        serial_port: ListPortInfo | None = get_item_client_data(self.choice_serial_port)
        if serial_port is None:
            return

        self._control = Control(SerialTransport(serial_port.device))

        schedule_task(self._update_device_parameters_task, self._connect_error, self._update_device_parameters_resume)

    def _connect_error(self, error: Exception) -> None:
        self._state = State.DISCONNECTED

        self._present_error(error)

    def _update_device_parameters_task(self) -> DeviceParameters:
        if self._control is None:
            raise ControlError

        identification = self._control.get_identification()
        magnification_range = self._control.get_magnification_range()
        magnification = self._control.get_magnification()
        collimation_range = self._control.get_collimation_range()
        collimation = self._control.get_collimation()
        wavelengths = self._control.get_wavelengths()
        wavelength = self._control.get_wavelength()
        presets = self._control.get_presets()
        preset_remaining = self._control.get_remaining_presets()
        flags = self._control.get_flags()

        self._control.wait_for_status_idle()

        return DeviceParameters(
            identification=identification,
            magnification_range=magnification_range,
            magnification=magnification,
            collimation_range=collimation_range,
            collimation=collimation,
            wavelengths=wavelengths,
            wavelength=wavelength,
            presets=presets,
            preset_remaining=preset_remaining,
            flags=flags,
        )

    def _update_device_parameters_resume(self, value: DeviceParameters) -> None:
        self._state = State.IDLE

        self._device_parameters = value

    def _disconnect(self) -> None:
        self._state = State.PROCESSING_MOVING

        self._control = None
        self._device_parameters = None

        self._state = State.DISCONNECTED

    # MARK: Homing

    def on_homing_click(self, _event: wx.CommandEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        self._state = State.PROCESSING_HOMING

        schedule_task(self._homing_task, self._connect_error, self._homing_resume)

    def _homing_task(self) -> None:
        if self._control is None:
            raise ControlError

        self._control.home()

    def _homing_resume(self, _value: None) -> None:
        self._state = State.IDLE

    # MARK: Magnification

    def on_magnification_decrease_large_click(self, _event: wx.CommandEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        if self._device_parameters is None:
            raise DeviceParametersError

        new_mag = round(math.ceil(self._device_parameters.magnification - MAGNIFICATION_STEP_LARGE), 0)
        self._handle_magnification_step_click(new_mag)

    def on_magnification_decrease_small_click(self, _event: wx.CommandEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        if self._device_parameters is None:
            raise DeviceParametersError

        new_mag = round(self._device_parameters.magnification - MAGNIFICATION_STEP_SMALL, 1)
        self._handle_magnification_step_click(new_mag)

    def on_magnification_increase_large_click(self, _event: wx.CommandEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        if self._device_parameters is None:
            raise DeviceParametersError

        new_mag = round(math.floor(self._device_parameters.magnification + MAGNIFICATION_STEP_LARGE), 0)
        self._handle_magnification_step_click(new_mag)

    def on_magnification_increase_small_click(self, _event: wx.CommandEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        if self._device_parameters is None:
            raise DeviceParametersError

        new_mag = round(self._device_parameters.magnification + MAGNIFICATION_STEP_SMALL, 1)
        self._handle_magnification_step_click(new_mag)

    def _handle_magnification_step_click(self, value: float) -> None:
        if self._device_parameters is None:
            raise DeviceParametersError

        self._state = State.PROCESSING_MOVING

        mag_min, mag_max = self._device_parameters.magnification_range
        new_mag = float(min(max(value, mag_min), mag_max))

        self._set_magnification(new_mag)

    def on_magnification_text_enter(self, event: wx.CommandEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        self._state = State.PROCESSING_MOVING

        event_object: wx.TextCtrl = event.GetEventObject()

        try:
            value = float(event_object.GetValue())
        except ValueError as ex:
            self._state = State.IDLE
            self._present_error(ex)
            return

        event_object.SetModified(modified=False)

        self._set_magnification(value)

    def on_magnification_kill_focus(self, event: wx.FocusEvent) -> None:
        if self._device_parameters is None:
            raise DeviceParametersError

        event_object: wx.TextCtrl = event.GetEventObject()

        if event_object.IsModified():
            event_object.SetValue(str(self._device_parameters.magnification))
            event_object.SetModified(modified=False)

    def _set_magnification(self, value: float) -> None:
        if self._device_parameters is None:
            raise DeviceParametersError

        col = COLLIMATION_DEFAULT
        self._device_parameters.magnification = value
        self._device_parameters.collimation = col

        schedule_task(
            self._magnification_command_task, self._task_error, self._magnification_command_resume, (value, col)
        )

    def _magnification_command_task(self, value: tuple[float, int]) -> tuple[float, int]:
        if self._control is None:
            raise ControlError

        mag, col = value

        self._control.set_magnification(mag)
        mag = self._control.get_magnification()

        self._control.set_collimation(col)
        col = self._control.get_collimation()

        return mag, col

    def _magnification_command_resume(self, value: tuple[float, int]) -> None:
        if self._device_parameters is None:
            raise DeviceParametersError

        self._state = State.IDLE

        mag, col = value
        self._device_parameters.magnification = mag
        self._device_parameters.collimation = col

    # MARK: Collimation

    def on_collimation_decrease_click(self, _event: wx.CommandEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        if self._device_parameters is None:
            raise DeviceParametersError

        new_col = self._device_parameters.collimation - COLLIMATION_STEP
        self._handle_collimation_step_click(new_col)

    def on_collimation_increase_click(self, _event: wx.CommandEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        if self._device_parameters is None:
            raise DeviceParametersError

        new_col = self._device_parameters.collimation + COLLIMATION_STEP
        self._handle_collimation_step_click(new_col)

    def _handle_collimation_step_click(self, value: int) -> None:
        if self._device_parameters is None:
            raise DeviceParametersError

        self._state = State.PROCESSING_MOVING

        col_min, col_max = self._device_parameters.collimation_range
        new_col = int(min(max(value, col_min), col_max))

        self._set_collimation(new_col)

    def on_collimation_text_enter(self, event: wx.CommandEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        self._state = State.PROCESSING_MOVING

        event_object: wx.TextCtrl = event.GetEventObject()

        try:
            value = int(event_object.GetValue())
        except ValueError as ex:
            self._state = State.IDLE
            self._present_error(ex)
            return

        event_object.SetModified(modified=False)

        self._set_collimation(value)

    def on_collimation_kill_focus(self, event: wx.FocusEvent) -> None:
        if self._device_parameters is None:
            raise DeviceParametersError

        event_object: wx.TextCtrl = event.GetEventObject()

        if event_object.IsModified():
            event_object.SetValue(str(self._device_parameters.collimation))
            event_object.SetModified(modified=False)

    def _set_collimation(self, value: int) -> None:
        if self._device_parameters is None:
            raise DeviceParametersError

        self._device_parameters.collimation = value

        schedule_task(self._collimation_command_task, self._task_error, self._collimation_command_resume, value)

    def _collimation_command_task(self, value: int) -> int:
        if self._control is None:
            raise ControlError

        self._control.set_collimation(value)
        return self._control.get_collimation()

    def _collimation_command_resume(self, value: int) -> None:
        if self._device_parameters is None:
            raise DeviceParametersError

        self._state = State.IDLE

        self._device_parameters.collimation = value

    # MARK: Wavelength

    def on_wavelength_choice(self, _event: wx.CommandEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        if self._device_parameters is None:
            raise DeviceParametersError

        wavelength: DecimalWithDimension | None = get_item_client_data(self.choice_wavelength)
        if wavelength is None:
            return

        if wavelength == self._device_parameters.wavelength:
            return

        self._state = State.PROCESSING_MOVING

        schedule_task(self._wavelength_command_task, self._task_error, self._wavelength_command_resume, wavelength)

    def _wavelength_command_task(
        self, value: tuple[DecimalWithDimension, list[PresetValue], int]
    ) -> DecimalWithDimension:
        if self._control is None:
            raise ControlError

        self._control.set_wavelength(int(value))
        wavelength = self._control.get_wavelength()
        presets = self._control.get_presets()
        preset_remaining = self._control.get_remaining_presets()

        return wavelength, presets, preset_remaining

    def _wavelength_command_resume(self, value: tuple[DecimalWithDimension, list[PresetValue], int]) -> None:
        if self._device_parameters is None:
            raise DeviceParametersError

        wavelength, presets, preset_remaining = value
        self._device_parameters.wavelength = wavelength
        self._device_parameters.presets = presets
        self._device_parameters.preset_remaining = preset_remaining

        self._set_magnification(self._device_parameters.magnification)

    # MARK: Preset

    def on_preset_add_click(self, _event: wx.CommandEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        if self._device_parameters is None:
            raise DeviceParametersError

        self._state = State.PROCESSING_MOVING

        schedule_task(self._add_preset_command_task, self._task_error, self._add_preset_command_resume)

    def _add_preset_command_task(self) -> tuple[list[PresetValue], int]:
        if self._control is None:
            raise ControlError

        self._control.save_preset()
        presets = self._control.get_presets()
        preset_remaining = self._control.get_remaining_presets()

        return presets, preset_remaining

    def _add_preset_command_resume(self, value: tuple[list[PresetValue], int]) -> None:
        if self._device_parameters is None:
            raise DeviceParametersError

        self._state = State.IDLE

        presets, preset_remaining = value
        self._device_parameters.presets = presets
        self._device_parameters.preset_remaining = preset_remaining

    def on_preset_remove_click(self, _event: wx.CommandEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        if self._device_parameters is None:
            raise DeviceParametersError

        row = self.dv_presets.GetSelectedRow()
        if row == wx.NOT_FOUND:
            return

        preset_id: int = self.dv_presets.GetItemData(self.dv_presets.RowToItem(row))

        self._state = State.PROCESSING_MOVING

        schedule_task(self._remove_preset_command_task, self._task_error, self._remove_preset_command_resume, preset_id)

    def _remove_preset_command_task(self, value: int) -> tuple[list[PresetValue], int]:
        if self._control is None:
            raise ControlError

        self._control.delete_preset(value)
        presets = self._control.get_presets()
        preset_remaining = self._control.get_remaining_presets()

        return presets, preset_remaining

    def _remove_preset_command_resume(self, value: tuple[list[PresetValue], int]) -> None:
        if self._device_parameters is None:
            raise DeviceParametersError

        self._state = State.IDLE

        presets, preset_remaining = value
        self._device_parameters.presets = presets
        self._device_parameters.preset_remaining = preset_remaining

    def on_presets_item_activated(self, event: wx.dataview.DataViewEvent) -> None:
        if self._state in [State.PROCESSING_MOVING, State.PROCESSING_HOMING]:
            return

        if self._device_parameters is None:
            raise DeviceParametersError

        self._state = State.PROCESSING_MOVING

        event_object: wx.dataview.DataViewListCtrl = event.GetEventObject()

        index = event_object.ItemToRow(event.GetItem())
        preset = self._device_parameters.presets[index]

        self._device_parameters.magnification = preset.magnification
        self._device_parameters.collimation = preset.collimation

        schedule_task(
            self._magnification_command_task,
            self._task_error,
            self._magnification_command_resume,
            (preset.magnification, preset.collimation),
        )

    # MARK: Other

    def statusbar_items(self) -> tuple[str, str]:
        return self._state.value, self._device_description()

    def _device_description(self) -> str:
        if self._device_parameters is None:
            return ""

        return self._device_parameters.identification.description()

    def _task_error(self, error: Exception) -> None:
        self._state = State.IDLE

        self._present_error(error)

    def _present_error(self, error: Exception) -> None:
        try:
            message = traceback.format_exception_only(error)[0].strip()
        except:  # noqa: E722
            message = str(error)

        dialog = wx.MessageDialog(self, message=message, caption="Error", style=wx.OK | wx.ICON_ERROR)
        dialog.ShowModal()
        dialog.Destroy()


def port_info_label(port_info: ListPortInfo) -> str:
    if port_info.description == "n/a":
        return port_info.device

    return f"{port_info.device} ({port_info.description})"


def get_item_client_data(item_container: wx.ItemContainer) -> Any | None:  # noqa: ANN401
    index = item_container.GetSelection()
    if index == wx.NOT_FOUND:
        return None

    return item_container.GetClientData(index)
