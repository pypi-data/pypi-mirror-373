"""


list_box
^^^^^^^^

ListBoxes make use of a ListBoxRenderer. The default ListBoxRenderer simply displays an item’s string representation.
To make your own ListBoxRenderer create a class that has a render_item() method that accepts the item to be rendered and returns a widget to render.

Here is an simple example of using the ListBox widget:

.. code:: python

  class MySys(bgui.System):
     def lb_click(self, lb):
        print(lb.selected)

     def __init__(self):
        bgui.System.__init__(self)

        items = ["One", "Two", 4, 4.6]
        self.frame = bgui.Frame(self, 'window', border=2, size=[0.5, 0.5], options=bgui.BGUI_DEFAULT|bgui.BGUI_CENTERED)
        self.lb = bgui.ListBox(self.frame, "lb", items=items, padding=0.05, size=[0.9, 0.9], pos=[0.05, 0.05])
        self.lb.on_click = self.lb_click

        # ... rest of __init__

"""

import typing
