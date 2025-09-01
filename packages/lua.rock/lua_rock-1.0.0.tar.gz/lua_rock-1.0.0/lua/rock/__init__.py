#!/usr/bin/python3
from luadata.luatable import LuaTable, GetRuntime
from zipfile import ZipFile, ZIP_DEFLATED
from hashlib import md5
import platform
import argparse
from pathlib import Path
root='rock_manifest'

architectures={
'i386': 'x86',
'i486': 'x86',
'i586': 'x86',
'i686': 'x86',
's390x': 's390',
'armv7l': 'arm',
'armv6l': 'arm'
}

def list_rock_directory(path):
    path_pool = [path]
    while path_pool:
        for file in path_pool.pop().iterdir():
            if file.is_dir():
                path_pool.append(file)
            else:
                parts = file.relative_to(path).parent.parts
                if parts or file.name != 'rock_manifest':
                    yield file, parts

def zippath(file, parts):
    return Path('').joinpath(*parts,file.name)

def write_manifest_part(file, parts, table):
    for i in parts:
        tab = table[i]
        if tab is None:
            tab = LuaTable()
            table[i] = tab
        table = tab
    table[file.name] = md5(file.open('rb').read()).hexdigest()

def create_rock(path, rockspec, dir, filename):
    with rockspec.open('r') as zipf:
        lua_text = zipf.read()
    run = GetRuntime()
    run.execute(lua_text)
    globs = run.globals()
    version = globs['version']
    package = globs['package']
    if not filename:
        filename = get_filename(path, package, version)
    rockfile = dir.joinpath(filename).absolute()
    rockfile.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(rockfile, 'w', ZIP_DEFLATED) as zipf:
        table = LuaTable()
        for file, parts in list_rock_directory(path):
            zipf.write(file, zippath(file, parts))
            write_manifest_part(file, parts, table)
        table[rockspec.name] = md5(lua_text.encode("utf-8")).hexdigest()
        zipf.writestr(f'{package}-{version}.rockspec', lua_text)
        zipf.writestr(root, f'{root} = {str(table)}')


def get_filename(path, package, version):
    system = platform.system()
    libdir = path.joinpath('lib')
    if libdir.is_dir() and next(libdir.iterdir(), False):
        machine = platform.machine()
        machine = architectures.get(machine, machine)
    else:
        machine = 'all'
    return f'{package}-{version}.{system}-{machine}.rock'.lower()

r = '/extra/home/suse/Desktop/local/gitfetch/lua-cjson/lua_data'

def main_create_rock(args=None):
    parser = argparse.ArgumentParser(description="A Python script that generates a rockspec file")
    # mainparser.print_help()
    # add noop operation
    parser.add_argument("--noop", help='', type=str, default='disable')
    # add directory path
    parser.add_argument('--srcdir', help='Directory to convert to rock file', type=Path, required=True)
    # add rockspec file
    parser.add_argument('--rockspec', help='Rockspec file', type=Path, required=True)
    # add path where rock file will be generated
    parser.add_argument('--outdir', help='Directory path where rock file will be generated', type=Path, default='.')
    # add basename for rock file
    parser.add_argument('--filename', help="File name", type=str, default='')
    args = parser.parse_args(args)
    if args.noop != 'enable':
        create_rock(args.srcdir, args.rockspec, args.outdir, args.filename)

