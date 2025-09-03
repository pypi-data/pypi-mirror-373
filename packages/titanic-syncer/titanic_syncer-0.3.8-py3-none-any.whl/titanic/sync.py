import os
import re
import sqlite3
import subprocess
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn


def rsync_with_includes(remote_server, source, destination, includes):
    includes = [f"{include[:3]}/{include}" for include in includes]

    with open('/tmp/includes.txt', 'w') as f:
        f.write("\n".join(includes))

    rsync_command = ["rsync", "-azl", "--progress", "--include-from=/tmp/includes.txt", "--include=*/", "--exclude=*"] + [f"{remote_server}:{source}/", destination]

    total_files = len(includes)
    # count number of files already in destination
    for include in includes:
        if os.path.exists(f"{destination}/{include}"):
            total_files -= 1

    file_transfer_pattern = re.compile(r"chk=\d+/\d+")

    console = Console(force_terminal=True)

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.completed]{task.completed}/{task.total} files",
        TimeRemainingColumn(),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task("Syncing files...", total=total_files)

        process = subprocess.Popen(rsync_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for line in process.stdout:
            if file_transfer_pattern.search(line):
                progress.advance(task)

        process.wait()
        if process.returncode != 0:
            raise Exception("rsync failed")


def sync_metadata_and_files(local_db_cursor, remote_server, project_id, remote_metadata_path, store_dir, remote_store_dir):
    remote_metadata_clone_path = '/tmp/titanic-metadata.db'

    subprocess.run(["rsync", "-avz", f"{remote_server}:{remote_metadata_path}", remote_metadata_clone_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    conn = sqlite3.connect(remote_metadata_clone_path)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM files WHERE project_id = ?', (project_id,))
    except sqlite3.OperationalError:
        print("Project ID not found in remote metadata")
        return False
    files_to_process = cursor.fetchall()

    for file_info in files_to_process:
        file_path = file_info[1]
        file_hash = file_info[2]
        file_mode = file_info[3]
        local_db_cursor.execute('INSERT INTO files (path, hash, mode, project_id) VALUES (?, ?, ?, ?)', (file_path, file_hash, file_mode, project_id))

    includes = [file_info[2] for file_info in files_to_process]

    rsync_with_includes(remote_server, remote_store_dir, store_dir, includes)
    return True
