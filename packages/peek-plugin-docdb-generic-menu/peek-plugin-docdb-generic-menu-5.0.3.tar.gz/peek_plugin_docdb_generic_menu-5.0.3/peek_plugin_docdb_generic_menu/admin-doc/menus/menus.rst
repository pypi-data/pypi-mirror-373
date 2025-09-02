Menu Screen
-----------

This section describes  the fields in the UI.

:Model Set Key: The key of the model set to match, or null to match all

:Ant Design Icon: The name of a ant design icon to show.
    EG `https://ng.ant.design/components/icon/en`

:Title: The title to show on the menu button.

:Tooltip: The tooltip to show when the button is hovered over.

:Condition: A condition that accepts :code:`prop` properties from the DocDB, it must be
    of the form :code:`{prop}==value` or :code:`{prop1}:{prop2}==thing:false`.
    Quotes around string values are not required (and won't work).

:URL: The URL to navigate to. This can contain properties from the DocDB,
    EG :code:`http://place/{prop}`

