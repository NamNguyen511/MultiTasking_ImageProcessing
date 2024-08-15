from PyQt5.QtCore import QPropertyAnimation, QRect, QTimer, QEasingCurve, QParallelAnimationGroup


def animation_widget(widget, start_y, end_y, duration=1500):

    animation = QPropertyAnimation(widget, b'geometry')
    animation.setDuration(duration)
    start_geometry = QRect(widget.x(), start_y, widget.width(), widget.height())
    end_geometry = QRect(widget.x(), end_y, widget.width(), widget.height())
    animation.setStartValue(start_geometry)
    animation.setEndValue(end_geometry)
    animation.start()
    return animation


def animation_group_widgets(widgets, start_y_offset, duration=1500):
    animation_group = QParallelAnimationGroup()
    delay = 200
    animations = []
    for i, widget in enumerate(widgets):
        start_y = widget.y() + start_y_offset
        animation = animation_widget(widget, start_y, widget.y(), duration + i * delay)
        animations.append(animation)
        animation_group.addAnimation(animation)
    animation_group.start()
    return animations
