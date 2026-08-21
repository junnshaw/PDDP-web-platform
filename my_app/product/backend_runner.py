import json
import os
import subprocess
import sys


def _read_text(filename):
    if not os.path.exists(filename):
        return ''

    with open(filename, 'r', encoding='utf-8', errors='replace') as handle:
        return handle.read()


def _write_task_state(base_path, tmp_folder, status, stdout='', stderr='', command=''):
    ext_dir = os.path.join(base_path, 'tmp', 'ext', tmp_folder)
    os.makedirs(ext_dir, exist_ok=True)

    with open(os.path.join(ext_dir, 'stdout.txt'), 'w', encoding='utf-8') as stdout_file:
        stdout_file.write(stdout or '')
    with open(os.path.join(ext_dir, 'stderr.txt'), 'w', encoding='utf-8') as stderr_file:
        stderr_file.write(stderr or '')
    with open(os.path.join(ext_dir, 'task_state.json'), 'w', encoding='utf-8') as state_file:
        json.dump(
            {
                'status': status,
                'stdout': stdout or '',
                'stderr': stderr or '',
                'command': command,
            },
            state_file,
        )


def _current_status(base_path, tmp_folder):
    state_file = os.path.join(base_path, 'tmp', 'ext', tmp_folder, 'task_state.json')
    if not os.path.exists(state_file):
        return ''

    try:
        with open(state_file, 'r', encoding='utf-8') as handle:
            return str(json.load(handle).get('status', '')).lower()
    except Exception:
        return ''


def main():
    base_path = sys.argv[1]
    tmp_folder = sys.argv[2]
    args = json.loads(sys.argv[3])
    cmd = sys.argv[4]
    stdout_path = sys.argv[5]
    stderr_path = sys.argv[6]

    with open(stdout_path, 'ab') as stdout_file, open(stderr_path, 'ab') as stderr_file:
        process = subprocess.Popen(args, stdout=stdout_file, stderr=stderr_file)
        return_code = process.wait()

    status = _current_status(base_path, tmp_folder)
    if status in ('success', 'finished', 'failed', 'failure', 'error'):
        return return_code

    stdout = _read_text(stdout_path)
    stderr = _read_text(stderr_path)
    final_status = 'finished' if return_code == 0 else 'failed'
    _write_task_state(base_path, tmp_folder, final_status, stdout=stdout, stderr=stderr, command=cmd)
    return return_code


if __name__ == '__main__':
    raise SystemExit(main())
