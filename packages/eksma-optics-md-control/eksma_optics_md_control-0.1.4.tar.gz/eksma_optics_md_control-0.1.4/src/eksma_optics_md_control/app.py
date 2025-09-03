import logging.config
import os

import wx
import wx.lib.mixins.inspection as wit

from eksma_optics_md_control.main_frame import MainFrame

DEFAULT_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
    },
}

MD_CONTROL_INSPECTABLE = os.getenv("MD_CONTROL_INSPECTABLE")


class App(wx.App):
    def OnInit(self) -> bool:  # noqa: N802
        frame = MainFrame(None)
        frame.Show()

        self.SetTopWindow(frame)

        return True


class InspectableApp(App, wit.InspectionMixin):
    def OnInit(self) -> bool:  # noqa: N802
        self.Init()

        return super().OnInit()


def main() -> None:
    logging.config.dictConfig(DEFAULT_LOGGING)

    app = InspectableApp() if MD_CONTROL_INSPECTABLE is not None else App()

    app.MainLoop()


if __name__ == "__main__":
    main()
