This testbed consists of two small example programs to test draft-ietf-dnsop-kskroll-sentinel.

`make-sentinel-js.py` creates an HTML file that has three different examples of how
to implement kskroll-sentinel in JavaScript in a client.
The first implementation was inspired by Warren Kumari, the second by Paul Hoffman,
and the third by Ray Bellis and Noah Ross. Its purpose is to show that
there are many ways to do the client side of draft-ietf-dnsop-kskroll-sentinel.

`test-sentinel-resolvers.py` sends `dig` queries to a bunch of resolvers to test
them for support of draft-ietf-dnsop-kskroll-sentinel.

Both of these tests use names under "sentinel.research.icann.org" for their tests.

Questions about this testbed should be sent to
[paul.hoffman@icann.org](mailto:paul.hoffman@icann.org).

