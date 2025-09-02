# pys3fuse
A FUSE Written in Python to Support S3 Protocol on POSIX

## Installation
1. You must have these libraries
```bash
sudo apt install libfuse2t64 libfuse3-3 libfuse3-dev libfuse-dev
```

2. Create a directory for your S3 bucket
```bash
mkdir some_name
```

3. Create a venv inside it
```bash
python3 -m venv .venv && source .venv/bin/activate
```

4. Install `PyS3FUSE`
```bash
python -m pip install pys3fuse
```

5. Usage
```bash
python -m pys3fuse --help
```
