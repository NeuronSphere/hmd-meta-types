.. Deliberate differences from Python

Differences from Python
=======================

Behavior where the Go implementation knowingly differs from Python. Each one is
outside what the golden corpus exercises, and none appears in a real lang pack's
``.hms`` files as of 2026-10-26.

.. req:: Regular expressions use RE2 syntax
    :id: HMD_META_TYPES_REQ_DIFF_001
    :status: implemented

    A ``regex`` validation shall be compiled with Go's RE2 syntax, anchored at the
    start like ``re.match``. Python-only constructs (lookaround, backreferences)
    shall fail validation instead of matching. No lang pack uses ``regex``.

.. req:: strptime implements the common directives
    :id: HMD_META_TYPES_REQ_DIFF_002
    :status: implemented

    ``datetime`` validation shall support ``%Y %y %m %d %j %H %I %M %S %f %z %p
    %a %A %b %B %%`` (C locale). Week-number, ISO-year, locale-composite and
    ``%Z`` directives (``%U %W %w %u %G %V %c %x %X %Z``), which Python accepts,
    shall fail validation. The only format lang packs use is ``%Y-%m-%d``.

.. req:: Go-set values follow Python's datetime limits
    :id: HMD_META_TYPES_REQ_DIFF_003
    :status: implemented

    A ``time.Time`` set from Go shall be truncated to microseconds, and a year
    outside 1-9999 shall be a type error, because a Python ``datetime`` can hold
    neither.
