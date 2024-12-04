"""
VSmesh: Visual Scripting Modular Extensible System for Holography

This project implements a visual flow programming system that generates code based on nodes for various programming languages.
It is modular, allowing developers to add support or plugins for other languages using .vsm files. These files define custom nodes,
their appearance, and their connections. In the future, an API system can be added to allow compiling modules for more powerful nodes,
or plugins can add nodes that execute grouped functions.

History:
VSmesh started as a concept to simplify the process of programming through a visual interface. Inspired by the plugin systems in 
software like Godot and Unreal Engine, it aims to provide a flexible, modular platform for creating and managing scripts visually.
The project will evolve to include support for multiple programming languages and aims to continue growing with community contributions.

Author: Aayden
Date: December 3, 2024
"""

from PySide6.QtCore import Qt, QPoint, QPointF
from PySide6.QtGui import QWheelEvent, QMouseEvent, QPainter, QPen, QColor
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QDockWidget, QWidget
import sys

class InfiniteGrid(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)  # Create a QGraphicsScene and set it to the view
        self.setScene(self.scene)

        # Zoom variables
        self.scale_factor = 1.0  # Initial scale factor
        self.max_scale_factor = 0.85  # Maximum zoom level
        self.min_scale_factor = 0.25  # Minimum zoom level

        # Panning variables
        self.pan_limit_x = 5000  # Panning limit on the x-axis
        self.pan_limit_y = 5000  # Panning limit on the y-axis

        # Configure rendering settings
        self.setRenderHint(QPainter.Antialiasing)  # Enable antialiasing for smoother lines
        self.setBackgroundBrush(QColor(30, 30, 30))  # Set background color to dark gray
        self.setSceneRect(-self.pan_limit_x, -self.pan_limit_y, 2 * self.pan_limit_x, 2 * self.pan_limit_y)  # Set the scene rectangle based on panning limits
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)  # Reduce screen tearing
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Remove horizontal scroll bar
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Remove vertical scroll bar
        self.setCursor(Qt.ArrowCursor)  # Set the default cursor to arrow

        # Draw the initial grid
        self.draw_grid()

    def draw_grid(self):
        """Draws a grid in the scene."""
        self.scene.clear()  # Clear the current scene
        grid_size = 50 * self.scale_factor  # Calculate the grid size based on the scale factor
        pen = QPen(QColor(200, 200, 200), 0.5)  # Create a pen with light gray color for grid lines and set pen width

        # Draw vertical lines
        for x in range(int(self.sceneRect().left()), int(self.sceneRect().right()), int(grid_size)):
            self.scene.addLine(x, self.sceneRect().top(), x, self.sceneRect().bottom(), pen)  # Draw a vertical line

        # Draw horizontal lines
        for y in range(int(self.sceneRect().top()), int(self.sceneRect().bottom()), int(grid_size)):
            self.scene.addLine(self.sceneRect().left(), y, self.sceneRect().right(), y, pen)  # Draw a horizontal line

    def wheelEvent(self, event: QWheelEvent):
        """Handles zooming in and out with the mouse wheel."""
        zoom_in_factor = 1.25  # Scale factor for zooming in
        zoom_out_factor = 0.8  # Scale factor for zooming out
        zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor  # Determine the zoom direction based on the wheel scroll
        new_scale_factor = self.scale_factor * zoom_factor  # Calculate the new scale factor

        if self.min_scale_factor <= new_scale_factor <= self.max_scale_factor:  # Check if the new scale factor is within limits
            self.scale_factor = new_scale_factor  # Update the scale factor
            self.scale(zoom_factor, zoom_factor)  # Apply the zoom
            self.draw_grid()  # Redraw the grid to match the new scale

    def mousePressEvent(self, event: QMouseEvent):
        """Handles mouse press events to initiate panning."""
        if event.button() == Qt.LeftButton:  # Check if the left mouse button was pressed
            self.last_mouse_pos = event.position().toPoint()  # Store the mouse position (convert QPointF to QPoint)
            self.setCursor(Qt.ClosedHandCursor)  # Change cursor to closed hand when panning starts
        super().mousePressEvent(event)  # Call the base class implementation

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handles mouse move events for panning."""
        if event.buttons() & Qt.LeftButton and self.last_mouse_pos:  # Check if the left mouse button is held down and a previous position is stored
            delta = self.mapToScene(event.position().toPoint()) - self.mapToScene(self.last_mouse_pos)  # Calculate the change in position (delta)
            new_x = max(min(self.horizontalScrollBar().value() - delta.x(), self.pan_limit_x), -self.pan_limit_x)  # Calculate and limit new x position
            new_y = max(min(self.verticalScrollBar().value() - delta.y(), self.pan_limit_y), -self.pan_limit_y)  # Calculate and limit new y position
            self.horizontalScrollBar().setValue(new_x)  # Update the horizontal scrollbar
            self.verticalScrollBar().setValue(new_y)  # Update the vertical scrollbar
            self.last_mouse_pos = event.position().toPoint()  # Update the last mouse position
        super().mouseMoveEvent(event)  # Call the base class implementation

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handles mouse release events to end panning."""
        if event.button() == Qt.LeftButton:  # Check if the left mouse button was released
            self.setCursor(Qt.ArrowCursor)  # Change cursor back to arrow when panning stops
        super().mouseReleaseEvent(event)  # Call the base class implementation

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VSmesh")  # Set the window title
        self.setGeometry(100, 100, 1200, 800)  # Set the window geometry (position and size)

        # Variables to control dock widget widths
        self.left_dock_width = 200
        self.right_dock_width = 200

        # Create and set the central widget
        self.grid_view = InfiniteGrid()
        self.setCentralWidget(self.grid_view)

        # Create left dock widget for adding functions and variables
        self.left_dock = QDockWidget("Functions and Variables", self)
        self.left_dock.setWidget(QWidget())  # Empty widget for now
        self.left_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)  # Make it undockable
        self.left_dock.setFixedWidth(self.left_dock_width)  # Set initial width
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        # Create right dock widget for generated code with flow-based programming
        self.right_dock = QDockWidget("Generated Code", self)
        self.right_dock.setWidget(QWidget())  # Empty widget for now
        self.right_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)  # Make it undockable
        self.right_dock.setFixedWidth(self.right_dock_width)  # Set initial width
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create an instance of QApplication
    window = MainWindow()  # Create the main window
    window.show()  # Show the main window
    sys.exit(app.exec())  # Start the application event loop
