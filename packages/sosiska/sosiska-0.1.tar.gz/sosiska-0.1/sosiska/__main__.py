# sosiska - DNS downloader
# Copyright (C) 2025  bitrate16 (bitrate16@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import os
import multiprocessing.pool
import multiprocessing
import sqlite3
import socket
import threading
import itertools
import ipaddress
import time
import tqdm

import dns
import dns.reversename
import dns.resolver
import dns.rdtypes
import dns.rdtypes.ANY
import dns.rdtypes.ANY.PTR


# llm-generated whatever i didn't check
def get_args():
    parser = argparse.ArgumentParser(description="Process data with configurable parameters.")

    parser.add_argument(
        "--database",
        type=str,
        default='dns.db',
        help="Path to the SQLite database"
    )

    parser.add_argument(
        "--batch_size",
        type=int,
        default=64,
        help="Size of the batch (default: 64)"
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=multiprocessing.cpu_count(),
        help="Number of threads to use (defaults to CPU core count)"
    )

    parser.add_argument(
        "--subnet",
        type=str,
        required=True,
        help="IP subnet in CIDR notation (e.g., 1.2.3.0/24 or 2001:db8::/32)"
    )

    return parser.parse_args()


def create_db(database: str) -> sqlite3.Connection:
    conn = sqlite3.connect(database, check_same_thread=False)
    conn.execute("""
CREATE TABLE IF NOT EXISTS dns (
    timestamp BIGINT,
    ip BLOB,
    name TEXT
)
    """)

    return conn


def insert_many(
    conn: sqlite3.Connection,
    timestamp: int,
    batch: list[tuple[str, str]],
):
    pack = []
    for (ip, name) in batch:
        ip_bytes = ipaddress.inet_aton(ip)
        pack.append((timestamp, ip_bytes, name))

    conn.executemany("INSERT INTO dns (timestamp, ip, name) VALUES (?, ?, ?)", pack)


def resolve(ip: str) -> str | None:
    try:
        rev_name = dns.reversename.from_address(ip)
        name = str(dns.resolver.resolve(rev_name, 'PTR')[0])

        if len(name) == 0:
            return None

        if name[-1] == '.':
            name = name[:-1]
    except dns.resolver.NXDOMAIN:
        return None

    return name


def batch(iterable, total: int, batch_size: int):
    it = iter(iterable)

    for ndx in range(0, total, batch_size):
        batch = tuple(itertools.islice(it, batch_size))
        if not batch:
            return
        yield batch


def main():
    args = get_args()

    timestamp = round(time.time() * 1000)
    subnet = ipaddress.ip_network(args.subnet)
    conn = create_db(args.database)

    progress = tqdm.tqdm(total=subnet.num_addresses)
    lock = threading.Lock()

    def worker(addr_batch) -> None:
        to_add = []

        for index, addr in enumerate(addr_batch):
            ip = str(addr)
            name = resolve(ip)

            if name is not None:
                to_add.append((ip, name))
                print(f'{ ip } is { name }', flush=True)

        with lock:
            progress.update(index)
            insert_many(conn, timestamp, to_add)

    pool = multiprocessing.pool.ThreadPool(processes=args.threads)
    map = pool.imap(
        worker,
        batch(
            subnet,
            subnet.num_addresses,
            args.batch_size,
        ),
    )
    for _ in map:
        pass


if __name__ == '__main__':
    main()
