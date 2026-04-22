import flet as ft

@ft.control
class DefaultContainer(ft.Container):
    def init(self):
        self.expand = True
        self.alignment = ft.Alignment.CENTER

@ft.control
class PresetColumn(ft.Column):
    spacing: ft.Number = 4
    horizontal_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER

@ft.control
class DefaultWindowDragArea(ft.WindowDragArea):
    def init(self):
        self.maximizable = False
        self.expand = True

@ft.control
class PresetWindowDragArea(DefaultWindowDragArea):
    def init(self):
        self.opacity = 0
        self.offset = ft.Offset(0, -1)
        self.animate_opacity = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
        self.animate_offset = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)

@ft.control
class CenteredColumn(ft.Column):
    alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.CENTER
    horizontal_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER