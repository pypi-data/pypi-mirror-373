# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.dataview

import gettext
_ = gettext.gettext

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Motorized Devices Control"), pos = wx.DefaultPosition, size = wx.Size( 800,400 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CLIP_CHILDREN|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.statusbar = self.CreateStatusBar( 2, wx.STB_DEFAULT_STYLE, wx.ID_ANY )
        self.menu = wx.MenuBar( 0 )
        self.menu_device = wx.Menu()
        self.menu_device_connect = wx.MenuItem( self.menu_device, wx.ID_ANY, _(u"Connect")+ u"\t" + u"Ctrl+K", wx.EmptyString, wx.ITEM_NORMAL )
        self.menu_device.Append( self.menu_device_connect )

        self.menu_device.AppendSeparator()

        self.menu_device_homing = wx.MenuItem( self.menu_device, wx.ID_ANY, _(u"Homing")+ u"\t" + u"Ctrl+Shift+H", wx.EmptyString, wx.ITEM_NORMAL )
        self.menu_device.Append( self.menu_device_homing )

        self.menu_device_increase_magnification_large = wx.MenuItem( self.menu_device, wx.ID_ANY, _(u"Increase Magnification by Large Step")+ u"\t" + u"Ctrl++", wx.EmptyString, wx.ITEM_NORMAL )
        self.menu_device.Append( self.menu_device_increase_magnification_large )

        self.menu_device_decrease_magnification_large = wx.MenuItem( self.menu_device, wx.ID_ANY, _(u"Decrease Magnification by Large Step")+ u"\t" + u"Ctrl+-", wx.EmptyString, wx.ITEM_NORMAL )
        self.menu_device.Append( self.menu_device_decrease_magnification_large )

        self.menu_device_increase_magnification_small = wx.MenuItem( self.menu_device, wx.ID_ANY, _(u"Increase Magnification by Small Step")+ u"\t" + u"Ctrl+Alt++", wx.EmptyString, wx.ITEM_NORMAL )
        self.menu_device.Append( self.menu_device_increase_magnification_small )

        self.menu_device_decrease_magnification_small = wx.MenuItem( self.menu_device, wx.ID_ANY, _(u"Decrease Magnification by Small Step")+ u"\t" + u"Ctrl+Alt+-", wx.EmptyString, wx.ITEM_NORMAL )
        self.menu_device.Append( self.menu_device_decrease_magnification_small )

        self.menu_device_increase_collimation = wx.MenuItem( self.menu_device, wx.ID_ANY, _(u"Increase Collimation")+ u"\t" + u"Ctrl+Shift+=", wx.EmptyString, wx.ITEM_NORMAL )
        self.menu_device.Append( self.menu_device_increase_collimation )

        self.menu_device_decrease_collimation = wx.MenuItem( self.menu_device, wx.ID_ANY, _(u"Decrease Collimation")+ u"\t" + u"Ctrl+Shift+-", wx.EmptyString, wx.ITEM_NORMAL )
        self.menu_device.Append( self.menu_device_decrease_collimation )

        self.menu.Append( self.menu_device, _(u"Device") )

        self.menu_presets = wx.Menu()
        self.menu_presets_add = wx.MenuItem( self.menu_presets, wx.ID_ANY, _(u"Add")+ u"\t" + u"Ctrl+D", wx.EmptyString, wx.ITEM_NORMAL )
        self.menu_presets.Append( self.menu_presets_add )

        self.menu_presets_remove = wx.MenuItem( self.menu_presets, wx.ID_ANY, _(u"Remove"), wx.EmptyString, wx.ITEM_NORMAL )
        self.menu_presets.Append( self.menu_presets_remove )

        self.menu.Append( self.menu_presets, _(u"Presets") )

        self.SetMenuBar( self.menu )


        self.Centre( wx.BOTH )

        # Connect Events
        self.statusbar.Bind( wx.EVT_UPDATE_UI, self.on_statusbar_update_ui )
        self.Bind( wx.EVT_MENU, self.on_menu_device_connect_click, id = self.menu_device_connect.GetId() )
        self.Bind( wx.EVT_UPDATE_UI, self.on_menu_device_connect_update_ui, id = self.menu_device_connect.GetId() )
        self.Bind( wx.EVT_MENU, self.on_menu_device_homing_click, id = self.menu_device_homing.GetId() )
        self.Bind( wx.EVT_UPDATE_UI, self.on_menu_update_ui, id = self.menu_device_homing.GetId() )
        self.Bind( wx.EVT_MENU, self.on_menu_device_increase_magnification_large_selection, id = self.menu_device_increase_magnification_large.GetId() )
        self.Bind( wx.EVT_UPDATE_UI, self.on_menu_update_ui, id = self.menu_device_increase_magnification_large.GetId() )
        self.Bind( wx.EVT_MENU, self.on_menu_device_decrease_magnification_large_selection, id = self.menu_device_decrease_magnification_large.GetId() )
        self.Bind( wx.EVT_UPDATE_UI, self.on_menu_update_ui, id = self.menu_device_decrease_magnification_large.GetId() )
        self.Bind( wx.EVT_MENU, self.on_menu_device_increase_magnification_small_selection, id = self.menu_device_increase_magnification_small.GetId() )
        self.Bind( wx.EVT_UPDATE_UI, self.on_menu_update_ui, id = self.menu_device_increase_magnification_small.GetId() )
        self.Bind( wx.EVT_MENU, self.on_menu_device_decrease_magnification_small_selection, id = self.menu_device_decrease_magnification_small.GetId() )
        self.Bind( wx.EVT_UPDATE_UI, self.on_menu_update_ui, id = self.menu_device_decrease_magnification_small.GetId() )
        self.Bind( wx.EVT_MENU, self.on_menu_device_increase_collimation_selection, id = self.menu_device_increase_collimation.GetId() )
        self.Bind( wx.EVT_UPDATE_UI, self.on_menu_update_ui, id = self.menu_device_increase_collimation.GetId() )
        self.Bind( wx.EVT_MENU, self.on_menu_device_decrease_collimation_selection, id = self.menu_device_decrease_collimation.GetId() )
        self.Bind( wx.EVT_UPDATE_UI, self.on_menu_update_ui, id = self.menu_device_decrease_collimation.GetId() )
        self.Bind( wx.EVT_MENU, self.on_menu_presets_add_selection, id = self.menu_presets_add.GetId() )
        self.Bind( wx.EVT_UPDATE_UI, self.on_menu_update_ui, id = self.menu_presets_add.GetId() )
        self.Bind( wx.EVT_MENU, self.on_menu_presets_remove_selection, id = self.menu_presets_remove.GetId() )
        self.Bind( wx.EVT_UPDATE_UI, self.on_menu_presets_remove_update_ui, id = self.menu_presets_remove.GetId() )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def on_statusbar_update_ui( self, event ):
        event.Skip()

    def on_menu_device_connect_click( self, event ):
        event.Skip()

    def on_menu_device_connect_update_ui( self, event ):
        event.Skip()

    def on_menu_device_homing_click( self, event ):
        event.Skip()

    def on_menu_update_ui( self, event ):
        event.Skip()

    def on_menu_device_increase_magnification_large_selection( self, event ):
        event.Skip()


    def on_menu_device_decrease_magnification_large_selection( self, event ):
        event.Skip()


    def on_menu_device_increase_magnification_small_selection( self, event ):
        event.Skip()


    def on_menu_device_decrease_magnification_small_selection( self, event ):
        event.Skip()


    def on_menu_device_increase_collimation_selection( self, event ):
        event.Skip()


    def on_menu_device_decrease_collimation_selection( self, event ):
        event.Skip()


    def on_menu_presets_add_selection( self, event ):
        event.Skip()


    def on_menu_presets_remove_selection( self, event ):
        event.Skip()

    def on_menu_presets_remove_update_ui( self, event ):
        event.Skip()


