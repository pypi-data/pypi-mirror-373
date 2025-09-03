expander.py command line options
================================

``-h``
++++++

    Show help for command line options.

``--summary``
+++++++++++++

    Print a summary of the function of the program.

``-f FILE --file FILE``
+++++++++++++++++++++++

    Specify a FILE to process. This option may be used more than once to
    process more than one file but note than this option is not really needed.
    Files can also be specified directly after the other command line options.
    If not given, the program gets it's input from stdin.

``--encoding``
++++++++++++++
    Specify the encoding of the input to the program. This encoding is also the
    default for all files that are read by ``$include()`` or ``$subst()``. Note
    that both mentioned commands allow to specify a different encoding at each
    call. Known encodings can be found at 
    `python encodings <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

``--output-encoding``
+++++++++++++++++++++
    Specify the encoding of the output of the program. Known encodings can be
    found at 
    `python encodings <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

``--eval``
++++++++++

    Evaluate PYTHONEXPRESSION in global context.

``-I PATH --include PATH``
++++++++++++++++++++++++++

    Add PATH to the list of include paths.

``-s --simple-vars``
++++++++++++++++++++

    Allow variables without brackets.

``-a --auto-continuation``
++++++++++++++++++++++++++

    Assume '\\' at the end of lines with commands.

``--safemode``
++++++++++++++

    Set safe mode mode globally. This mode makes pyexpander more
    restrictive as it disables the execution of arbitrary python
    commands and commands that extend the pyexpander language.

``-p --permissive``
+++++++++++++++++++

    Set permissive mode globally. Undefined variables in expressions do not
    abort the program. If an error occurs, the pyexpander expression
    `$(EXPRESSION)` remains unchanged.

``--preserve-backslashes``
++++++++++++++++++++++++++

    Preserve all backslashes '\\' except the ones used for line continuation.

``-i --auto-indent``
++++++++++++++++++++
    
    Automatically indent macros.

``--no-stdin-msg``
++++++++++++++++++

    Do not print a message on stderr when the program is reading it's input
    from stdin.

``--deps``
++++++++++

    Print dependencies due to $include commands in a makefile compatible
    format.

``-d --dump``
+++++++++++++

    Dump list of strings instead of printing to the console, this is for
    debugging only.

``--exception``
+++++++++++++++

    Do not catch exceptions (for debugging). In case of errors this allows to
    locate the location in the code where the error was detected.

