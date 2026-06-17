import os
import sys
import argparse
import jinja2
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from dataclasses import dataclass
from typing import List, Optional

console = Console()

@dataclass
class UvcInfo:
    """UVC 信息类"""
    uvc_name: str = ''
    version: str = ''
    mode: str = 'single'
    master_num: int = 1
    slave_num: int = 1
    agent_num: int = 1
    with_env: bool = False
    with_coverage: bool = False
    with_scoreboard: bool = False
    with_ref_model: bool = False

class UvcGen:
    """UVC 生成器类"""
    def __init__(self):
        self.uvc_name: str = ''
        self.file_list: List[Path] = []
        self.output: str = './'
        self.tpl_dir: Optional[str] = None
        self.version: str = ''
        self.mode: str = 'single'
        self.master_num: int = 1
        self.slave_num: int = 1
        self.agent_num: int = 1
        self.with_env: bool = False
        self.with_coverage: bool = False
        self.with_scoreboard: bool = False
        self.with_ref_model: bool = False

        script_dir = Path(__file__).resolve().parent
        self.TEMPLATES_DIR = script_dir / "templates"
        self.DEFAULT_TPL = str(self.TEMPLATES_DIR / "default" / "xxx_uvc")
        self.MSTSLV_TPL = str(self.TEMPLATES_DIR / "default" / "xxx_uvc_mstslv")

    def get_input_args(self) -> argparse.Namespace:
        """获取命令行参数"""
        parser = argparse.ArgumentParser(description='UVC Generator Tool')
        parser.add_argument('-t', '--tpl_dir', 
                          default=self.DEFAULT_TPL, 
                          help='UVC template directory path (absolute path or folder name in templates/)')
        parser.add_argument('-n', '--uvc_name', 
                          required=True,
                          help='UVC name')
        parser.add_argument('-o', '--output',
                          default=os.getcwd(),
                          help='Output directory path')
        parser.add_argument('-v', '--version',
                          default='v1.0',
                          help='UVC version')
        parser.add_argument('-m', '--mode',
                          choices=['single', 'mstslv'],
                          default='single',
                          help='Generation mode: single (default) or mstslv')
        parser.add_argument('--mst-num',
                          type=int, default=1,
                          help='Number of master agents (mstslv mode)')
        parser.add_argument('--slv-num',
                          type=int, default=1,
                          help='Number of slave agents (mstslv mode)')
        parser.add_argument('--agent-num',
                          type=int, default=1,
                          help='Number of agents (single mode)')
        parser.add_argument('--with-env',
                          action='store_true', default=False,
                          help='Enable env/env_cfg includes in package')
        parser.add_argument('--with-coverage',
                          action='store_true', default=False,
                          help='Enable coverage collector include in package')
        parser.add_argument('--with-scoreboard',
                          action='store_true', default=False,
                          help='Enable scoreboard include in package')
        parser.add_argument('--with-ref-model',
                          action='store_true', default=False,
                          help='Enable reference model include in package')
        return parser.parse_args()

    def _resolve_template_dir(self, tpl_dir: str) -> str:
        """解析模板目录路径

        Args:
            tpl_dir: 模板目录路径，可以是绝对路径或文件夹名

        Returns:
            解析后的绝对路径
        """
        # Handle mode aliases
        if tpl_dir == "mstslv":
            return self.MSTSLV_TPL

        tpl_path = Path(tpl_dir)

        # 如果是绝对路径且存在，直接返回
        if tpl_path.is_absolute() and tpl_path.exists():
            return str(tpl_path)

        # 如果是相对路径但存在，转换为绝对路径
        if tpl_path.exists():
            return str(tpl_path.resolve())

        # 尝试在templates目录下搜索匹配的文件夹
        if self.TEMPLATES_DIR.exists():
            for template_folder in self.TEMPLATES_DIR.iterdir():
                if template_folder.is_dir() and template_folder.name == tpl_dir:
                    # 检查是否包含xxx_uvc子目录
                    xxx_uvc_path = template_folder / "xxx_uvc"
                    if xxx_uvc_path.exists():
                        return str(xxx_uvc_path)
                    else:
                        return str(template_folder)

        # 如果都找不到，返回原始路径（让后续的存在性检查处理错误）
        return tpl_dir

    def init_para(self, tpl_dir: str, uvc_name: str, version: str, output: str,
                  mode: str = 'single', master_num: int = 1, slave_num: int = 1,
                  agent_num: int = 1, with_env: bool = False,
                  with_coverage: bool = False, with_scoreboard: bool = False,
                  with_ref_model: bool = False) -> None:
        """初始化参数"""
        self.mode = mode
        self.master_num = master_num
        self.slave_num = slave_num
        self.agent_num = agent_num
        self.with_env = with_env
        self.with_coverage = with_coverage
        self.with_scoreboard = with_scoreboard
        self.with_ref_model = with_ref_model

        # If tpl_dir is the default and mode is mstslv, switch to mstslv template
        if mode == 'mstslv' and tpl_dir == self.DEFAULT_TPL:
            tpl_dir = self.MSTSLV_TPL

        # 处理模板目录路径
        resolved_tpl_dir = self._resolve_template_dir(tpl_dir)

        if not Path(resolved_tpl_dir).exists():
            raise FileNotFoundError(f"Template directory not found: {resolved_tpl_dir}")

        self.tpl_dir = resolved_tpl_dir
        self.uvc_name = uvc_name
        self.version = version
        self.output = output

    def parse_tpl_dir(self) -> List[Path]:
        """解析模板目录"""
        file_list = []
        p = Path(self.tpl_dir)
        
        console.print(Panel(f"[bold cyan]Template Directory[/]\n{p.resolve()}", expand=False))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Parsing template files...", total=None)
            
            try:
                for file_path in p.iterdir():
                    if file_path.is_file():
                        #progress.console.print(f"[green]Found:[/] {file_path.name}")
                        file_list.append(file_path)
            except Exception as e:
                console.print(f"[red]Error parsing template directory:[/] {str(e)}")
                raise
            
            progress.update(task, completed=True)
        
        self.file_list = file_list
        return file_list

    def generate_uvc(self) -> None:
        """生成 UVC 文件"""
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.tpl_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 确定输出目录
        out_dir = Path(self.output).joinpath(
            f'{self.uvc_name}_uvc',
            self.version if self.version else ''
        )
        console.print(Panel(f"[bold cyan]Output Directory[/]\n{out_dir.resolve()}", expand=False))
        
        # Auto-implicate --with-env when agent_num >= 2
        if self.mode == 'single' and self.agent_num >= 2 and not self.with_env:
            self.with_env = True
            console.print("[yellow]Note:[/] --agent-num >= 2 implies --with-env (env_cfg required)")

        uvc_info = UvcInfo(
            uvc_name=self.uvc_name,
            version=self.version,
            mode=self.mode,
            master_num=self.master_num,
            slave_num=self.slave_num,
            agent_num=self.agent_num,
            with_env=self.with_env,
            with_coverage=self.with_coverage,
            with_scoreboard=self.with_scoreboard,
            with_ref_model=self.with_ref_model
        )

        # Filter out env_cfg template when single-agent mode
        file_list = self.file_list
        if self.mode == 'single' and self.agent_num <= 1:
            file_list = [f for f in file_list
                         if f.name != 'xxx_environment_cfg.sv']

        # Filter out optional component templates when not requested
        optional_skip = set()
        if not self.with_coverage:
            optional_skip.add('xxx_coverage.sv')
        if not self.with_scoreboard:
            optional_skip.add('xxx_scoreboard.sv')
        if not self.with_ref_model:
            optional_skip.add('xxx_ref_model.sv')
        if optional_skip:
            file_list = [f for f in file_list if f.name not in optional_skip]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Generating UVC files...",
                total=len(file_list)
            )

            for file_path in file_list:
                try:
                    rel_path = file_path.relative_to(self.tpl_dir)
                    output_path = out_dir.joinpath(rel_path)

                    # 修改文件名前缀
                    if output_path.name.startswith('xxx_'):
                        new_filename = output_path.name.replace('xxx_', f'{self.uvc_name}_', 1)
                        output_path = output_path.with_name(new_filename)

                    # 创建输出文件夹
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    # 读取并渲染模板
                    content = file_path.read_text(encoding='utf-8')
                    template = env.from_string(content)
                    rendered_content = template.render(uvc_info=uvc_info)
                    
                    # 写入文件
                    output_path.write_text(rendered_content, encoding='utf-8')
                    #progress.console.print(f"[green]✓[/] Generated: {output_path.name}")
                
                except jinja2.TemplateError as e:
                    progress.console.print(f"[red]✗[/] Template error in {file_path.name}: {str(e)}")
                    continue
                except Exception as e:
                    progress.console.print(f"[red]✗[/] Error processing {file_path.name}: {str(e)}")
                    continue
                
                progress.advance(task)

        # 创建 latest 符号链接
        if self.version:
            try:
                latest_link = Path(self.output).joinpath(f'{self.uvc_name}_uvc', 'latest')
                if latest_link.exists():
                    latest_link.unlink()
                latest_link.symlink_to(self.version)
                console.print(f"[green]✓[/] Created symbolic link: {latest_link} -> {self.version}")
            except Exception as e:
                console.print(f"[red]✗[/] Failed to create symbolic link: {str(e)}")

def main() -> int:
    """主函数"""
    try:
        uvc_gen = UvcGen()
        args = uvc_gen.get_input_args()
        uvc_gen.init_para(args.tpl_dir, args.uvc_name, args.version, args.output,
                          mode=args.mode, master_num=args.mst_num, slave_num=args.slv_num,
                          agent_num=args.agent_num, with_env=args.with_env,
                          with_coverage=args.with_coverage, with_scoreboard=args.with_scoreboard,
                          with_ref_model=args.with_ref_model)
        uvc_gen.parse_tpl_dir()
        uvc_gen.generate_uvc()
        return 0
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
