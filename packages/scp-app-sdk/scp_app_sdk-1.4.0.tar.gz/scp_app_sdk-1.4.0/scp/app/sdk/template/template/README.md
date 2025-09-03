# {{ name }}

Welcome to my SCP APP: {{ name }}

## Management

Install SCP APP CLI

```bash
pip install scp-app-sdk
```

Create a new build via this command line and `.sap` file will be created in the `builds` directory.

```bash
scp-app build
```

Publish your build

```bash
scp-app publish builds/my-app-0.1.0.sap
```
