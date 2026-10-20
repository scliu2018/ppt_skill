#!/usr/bin/env python3
"""Download selected public slide PDFs into the ignored local reference library."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def fetch(source, force=False):
    dest = (ROOT / source['local_file']).resolve()
    dest.relative_to(ROOT / '.local')
    expected = source.get('sha256')
    if dest.exists() and not force:
        if dest.read_bytes()[:5] != b'%PDF-':
            raise ValueError(f'{dest.name}: existing file is not a PDF')
        digest = sha256(dest)
        if expected and digest != expected:
            raise ValueError(f'{dest.name}: existing checksum differs; inspect before replacing')
        return {'id': source['id'], 'status': 'cached', 'bytes': dest.stat().st_size, 'sha256': digest}
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        request = Request(source['download_url'], headers={'User-Agent': 'ppt-skill-reference-fetcher/1.0'})
        with urlopen(request, timeout=60) as response, tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as out:
            temp = Path(out.name)
            total = 0
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > 150 * 1024 * 1024:
                    raise ValueError('Download exceeds 150 MiB')
                out.write(chunk)
        with temp.open('rb') as stream:
            if stream.read(5) != b'%PDF-':
                raise ValueError('Server did not return a PDF')
        digest = sha256(temp)
        if expected and digest != expected:
            raise ValueError('Remote file changed; inspect the new version and update the manifest deliberately')
        temp.replace(dest)
        return {'id': source['id'], 'status': 'downloaded', 'bytes': total, 'sha256': digest}
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--id', action='append', help='Source ID; repeat to select multiple sources')
    parser.add_argument('--force', action='store_true', help='Re-download, while still requiring the pinned checksum')
    args = parser.parse_args()
    sources = json.loads((ROOT / 'references/sources.json').read_text())['sources']
    known = {s['id'] for s in sources}
    unknown = set(args.id or []) - known
    if unknown:
        parser.error(f'Unknown source IDs: {sorted(unknown)}')
    results = []
    for source in sources:
        if args.id and source['id'] not in args.id:
            continue
        try:
            result = fetch(source, args.force)
        except Exception as exc:
            result = {'id': source['id'], 'status': 'failed', 'error': str(exc)}
        print(json.dumps(result, ensure_ascii=False), flush=True)
        results.append(result)
    report = ROOT / '.local/download-report.json'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
    return int(any(r['status'] == 'failed' for r in results))


if __name__ == '__main__':
    sys.exit(main())