###########################################################################
## Class MainPanel
###########################################################################

class MainPanel ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        main_sizer = wx.BoxSizer( wx.VERTICAL )

        sizer_connection = wx.BoxSizer( wx.VERTICAL )

        self.label_serial_port = wx.StaticText( self, wx.ID_ANY, _(u"Serial Port"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_serial_port.Wrap( -1 )

        sizer_connection.Add( self.label_serial_port, 0, wx.ALL, 5 )

        sizer_connection_controls = wx.BoxSizer( wx.HORIZONTAL )

        choice_serial_portChoices = []
        self.choice_serial_port = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_serial_portChoices, 0 )
        self.choice_serial_port.SetSelection( 0 )
        sizer_connection_controls.Add( self.choice_serial_port, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.button_connect = wx.Button( self, wx.ID_ANY, _(u"Connect"), wx.DefaultPosition, wx.DefaultSize, 0 )
        sizer_connection_controls.Add( self.button_connect, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sizer_connection.Add( sizer_connection_controls, 1, wx.EXPAND, 5 )


        main_sizer.Add( sizer_connection, 0, wx.ALL|wx.EXPAND, 5 )

        device_control_sizer = wx.BoxSizer( wx.HORIZONTAL )

        preset_sizer = wx.BoxSizer( wx.VERTICAL )

        preset_list_sizer = wx.BoxSizer( wx.VERTICAL )

        self.dv_presets = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_ROW_LINES )
        preset_list_sizer.Add( self.dv_presets, 1, wx.ALL|wx.EXPAND, 5 )


        preset_sizer.Add( preset_list_sizer, 1, wx.EXPAND, 5 )

        preset_action_sizer = wx.BoxSizer( wx.HORIZONTAL )

        self.button_preset_add = wx.Button( self, wx.ID_ANY, _(u"Add"), wx.DefaultPosition, wx.DefaultSize, 0 )
        preset_action_sizer.Add( self.button_preset_add, 0, wx.ALL, 5 )


        preset_action_sizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.button_preset_remove = wx.Button( self, wx.ID_ANY, _(u"Remove"), wx.DefaultPosition, wx.DefaultSize, 0 )
        preset_action_sizer.Add( self.button_preset_remove, 0, wx.ALL, 5 )


        preset_sizer.Add( preset_action_sizer, 0, wx.EXPAND, 5 )


        device_control_sizer.Add( preset_sizer, 0, wx.EXPAND, 5 )

        sizer_device_control = wx.BoxSizer( wx.VERTICAL )

        sizer_wavelength = wx.BoxSizer( wx.VERTICAL )

        self.label_wavelength = wx.StaticText( self, wx.ID_ANY, _(u"Wavelength"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_wavelength.Wrap( -1 )

        sizer_wavelength.Add( self.label_wavelength, 0, wx.ALL, 5 )

        self.label_line_wavelength = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,1 ), wx.LI_HORIZONTAL )
        sizer_wavelength.Add( self.label_line_wavelength, 0, wx.EXPAND |wx.ALL, 5 )

        sizer_wawelength_controls = wx.BoxSizer( wx.HORIZONTAL )

        choice_wavelengthChoices = []
        self.choice_wavelength = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice_wavelengthChoices, 0 )
        self.choice_wavelength.SetSelection( 0 )
        sizer_wawelength_controls.Add( self.choice_wavelength, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sizer_wavelength.Add( sizer_wawelength_controls, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )


        sizer_device_control.Add( sizer_wavelength, 0, wx.ALL|wx.EXPAND, 5 )

        sizer_magnification = wx.BoxSizer( wx.VERTICAL )

        self.label_magnification = wx.StaticText( self, wx.ID_ANY, _(u"Magnification"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_magnification.Wrap( -1 )

        sizer_magnification.Add( self.label_magnification, 0, wx.ALL, 5 )

        self.label_line_magnification = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,1 ), wx.LI_HORIZONTAL )
        sizer_magnification.Add( self.label_line_magnification, 0, wx.EXPAND |wx.ALL, 5 )

        sizer_magnification_controls = wx.BoxSizer( wx.HORIZONTAL )

        self.button_magnification_decrease_small = wx.Button( self, wx.ID_ANY, _(u"-0.1"), wx.DefaultPosition, wx.Size( 48,-1 ), 0 )
        sizer_magnification_controls.Add( self.button_magnification_decrease_small, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.button_magnification_decrease_large = wx.Button( self, wx.ID_ANY, _(u"-1"), wx.DefaultPosition, wx.Size( 48,-1 ), 0 )
        sizer_magnification_controls.Add( self.button_magnification_decrease_large, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.label_magnification_min = wx.StaticText( self, wx.ID_ANY, _(u"0"), wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
        self.label_magnification_min.Wrap( -1 )

        self.label_magnification_min.SetMinSize( wx.Size( 50,-1 ) )

        sizer_magnification_controls.Add( self.label_magnification_min, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.text_magnification = wx.TextCtrl( self, wx.ID_ANY, _(u"0"), wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER )
        self.text_magnification.SetMinSize( wx.Size( 50,-1 ) )

        sizer_magnification_controls.Add( self.text_magnification, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.label_magnification_max = wx.StaticText( self, wx.ID_ANY, _(u"0"), wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
        self.label_magnification_max.Wrap( -1 )

        self.label_magnification_max.SetMinSize( wx.Size( 50,-1 ) )

        sizer_magnification_controls.Add( self.label_magnification_max, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.button_magnification_increase_large = wx.Button( self, wx.ID_ANY, _(u"+1"), wx.DefaultPosition, wx.Size( 48,-1 ), 0 )
        sizer_magnification_controls.Add( self.button_magnification_increase_large, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.button_magnification_increase_small = wx.Button( self, wx.ID_ANY, _(u"+0.1"), wx.DefaultPosition, wx.Size( 48,-1 ), 0 )
        sizer_magnification_controls.Add( self.button_magnification_increase_small, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sizer_magnification.Add( sizer_magnification_controls, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )


        sizer_device_control.Add( sizer_magnification, 0, wx.ALL|wx.EXPAND, 5 )

        sizer_collimation = wx.BoxSizer( wx.VERTICAL )

        self.label_collimation = wx.StaticText( self, wx.ID_ANY, _(u"Collimation"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.label_collimation.Wrap( -1 )

        sizer_collimation.Add( self.label_collimation, 0, wx.ALL, 5 )

        self.label_line_collimation = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,1 ), wx.LI_HORIZONTAL )
        sizer_collimation.Add( self.label_line_collimation, 0, wx.EXPAND |wx.ALL, 5 )

        sizer_collimation_controls = wx.BoxSizer( wx.HORIZONTAL )

        self.button_collimation_decrease = wx.Button( self, wx.ID_ANY, _(u"-1"), wx.DefaultPosition, wx.Size( 48,-1 ), 0 )
        sizer_collimation_controls.Add( self.button_collimation_decrease, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.label_collimation_min = wx.StaticText( self, wx.ID_ANY, _(u"0"), wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
        self.label_collimation_min.Wrap( -1 )

        self.label_collimation_min.SetMinSize( wx.Size( 50,-1 ) )

        sizer_collimation_controls.Add( self.label_collimation_min, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.text_collimation = wx.TextCtrl( self, wx.ID_ANY, _(u"0"), wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER )
        self.text_collimation.SetMinSize( wx.Size( 50,-1 ) )

        sizer_collimation_controls.Add( self.text_collimation, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.label_collimation_max = wx.StaticText( self, wx.ID_ANY, _(u"0"), wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
        self.label_collimation_max.Wrap( -1 )

        self.label_collimation_max.SetMinSize( wx.Size( 50,-1 ) )

        sizer_collimation_controls.Add( self.label_collimation_max, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.button_collimation_increase = wx.Button( self, wx.ID_ANY, _(u"+1"), wx.DefaultPosition, wx.Size( 48,-1 ), 0 )
        sizer_collimation_controls.Add( self.button_collimation_increase, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sizer_collimation.Add( sizer_collimation_controls, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )


        sizer_device_control.Add( sizer_collimation, 0, wx.ALL|wx.EXPAND, 5 )


        device_control_sizer.Add( sizer_device_control, 1, wx.EXPAND, 5 )


        main_sizer.Add( device_control_sizer, 1, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( main_sizer )
        self.Layout()
        main_sizer.Fit( self )
        self.timer = wx.Timer()
        self.timer.SetOwner( self, self.timer.GetId() )
        self.timer.Start( 1000 )


        # Connect Events
        self.choice_serial_port.Bind( wx.EVT_UPDATE_UI, self.on_choice_serial_port_update_ui )
        self.button_connect.Bind( wx.EVT_BUTTON, self.on_connect_click )
        self.button_connect.Bind( wx.EVT_UPDATE_UI, self.on_connect_update_ui )
        self.dv_presets.Bind( wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_presets_item_activated, id = wx.ID_ANY )
        self.dv_presets.Bind( wx.EVT_UPDATE_UI, self.on_presets_update_ui )
        self.button_preset_add.Bind( wx.EVT_BUTTON, self.on_preset_add_click )
        self.button_preset_add.Bind( wx.EVT_UPDATE_UI, self.on_preset_add_update_ui )
        self.button_preset_remove.Bind( wx.EVT_BUTTON, self.on_preset_remove_click )
        self.button_preset_remove.Bind( wx.EVT_UPDATE_UI, self.on_preset_remove_update_ui )
        self.choice_wavelength.Bind( wx.EVT_CHOICE, self.on_wavelength_choice )
        self.choice_wavelength.Bind( wx.EVT_UPDATE_UI, self.on_wavelength_update_ui )
        self.button_magnification_decrease_small.Bind( wx.EVT_BUTTON, self.on_magnification_decrease_small_click )
        self.button_magnification_decrease_small.Bind( wx.EVT_UPDATE_UI, self.on_update_ui )
        self.button_magnification_decrease_large.Bind( wx.EVT_BUTTON, self.on_magnification_decrease_large_click )
        self.button_magnification_decrease_large.Bind( wx.EVT_UPDATE_UI, self.on_update_ui )
        self.label_magnification_min.Bind( wx.EVT_UPDATE_UI, self.on_magnification_min_update_ui )
        self.text_magnification.Bind( wx.EVT_KILL_FOCUS, self.on_magnification_kill_focus )
        self.text_magnification.Bind( wx.EVT_TEXT_ENTER, self.on_magnification_text_enter )
        self.text_magnification.Bind( wx.EVT_UPDATE_UI, self.on_magnification_update_ui )
        self.label_magnification_max.Bind( wx.EVT_UPDATE_UI, self.on_magnification_max_update_ui )
        self.button_magnification_increase_large.Bind( wx.EVT_BUTTON, self.on_magnification_increase_large_click )
        self.button_magnification_increase_large.Bind( wx.EVT_UPDATE_UI, self.on_update_ui )
        self.button_magnification_increase_small.Bind( wx.EVT_BUTTON, self.on_magnification_increase_small_click )
        self.button_magnification_increase_small.Bind( wx.EVT_UPDATE_UI, self.on_update_ui )
        self.button_collimation_decrease.Bind( wx.EVT_BUTTON, self.on_collimation_decrease_click )
        self.button_collimation_decrease.Bind( wx.EVT_UPDATE_UI, self.on_update_ui )
        self.label_collimation_min.Bind( wx.EVT_UPDATE_UI, self.on_collimation_min_update_ui )
        self.text_collimation.Bind( wx.EVT_KILL_FOCUS, self.on_collimation_kill_focus )
        self.text_collimation.Bind( wx.EVT_TEXT_ENTER, self.on_collimation_text_enter )
        self.text_collimation.Bind( wx.EVT_UPDATE_UI, self.on_collimation_update_ui )
        self.label_collimation_max.Bind( wx.EVT_UPDATE_UI, self.on_collimation_max_update_ui )
        self.button_collimation_increase.Bind( wx.EVT_BUTTON, self.on_collimation_increase_click )
        self.button_collimation_increase.Bind( wx.EVT_UPDATE_UI, self.on_update_ui )
        self.Bind( wx.EVT_TIMER, self.on_timer, id=self.timer.GetId() )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def on_choice_serial_port_update_ui( self, event ):
        event.Skip()

    def on_connect_click( self, event ):
        event.Skip()

    def on_connect_update_ui( self, event ):
        event.Skip()

    def on_presets_item_activated( self, event ):
        event.Skip()

    def on_presets_update_ui( self, event ):
        event.Skip()

    def on_preset_add_click( self, event ):
        event.Skip()

    def on_preset_add_update_ui( self, event ):
        event.Skip()

    def on_preset_remove_click( self, event ):
        event.Skip()

    def on_preset_remove_update_ui( self, event ):
        event.Skip()

    def on_wavelength_choice( self, event ):
        event.Skip()

    def on_wavelength_update_ui( self, event ):
        event.Skip()

    def on_magnification_decrease_small_click( self, event ):
        event.Skip()

    def on_update_ui( self, event ):
        event.Skip()

    def on_magnification_decrease_large_click( self, event ):
        event.Skip()


    def on_magnification_min_update_ui( self, event ):
        event.Skip()

    def on_magnification_kill_focus( self, event ):
        event.Skip()

    def on_magnification_text_enter( self, event ):
        event.Skip()

    def on_magnification_update_ui( self, event ):
        event.Skip()

    def on_magnification_max_update_ui( self, event ):
        event.Skip()

    def on_magnification_increase_large_click( self, event ):
        event.Skip()


    def on_magnification_increase_small_click( self, event ):
        event.Skip()


    def on_collimation_decrease_click( self, event ):
        event.Skip()


    def on_collimation_min_update_ui( self, event ):
        event.Skip()

    def on_collimation_kill_focus( self, event ):
        event.Skip()

    def on_collimation_text_enter( self, event ):
        event.Skip()

    def on_collimation_update_ui( self, event ):
        event.Skip()

    def on_collimation_max_update_ui( self, event ):
        event.Skip()

    def on_collimation_increase_click( self, event ):
        event.Skip()


    def on_timer( self, event ):
        event.Skip()


