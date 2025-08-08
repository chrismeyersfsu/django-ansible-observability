# Django Ansible Observability

```
pip3 -m venv .venv
pip install -e .
python manage.py runserver
```

`http://localhost:8000`

This should output something like the text below. The trace is showing on your console because of the Django setting `ANSIBLE_OBSERVE_OUTPUT_SPAN_TO_CONSOLE = True`.

```
[08/Aug/2025 15:31:22] "GET / HTTP/1.1" 200 43
Trace beffbf37476957dea79abb858553191a
└── [20:31:22.510739] GET index, span c29749adb0de6a7e
    ├── Kind : SERVER
    ├── Attributes :
    │   ├── http.method : GET
    │   ├── http.server_name : localhost.localdomain
    │   ├── http.scheme : http
    │   ├── net.host.name : localhost:8000
    │   ├── http.host : localhost:8000
    │   ├── net.host.port : 8000
    │   ├── http.url : http://localhost:8000/
    │   ├── net.peer.ip : 127.0.0.1
    │   ├── http.user_agent : Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36
    │   ├── http.flavor : 1.1
    │   └── http.status_code : 200
    └── Resources :
        └── service.name : aap-generic
Transient error StatusCode.UNAVAILABLE encountered while exporting traces to localhost:4317, retrying in 1.15s.
Transient error StatusCode.UNAVAILABLE encountered while exporting traces to localhost:4317, retrying in 2.02s.
Transient error StatusCode.UNAVAILABLE encountered while exporting traces to localhost:4317, retrying in 4.76s.
Failed to export traces to localhost:4317, error code: StatusCode.UNAVAILABLE
```
