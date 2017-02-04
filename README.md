## Provider interface

In order for all the providers to be used transparently,
they must respect the Provider interface.

They must expose an asynchronous `search` function.

## Bridge interface
In order for all the bridges to be used transparently,
they must respect the Bridge interface.

They must expose a factory function that creates an
asynchronous context manager object when called. This
context manager object should be used to initiate the
connection to the remote bridge, if needed. When the
context manager exits, it should close the connection,
and clean up all of its resources.

This object should also have two methods:
`add_torrent_magnet` and `add_torrent_url`, to
add magnet urls and torrent file urls respectively.
