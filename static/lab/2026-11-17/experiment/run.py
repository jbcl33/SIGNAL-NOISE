#!/usr/bin/env python3
"""Reproduce the issue's ERC experiment with KiCad 9 CLI; no PCB/hardware test."""
from pathlib import Path
import json, os, shutil, subprocess, hashlib, tempfile


def main():
    here = Path(__file__).resolve().parent
    output = here / 'results'
    output.mkdir(exist_ok=True)
    runtime = Path(tempfile.mkdtemp(prefix='signal-noise-kicad-'))
    env = os.environ.copy()
    for key, sub in [('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache'), ('XDG_DATA_HOME', 'data')]:
        folder = runtime / sub
        folder.mkdir(parents=True, exist_ok=True)
        env[key] = str(folder)
    cli = shutil.which('kicad-cli')
    if cli is None:
        raise SystemExit('Install KiCad 9 CLI, then run this script again.')
    version = subprocess.run([cli, 'version'], capture_output=True, text=True, env=env, check=True).stdout.strip()
    commands = [
        ('good-strict', ['sch', 'erc', '--format', 'json', '--severity-all', '--exit-code-violations', '-o', str(output / 'good-strict.json'), str(here / 'good.kicad_sch')]),
        ('bad-strict', ['sch', 'erc', '--format', 'json', '--severity-all', '--exit-code-violations', '-o', str(output / 'bad-strict.json'), str(here / 'bad.kicad_sch')]),
        ('bad-default', ['sch', 'erc', '--format', 'json', '--severity-all', '-o', str(output / 'bad-default.json'), str(here / 'bad.kicad_sch')]),
        ('bad-netlist', ['sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(output / 'bad.net'), str(here / 'bad.kicad_sch')]),
        ('good-svg', ['sch', 'export', 'svg', '--black-and-white', '--exclude-drawing-sheet', '-o', str(output / 'svg'), str(here / 'good.kicad_sch')]),
        ('bad-svg', ['sch', 'export', 'svg', '--black-and-white', '--exclude-drawing-sheet', '-o', str(output / 'svg'), str(here / 'bad.kicad_sch')]),
    ]
    runs = []
    for name, args in commands:
        result = subprocess.run([cli, *args], capture_output=True, text=True, env=env)
        (output / (name + '.log')).write_text(result.stdout + result.stderr)
        entry = dict(name=name, command=['kicad-cli', *[a.replace(str(here) + '/', '') for a in args]], exitCode=result.returncode)
        if name in ('good-strict', 'bad-strict', 'bad-default'):
            report = json.loads((output / (name + '.json')).read_text())
            violations = [v for sheet in report['sheets'] for v in sheet['violations']]
            entry['violationCount'] = len(violations)
            entry['violationTypes'] = [v['type'] for v in violations]
        runs.append(entry)
    inputs = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in here.iterdir() if p.suffix in ('.kicad_sch', '.kicad_sym', '.kicad_pro') or p.name == 'sym-lib-table'}
    data = dict(kicadVersion=version, inputs=inputs, runs=runs, scope='Software ERC and exports only; no board fabrication, circuit simulation or hardware test.')
    (output / 'summary.json').write_text(json.dumps(data, indent=2) + '\n')
    expected = [('good-strict', 0, 0), ('bad-strict', 5, 1), ('bad-default', 0, 1)]
    for name, code, count in expected:
        actual = next(x for x in runs if x['name'] == name)
        if (actual['exitCode'], actual['violationCount']) != (code, count):
            raise SystemExit(f'Unexpected ERC result for {name}: inspect results/summary.json')
    if any(x['exitCode'] != 0 for x in runs if x['name'].endswith(('netlist', 'svg'))):
        raise SystemExit('Export failed: inspect logs')
    shutil.rmtree(runtime)
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
