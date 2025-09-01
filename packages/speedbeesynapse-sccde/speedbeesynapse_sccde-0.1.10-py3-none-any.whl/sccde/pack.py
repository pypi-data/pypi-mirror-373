"""SCCDE packaging module.."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from . import utils

PACKAGE_SUFFIX = '.sccpkg'

def distribute(info_path: Path, info: dict, target_dir: Path) -> None:
    """Put sccde package into the specified directory."""
    # テスト専用コンポーネントは除外
    for compo_id, compo_info in info['components'].items():
        if compo_info.get('test-only', False):
            del info['components'][compo_id]

    # 一時ディレクトリを作成
    target_python_dir = (target_dir / 'python')
    # not use now: target_so_dir = (target_dir / 'so')

    # Pythonソースディレクトリをコピー
    if 'python-components-source-dir' in info:
        python_dir = info_path.parent / info['python-components-source-dir']
        if python_dir.is_dir():
            copy_python_dir(python_dir, target_python_dir)
        info['python-components-source-dir'] = 'python'

    # パラメータ画面カスタム設定ファイルをコピー
    for compo_info in info['components'].values():
        copy_parameter_ui(info_path, compo_info, target_dir)

    # パッケージ情報ファイルを作成
    with (target_dir / 'scc-package-info.json').open(mode='w', encoding='utf-8') as fo:
        json.dump(info, fo, ensure_ascii=False, indent=2)
        fo.write('\n')


def make_package(info_path: Path, info: dict, zippath: Optional[Path]) -> None:
    """Make sccde package."""
    # 出力するzipファイルパスを決定
    if zippath:
        outfile = zippath.with_suffix(PACKAGE_SUFFIX)
    else:
        basename = info['package-name'].replace(' ', '_').lower()
        outfile = info_path.parent / f'{basename}{PACKAGE_SUFFIX}'

    # テスト専用コンポーネントは除外
    for compo_id, compo_info in info['components'].items():
        if compo_info.get('test-only', False):
            del info['components'][compo_id]

    # 一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        target_python_dir = (tmpdir / 'python')
        # not use now: target_so_dir = (tmpdir / 'so')

        # Pythonソースディレクトリをコピー
        if 'python-components-source-dir' in info:
            python_dir = info_path.parent / info['python-components-source-dir']
            if python_dir.is_dir():
                copy_python_dir(python_dir, target_python_dir)
            info['python-components-source-dir'] = 'python'

        # パラメータ画面カスタム設定ファイルをコピー
        for compo_info in info['components'].values():
            copy_parameter_ui(info_path, compo_info, tmpdir)

        # パッケージ情報ファイルを作成
        with (tmpdir / 'scc-package-info.json').open(mode='w', encoding='utf-8') as fo:
            json.dump(info, fo, ensure_ascii=False, indent=2)
            fo.write('\n')

        # zipファイルを生成、拡張子'.zip'を除去
        shutil.make_archive(str(outfile), 'zip', tmpdir, '.')
        outfile.unlink(missing_ok=True)
        Path(str(outfile) + '.zip').rename(outfile)


def copy_python_dir(source: Path, dest: Path) -> None:
    """Copy contents of `source` dirctory into `dest` directory."""
    shutil.copytree(source, dest, dirs_exist_ok=True)


def copy_parameter_ui(info_path: Path, compo_info: dict, dest: Path) -> None:
    """Copy parameter ui file into temporal directory."""
    ui_type = compo_info.get('parameter-ui-type', 'none')
    if ui_type == 'json':
        uifile = compo_info.get('parameter-ui')
        if uifile:
            destfile = dest / uifile
            destfile.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(info_path.parent / uifile, dest / uifile)
        else:
            utils.print_error('Invalid parameter ui setting.')
    elif ui_type == 'html':
        ui_html_dir = compo_info.get('parameter-ui')
        if ui_html_dir:
            destfile = dest / ui_html_dir
            destfile.mkdir(parents=True, exist_ok=True)
            shutil.copytree(info_path.parent / ui_html_dir, dest / ui_html_dir, dirs_exist_ok=True)
        else:
            utils.print_error('Invalid parameter ui setting.')
    else:
        pass
