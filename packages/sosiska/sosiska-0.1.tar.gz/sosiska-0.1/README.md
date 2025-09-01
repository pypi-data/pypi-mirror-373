# sosiska 🌭 - DNS downloader

Ever wanted to download DNS? Now you can

# Why it is called so?

Because I need to go touch some grass.

# How to use

This will blow up your DNS server

```bash
python -m sosiska --subnet '0.0.0.0/0' --batch_size 64 --threads 64 --database dns.db
```

It iterates through subnet, collects domain names using PTR request and writes into sqlite database with startup timestamp

# LICENSE

```
sosiska - DNS downloader
Copyright (C) 2025  bitrate16 (bitrate16@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
