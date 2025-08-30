import flet as ft
from typing import List, Optional, Union, Callable
from enum import Enum

class StepState(Enum):
    """États possibles pour chaque étape"""
    DISABLED = "disabled"
    INACTIVE = "inactive"
    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"

class StepperOrientation(Enum):
    """Orientation du stepper"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

class Step:
    """Classe représentant une étape du stepper"""
    def __init__(
        self,
        title: str,
        content: Optional[Union[str, ft.Control]] = None,
        icon: Optional[Union[str, ft.Icon, ft.Image, ft.Control]] = None,
        state: StepState = StepState.INACTIVE,
        is_active: bool = False,
        subtitle: Optional[str] = None
    ):
        self.title = title
        self.content = content
        self.icon = icon
        self.state = state
        self.is_active = is_active
        self.subtitle = subtitle

class CustomStepper(ft.UserControl):
    """Widget Stepper personnalisable pour Flet"""
    
    def __init__(
        self,
        steps: List[Step],
        current_step: int = 0,
        orientation: StepperOrientation = StepperOrientation.HORIZONTAL,
        # Couleurs personnalisables
        active_color: str = ft.colors.BLUE,
        completed_color: str = ft.colors.GREEN,
        inactive_color: str = ft.colors.GREY_400,
        error_color: str = ft.colors.RED,
        disabled_color: str = ft.colors.GREY_300,
        # Styles
        connector_thickness: float = 2,
        step_size: float = 32,
        # Callbacks
        on_step_tapped: Optional[Callable[[int], None]] = None,
        on_step_changed: Optional[Callable[[int], None]] = None,
        # Options d'affichage
        show_step_numbers: bool = True,
        show_titles: bool = True,
        show_subtitles: bool = True,
        clickable_steps: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.steps = steps
        self.current_step = current_step
        self.orientation = orientation
        
        # Couleurs
        self.active_color = active_color
        self.completed_color = completed_color
        self.inactive_color = inactive_color
        self.error_color = error_color
        self.disabled_color = disabled_color
        
        # Styles
        self.connector_thickness = connector_thickness
        self.step_size = step_size
        
        # Callbacks
        self.on_step_tapped = on_step_tapped
        self.on_step_changed = on_step_changed
        
        # Options
        self.show_step_numbers = show_step_numbers
        self.show_titles = show_titles
        self.show_subtitles = show_subtitles
        self.clickable_steps = clickable_steps
        
        # Mettre à jour les états initiaux
        self._update_step_states()

    def _get_step_color(self, step: Step, index: int) -> str:
        """Retourne la couleur appropriée pour une étape"""
        if step.state == StepState.DISABLED:
            return self.disabled_color
        elif step.state == StepState.ERROR:
            return self.error_color
        elif step.state == StepState.COMPLETED or index < self.current_step:
            return self.completed_color
        elif index == self.current_step:
            return self.active_color
        else:
            return self.inactive_color

    def _create_step_icon(self, step: Step, index: int) -> ft.Control:
        """Crée l'icône pour une étape"""
        color = self._get_step_color(step, index)
        
        # Si une icône personnalisée est fournie
        if step.icon:
            if isinstance(step.icon, str):
                return ft.Icon(step.icon, color=color, size=self.step_size * 0.6)
            elif isinstance(step.icon, ft.Control):
                return step.icon
            else:
                return step.icon
        
        # Icône par défaut basée sur l'état
        if step.state == StepState.COMPLETED or index < self.current_step:
            icon_name = ft.icons.CHECK
        elif step.state == StepState.ERROR:
            icon_name = ft.icons.ERROR
        else:
            # Afficher le numéro de l'étape si activé
            if self.show_step_numbers:
                return ft.Text(
                    str(index + 1),
                    color=ft.colors.WHITE if index == self.current_step else color,
                    weight=ft.FontWeight.BOLD,
                    size=self.step_size * 0.4
                )
            else:
                icon_name = ft.icons.CIRCLE

        return ft.Icon(
            icon_name,
            color=ft.colors.WHITE if index == self.current_step else color,
            size=self.step_size * 0.6
        )

    def _create_step_circle(self, step: Step, index: int) -> ft.Control:
        """Crée le cercle pour une étape"""
        color = self._get_step_color(step, index)
        icon = self._create_step_icon(step, index)
        
        circle = ft.Container(
            content=icon,
            width=self.step_size,
            height=self.step_size,
            bgcolor=color if index == self.current_step else ft.colors.TRANSPARENT,
            border=ft.border.all(2, color),
            border_radius=self.step_size / 2,
            alignment=ft.alignment.center,
        )
        
        if self.clickable_steps and step.state != StepState.DISABLED:
            circle = ft.GestureDetector(
                content=circle,
                on_tap=lambda e, i=index: self._on_step_tap(i)
            )
        
        return circle

    def _create_connector(self, is_completed: bool = False) -> ft.Control:
        """Crée un connecteur entre les étapes"""
        color = self.completed_color if is_completed else self.inactive_color
        
        if self.orientation == StepperOrientation.HORIZONTAL:
            return ft.Container(
                width=50,
                height=self.connector_thickness,
                bgcolor=color,
                margin=ft.margin.symmetric(horizontal=5)
            )
        else:
            return ft.Container(
                width=self.connector_thickness,
                height=30,
                bgcolor=color,
                margin=ft.margin.symmetric(vertical=5)
            )

    def _create_step_content(self, step: Step, index: int) -> ft.Control:
        """Crée le contenu d'une étape (titre, sous-titre)"""
        controls = []
        
        if self.show_titles and step.title:
            color = self._get_step_color(step, index)
            title = ft.Text(
                step.title,
                weight=ft.FontWeight.BOLD if index == self.current_step else ft.FontWeight.NORMAL,
                color=color,
                size=14
            )
            controls.append(title)
        
        if self.show_subtitles and step.subtitle:
            subtitle = ft.Text(
                step.subtitle,
                color=ft.colors.GREY_600,
                size=12
            )
            controls.append(subtitle)
        
        # Contenu personnalisé de l'étape
        if step.content and index == self.current_step:
            if isinstance(step.content, str):
                content_widget = ft.Text(step.content)
            else:
                content_widget = step.content
            controls.append(ft.Container(content=content_widget, margin=ft.margin.only(top=10)))
        
        if not controls:
            return ft.Container()
        
        return ft.Column(
            controls=controls,
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER if self.orientation == StepperOrientation.HORIZONTAL else ft.CrossAxisAlignment.START
        )

    def _on_step_tap(self, index: int):
        """Gestionnaire de clic sur une étape"""
        if self.on_step_tapped:
            self.on_step_tapped(index)
        
        # Changer l'étape active si autorisé
        if self.steps[index].state != StepState.DISABLED:
            old_step = self.current_step
            self.current_step = index
            self._update_step_states()
            self.update()
            
            if self.on_step_changed and old_step != index:
                self.on_step_changed(index)

    def _update_step_states(self):
        """Met à jour les états des étapes"""
        for i, step in enumerate(self.steps):
            if step.state != StepState.DISABLED and step.state != StepState.ERROR:
                if i < self.current_step:
                    step.state = StepState.COMPLETED
                elif i == self.current_step:
                    step.state = StepState.ACTIVE
                else:
                    step.state = StepState.INACTIVE

    def build(self):
        step_widgets = []
        
        for i, step in enumerate(self.steps):
            step_circle = self._create_step_circle(step, i)
            step_content = self._create_step_content(step, i)
            
            if self.orientation == StepperOrientation.HORIZONTAL:
                step_widget = ft.Column([
                    step_circle,
                    step_content
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
            else:
                step_widget = ft.Row([
                    step_circle,
                    ft.Container(step_content, margin=ft.margin.only(left=15))
                ], alignment=ft.MainAxisAlignment.START, spacing=0)
            
            step_widgets.append(step_widget)
            
            # Ajouter un connecteur sauf après la dernière étape
            if i < len(self.steps) - 1:
                is_completed = i < self.current_step
                connector = self._create_connector(is_completed)
                step_widgets.append(connector)
        
        if self.orientation == StepperOrientation.HORIZONTAL:
            return ft.Row(
                step_widgets,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
        else:
            return ft.Column(
                step_widgets,
                alignment=ft.MainAxisAlignment.START
            )

    # Méthodes publiques pour contrôler le stepper
    def next_step(self):
        """Passe à l'étape suivante"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._update_step_states()
            self.update()
            if self.on_step_changed:
                self.on_step_changed(self.current_step)

    def previous_step(self):
        """Revient à l'étape précédente"""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_step_states()
            self.update()
            if self.on_step_changed:
                self.on_step_changed(self.current_step)

    def go_to_step(self, step_index: int):
        """Va à une étape spécifique"""
        if 0 <= step_index < len(self.steps) and self.steps[step_index].state != StepState.DISABLED:
            old_step = self.current_step
            self.current_step = step_index
            self._update_step_states()
            self.update()
            if self.on_step_changed and old_step != step_index:
                self.on_step_changed(step_index)

    def set_step_state(self, step_index: int, state: StepState):
        """Définit l'état d'une étape spécifique"""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index].state = state
            self.update()

    def reset(self):
        """Remet le stepper au début"""
        self.current_step = 0
        for step in self.steps:
            if step.state not in [StepState.DISABLED, StepState.ERROR]:
                step.state = StepState.INACTIVE
        self._update_step_states()
        self.update()