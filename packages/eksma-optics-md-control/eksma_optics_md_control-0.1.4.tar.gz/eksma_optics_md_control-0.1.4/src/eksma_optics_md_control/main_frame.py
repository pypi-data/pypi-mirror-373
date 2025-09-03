from __future__ import annotations

import logging
import sys
from pathlib import Path

import wx

from eksma_optics_md_control._gui_base import MainFrame as _MainFrame
from eksma_optics_md_control.main_panel import MainPanel

logger = logging.getLogger(__name__)


class MainFrame(_MainFrame):
    def __init__(self, parent: wx.Frame) -> None:
        super().__init__(parent)

        self._panel = MainPanel(self)

        self.statusbar.SetStatusWidths([200, -1])

        platform_information: wx.PlatformInformation = wx.PlatformInformation.Get()
        if platform_information.GetOperatingSystemId() == wx.OS_WINDOWS_NT:
            if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
                icon_path = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"
            else:
                icon_path = Path("assets/icon.ico")

            icon = wx.Icon(str(icon_path), wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)

    def on_statusbar_update_ui(self, _event: wx.UpdateUIEvent) -> None:
        for i, text in enumerate(self._panel.statusbar_items()):
            self.statusbar.SetStatusText(text, i)

    def on_menu_update_ui(self, event: wx.CommandEvent) -> None:
        self._panel.on_menu_update_ui(event)

    # MARK: Device

    def on_menu_device_connect_click(self, event: wx.CommandEvent) -> None:
        self._panel.on_connect_click(event)

    def on_menu_device_connect_update_ui(self, event: wx.UpdateUIEvent) -> None:
        self._panel.on_connect_update_ui(event)

    def on_menu_device_homing_click(self, event: wx.CommandEvent) -> None:
        self._panel.on_homing_click(event)

    def on_menu_device_increase_magnification_large_selection(self, event: wx.CommandEvent) -> None:
        self._panel.on_magnification_increase_large_click(event)

    def on_menu_device_decrease_magnification_large_selection(self, event: wx.CommandEvent) -> None:
        self._panel.on_magnification_decrease_large_click(event)

    def on_menu_device_increase_magnification_small_selection(self, event: wx.CommandEvent) -> None:
        self._panel.on_magnification_increase_small_click(event)

    def on_menu_device_decrease_magnification_small_selection(self, event: wx.CommandEvent) -> None:
        self._panel.on_magnification_decrease_small_click(event)

    def on_menu_device_increase_collimation_selection(self, event: wx.CommandEvent) -> None:
        self._panel.on_collimation_increase_click(event)

    def on_menu_device_decrease_collimation_selection(self, event: wx.CommandEvent) -> None:
        self._panel.on_collimation_decrease_click(event)

    # MARK: Presets

    def on_menu_presets_add_selection(self, event: wx.CommandEvent) -> None:
        self._panel.on_preset_add_click(event)

    def on_menu_presets_remove_selection(self, event: wx.CommandEvent) -> None:
        self._panel.on_preset_remove_click(event)

    def on_menu_presets_remove_update_ui(self, event: wx.CommandEvent) -> None:
        self._panel.on_preset_remove_update_ui(event)
