# winup/animate/fx.py
"""
A module for handling animations in WinUp.
"""
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QAbstractAnimation
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect

def animate(
    widget: QWidget,
    prop_name: str,
    end_value,
    duration: int,
    easing_curve: QEasingCurve.Type = QEasingCurve.Type.InOutQuad,
    on_finish: callable = None,
):
    """
    Animates a widget's property to a new value.

    Args:
        widget: The widget to animate.
        prop_name: The name of the property to animate (e.g., b"geometry", b"windowOpacity").
                   Must be a bytes object.
        end_value: The final value for the property.
        duration: The duration of the animation in milliseconds.
        easing_curve: The easing curve to use for the animation.
        on_finish: An optional function to call when the animation is complete.
    """
    if isinstance(prop_name, str):
        prop_name = prop_name.encode()

    animation = QPropertyAnimation(widget, prop_name)
    animation.setDuration(duration)
    animation.setEndValue(end_value)
    animation.setEasingCurve(easing_curve)

    if on_finish:
        # The animation will be garbage collected if we don't hold a reference,
        # so we attach it to the widget itself. We also connect the finished
        # signal to a lambda that cleans up the animation reference.
        animation.finished.connect(lambda: (on_finish(), delattr(widget, "_active_animation")))
        setattr(widget, "_active_animation", animation)
    
    animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    return animation


def stop(widget: QWidget, prop_name: str = None):
    """
    Stops any active animation on a widget.
    If prop_name is specified, only the animation for that property is stopped.
    """
    if hasattr(widget, "_active_animation"):
        # This is a simple implementation. For a more robust system,
        # you might want to manage a dictionary of animations per property.
        widget._active_animation.stop()
        delattr(widget, "_active_animation")


def fade_in(widget: QWidget, duration: int = 300, on_finish: callable = None):
    """
    Fades a widget in by animating its opacity from 0.0 to 1.0.
    """
    # Create an opacity effect if the widget doesn't have one
    if not hasattr(widget, 'graphicsEffect') or not isinstance(widget.graphicsEffect(), QGraphicsOpacityEffect):
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
    else:
        opacity_effect = widget.graphicsEffect()

    opacity_effect.setOpacity(0.0)
    widget.show()
    
    # We animate the 'opacity' property of the QGraphicsOpacityEffect
    return animate(opacity_effect, b"opacity", 1.0, duration, on_finish=on_finish)


def fade_out(widget: QWidget, duration: int = 300, on_finish: callable = None):
    """
    Fades a widget out by animating its opacity from 1.0 to 0.0.
    The widget is hidden upon completion.
    """
    if not hasattr(widget, 'graphicsEffect') or not isinstance(widget.graphicsEffect(), QGraphicsOpacityEffect):
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
    else:
        opacity_effect = widget.graphicsEffect()
    
    opacity_effect.setOpacity(1.0)

    def _on_finish_internal():
        widget.hide()
        if on_finish:
            on_finish()
    
    # We animate the 'opacity' property of the QGraphicsOpacityEffect
    return animate(opacity_effect, b"opacity", 0.0, duration, on_finish=_on_finish_internal)