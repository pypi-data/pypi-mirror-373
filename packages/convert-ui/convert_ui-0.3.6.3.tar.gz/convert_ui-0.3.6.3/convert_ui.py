import os, sys
import subprocess
import argparse
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn
from rich_argparse import RichHelpFormatter
# 导入 importlib.metadata
try:
    from importlib.metadata import version
except ImportError:
    # Python 3.8 之前需要安装 importlib-metadata
    from importlib_metadata import version


# 创建 Rich Console 对象
console = Console()

def find_pyside6_uic():
    """
    查找 pyside6-uic 工具路径。
    """
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        if sys.platform == "win32":
            uic_path = os.path.join(venv_path, 'Scripts', 'pyside6-uic.exe')
        else:
            uic_path = os.path.join(venv_path, 'bin', 'pyside6-uic')
        if os.path.exists(uic_path):
            return uic_path
    return 'pyside6-uic'


def convert_ui_file(ui_file, output_dir):
    """
    将单个 .ui 文件转换为 .py 文件。
    """
    if not os.path.isfile(ui_file):
        console.print(f"[red]错误:[/red] 找不到 UI 文件 '[yellow]{ui_file}[/yellow]'")
        return

    os.makedirs(output_dir, exist_ok=True)

    uic_path = find_pyside6_uic()
    py_filename = os.path.splitext(os.path.basename(ui_file))[0] + ".py"
    py_path = os.path.join(output_dir, py_filename)

    console.print(f"[bold]正在转换[/bold] '[cyan]{ui_file}[/cyan]' -> '[green]{py_path}[/green]'...")
    try:
        subprocess.run([uic_path, ui_file, "-o", py_path], check=True)
        console.print("[bold green]转换成功。[/bold green]")
    except FileNotFoundError:
        console.print(
            f"[red]错误:[/red] 找不到 '[yellow]{uic_path}[/yellow]'。请确保 PySide6 已经安装，并且该工具在系统 PATH 中。")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]转换失败:[/red] {e}")
    except Exception as e:
        console.print(f"[red]发生未知错误:[/red] {e}")


def collect_ui_files(paths):
    """
    根据输入路径列表收集所有 .ui 文件。
    paths 可以是文件或文件夹。
    """
    ui_files = []
    for p in paths:
        if os.path.isfile(p) and p.endswith(".ui"):
            ui_files.append(p)
        elif os.path.isdir(p):
            for f in os.listdir(p):
                full_path = os.path.join(p, f)
                if os.path.isfile(full_path) and f.endswith(".ui"):
                    ui_files.append(full_path)
    return ui_files


def main():
    """
    主函数，处理命令行参数和转换逻辑。
    """

    # ! 从 pyproject.toml 文件中动态获取版本信息
    try:
        current_version = version("convert-ui") # 这里的名字要和 pyproject.toml 中的 [project] name 对应
    except Exception:
        current_version = "unknown" # 如果包没有安装，就显示 unknown

    usage_string = ("[dim]convert_ui[/] [bold cyan][-t[/] "
                    "[bold green]UI_FILE(S)[/]"
                    "[bold cyan]][/] "
                    "[bold cyan][-p[/] "
                    "[bold green]OUTPUT_DIR[/]"
                    "[bold cyan]][/]")
    # 开启 usage 着色
    RichHelpFormatter.usage_markup = True
    # argparse 继续用 RichHelpFormatter
    parser = argparse.ArgumentParser(
        prog="convert_ui",
        usage=usage_string,  # 将包含 Rich 标记的字符串传递给 usage
        formatter_class=RichHelpFormatter,  # 使用 Rich 的解析器，美化输出
        add_help=False,
    )

    parser.add_argument(
        "-h", "--help",
        action="help",
        help="显示帮助信息"
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="显示版本信息"
    )
    parser.add_argument(
        "-t", "--target",
        # nargs="+",
        metavar="Target UI File(s)",
        help="指定一个或多个 .ui 文件或文件夹路径 [dim](默认: 当前目录下所有 .ui 文件)[/dim]"
    )
    parser.add_argument(
        "-p", "--path",
        metavar="Output DIR",
        help="指定生成 PyQt 文件存储的文件夹路径 [dim](默认: ./ui_files)[/dim]"
    )


    # * 解析外部获取的参数
    args = parser.parse_args()
    
    if args.version:
        console.print(f"[bold yellow]VERSION[/] [bold blue]'v{current_version}'[/]")
        return

    output_dir = args.path if args.path else os.path.join(os.getcwd(), "ui_files")

    if args.target:
        ui_files = collect_ui_files(args.target)
    else:
        cwd = os.getcwd()
        ui_files = [os.path.join(cwd, f) for f in os.listdir(cwd) if f.endswith(".ui")]

    if not ui_files:
        console.print("[yellow]未找到任何 .ui 文件可以转换。[/yellow]")
        return

    # 使用 Rich Progress 动态显示进度条
    with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            console=console,
    ) as progress:
        task = progress.add_task("[cyan]转换中...", total=len(ui_files))
        for ui_file in ui_files:
            convert_ui_file(ui_file, output_dir)
            progress.update(task, advance=1)


if __name__ == "__main__":
    main()