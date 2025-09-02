import os
import shutil
import sys

from biolib._internal.templates import templates


def add_gui_files(force=False, silent=False) -> None:
    cwd = os.getcwd()
    template_dir = templates.gui_template()

    root_files = ['package.json', 'Dockerfile', 'index.html', 'vite.config.mts', '.yarnrc.yml']

    conflicting_files = []

    # Copy root_files to init_template root and rest to subdirectory
    for root, _, filenames in os.walk(template_dir):
        relative_dir = os.path.relpath(root, template_dir)

        for filename in filenames:
            if filename in root_files:
                destination_dir = cwd
            else:
                if relative_dir == '.':
                    destination_dir = os.path.join(cwd, 'gui')
                else:
                    destination_dir = os.path.join(cwd, 'gui', relative_dir)

            source_file = os.path.join(root, filename)
            destination_file = os.path.join(destination_dir, filename)

            if filename == 'Dockerfile':
                force = True

            if os.path.exists(destination_file) and not force:
                with open(source_file, 'rb') as fsrc, open(destination_file, 'rb') as fdest:
                    if fsrc.read() != fdest.read():
                        conflicting_files.append(os.path.relpath(destination_file, cwd))
            else:
                os.makedirs(destination_dir, exist_ok=True)
                shutil.copy2(source_file, destination_file)

    gitignore_path = os.path.join(cwd, '.gitignore')
    with open(gitignore_path, 'a') as gitignore_file:
        gitignore_file.write('\n# gui\n')
        gitignore_file.write('.yarn\n')
        gitignore_file.write('dist\n')
        gitignore_file.write('yarn.lock\n')
        gitignore_file.write('tsconfig.tsbuildinfo\n')
        gitignore_file.write('node_modules\n')

    if conflicting_files:
        print('The following files were not overwritten. Use --force to override them:', file=sys.stderr)
        for conflicting_file in list(set(conflicting_files)):
            print(f'  {conflicting_file}', file=sys.stderr)
        exit(1)

    if not silent:
        print('gui files added to project root and gui/ subdirectory')
