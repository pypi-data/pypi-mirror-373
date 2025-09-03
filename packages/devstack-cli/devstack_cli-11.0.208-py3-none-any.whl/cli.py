import argparse
import asyncio
import configparser
import contextlib
import datetime
import functools
import io
import itertools
import json
import logging
import os
import pathlib
import re
import readline
import shlex
import shutil
import signal
import stat
import string
import sys
import termios
import tty
import typing

import aiofiles
import aiohttp
import asyncssh
import paramiko
import paramiko.sftp_client
import rich.console
import rich.highlighter
import rich.json
import rich.logging
import rich.markup
import rich.pretty
import rich.progress
import watchdog.events
import watchdog.observers
import yarl

import version


def sigint_handler(signum: int, frame, *, cli: 'Cli') -> None:
    if cli.terminal_process is None:
        return
    #cli.terminal_process.send_signal(signal.SIGINT)
    cli.terminal_process.stdin.write('\x03')


EVENT_DEBOUNCE_SECONDS = .5
RETRY_DELAY_SECONDS = 30

logging.basicConfig(level=logging.INFO, handlers=[], format='%(message)s')
logger = logging.getLogger('cli')
logger.addHandler(rich.logging.RichHandler())
json_logger = logging.getLogger('cli-json')
json_logger.addHandler(rich.logging.RichHandler(highlighter=rich.highlighter.JSONHighlighter()))

def is_valid_username(username: str) -> bool:
    return re.match(r'^[a-zA-Z0-9]+[a-zA-Z0-9_.-]*$', username) is not None

def is_valid_hostname(hostname: str) -> bool:
    return re.match(r'^([a-zA-Z0-9][a-zA-Z0-9-]*\.)*([a-zA-Z0-9][a-zA-Z0-9-]*)$', hostname) is not None

def is_valid_path(path: str) -> bool:
    return re.match(r'^[a-zA-Z0-9/_.,\-+ ]+$', path) is not None

def ensure_valid_username(username: str) -> str:
    if not is_valid_username(username):
        raise ValueError(f'Invalid username: "{username}". Username must start with an alphanumeric character, and contain only alphanumeric characters, dots, underscores and hyphens.')
    return username

def ensure_valid_hostname(hostname: str) -> str:
    if not is_valid_hostname(hostname):
        raise ValueError(f'Invalid hostname: "{hostname}". Hostname must start with an alphanumeric character, and contain only alphanumeric characters, dots, and hyphens.')
    return hostname

def ensure_valid_path(path: str) -> str:
    if not is_valid_path(path):
        raise ValueError(f'Invalid path: "{path}". Path must start with an alphanumeric character, and contain only alphanumeric characters, slashes, dots, underscores, commas, pluses, hyphens, and spaces.')
    return path

class SubprocessError(Exception):
    """A subprocess call returned with non-zero."""


class InitializationError(Exception):
    """Initialization of devstack-cli failed"""


class FileSystemEventHandlerToQueue(watchdog.events.FileSystemEventHandler):
    def __init__(
            self: 'FileSystemEventHandlerToQueue',
            queue: asyncio.Queue,
            loop: asyncio.BaseEventLoop,
            *args,
            **kwargs,
    ) -> None:
        self._loop = loop
        self._queue = queue
        super(*args, **kwargs)

    def on_any_event(
            self: 'FileSystemEventHandlerToQueue',
            event: watchdog.events.FileSystemEvent,
    ) -> None:
        if event.event_type in (
                watchdog.events.EVENT_TYPE_OPENED,
                watchdog.events.EVENT_TYPE_CLOSED,
                watchdog.events.EVENT_TYPE_CLOSED_NO_WRITE,
        ):
            return
        if event.event_type == watchdog.events.EVENT_TYPE_MODIFIED and event.is_directory:
            return
        if '/.git' in event.src_path:
            return
        if hasattr(event, 'dest_path') and '/.git' in event.dest_path:
            return
        self._loop.call_soon_threadsafe(self._queue.put_nowait, event)


async def run_subprocess(
        program: str,
        args: typing.List[str],
        *,
        name: str,
        cwd: typing.Optional[pathlib.Path] = None,
        env: typing.Optional[dict] = None,
        capture_stdout: bool = True,
        print_stdout: bool = True,
        capture_stderr: bool = True,
        print_stderr: bool = True,
        print_to_debug_log: bool = False,
) -> None:
    args_str = ' '.join(args)
    process = await asyncio.create_subprocess_exec(
        program,
        *args,
        cwd=cwd,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE if capture_stdout else asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE if capture_stderr else asyncio.subprocess.DEVNULL,
        env=env,
    )
    stdout = b''
    stderr = b''
    try:
        if not capture_stdout and not capture_stderr:
            await process.wait()
        else:
            tasks = set()
            if capture_stdout:
                stdout_readline = asyncio.create_task(process.stdout.readline())
                tasks.add(stdout_readline)
            if capture_stderr:
                stderr_readline = asyncio.create_task(process.stderr.readline())
                tasks.add(stderr_readline)
            while process.returncode is None:
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                if capture_stdout and stdout_readline in done:
                    stdout_line = await stdout_readline
                    if print_stdout and stdout_line.decode().strip():
                        if print_to_debug_log:
                            logger.debug('%s: %s', name, stdout_line.decode().strip())
                        else:
                            logger.info('%s: %s', name, stdout_line.decode().strip())
                    stdout += stdout_line + b'\n'
                    stdout_readline = asyncio.create_task(process.stdout.readline())
                    pending.add(stdout_readline)
                if capture_stderr and stderr_readline in done:
                    stderr_line = await stderr_readline
                    if print_stderr and stderr_line.decode().strip():
                        logger.warning('%s: %s', name, stderr_line.decode().strip())
                    stderr += stderr_line + b'\n'
                    stderr_readline = asyncio.create_task(process.stderr.readline())
                    pending.add(stderr_readline)
                tasks = pending
    finally:
        if process.returncode is None:
            logger.debug('Terminating "%s %s"', program, args_str)
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=3)
            except asyncio.TimeoutError:
                logger.info('Killing "%s %s"', program, args_str)
                process.kill()
                await asyncio.wait_for(process.wait(), timeout=3)
    if process.returncode:
        if cwd is None:
            msg = f'Command "{program} {args_str}" failed with returncode {process.returncode}.'
        else:
            msg = f'Command "{program} {args_str}" in "{cwd}" failed with returncode {process.returncode}.'
        raise SubprocessError(msg)
    logger.debug(
        'Command "%s %s" succeeded.',
        program,
        args_str,
    )
    return stdout, stderr


def _get_event_significant_path(event: watchdog.events.FileSystemEvent) -> str:
    if hasattr(event, 'dest_path') and event.dest_path != '':
        return event.dest_path
    return event.src_path


def _is_relative_to(self: pathlib.Path, other: pathlib.Path) -> bool:
    return pathlib.Path(other) == pathlib.Path(self) or pathlib.Path(other) in pathlib.Path(self).parents


async def _create_temp_file(
        *,
        exit_stack: contextlib.AsyncExitStack,
        content: typing.Union[bytes, str],
) -> aiofiles.tempfile.NamedTemporaryFile:
    temp_file = await exit_stack.enter_async_context(
        aiofiles.tempfile.NamedTemporaryFile(
            'wb+',
            delete=False,
        ),
    )
    await temp_file.write(content.encode() if isinstance(content, str) else content)
    await temp_file.close()
    return temp_file


class Cli:
    def __init__(self: 'Cli') -> None:
        self.config_file: typing.Optional[pathlib.Path] = None
        self.args: typing.Optional[argparse.Namespace] = None
        self.config: typing.Optional[configparser.ConfigParser] = None
        self.password: typing.Optional[str] = None
        self.session: typing.Optional[aiohttp.ClientSession] = None
        self.workspace_url: typing.Optional[yarl.URL] = None
        self.sync_task: typing.Optional[asyncio.Task] = None
        self.port_forwarding_task: typing.Optional[asyncio.Task] = None
        self.logs_task: typing.Optional[asyncio.Task] = None
        self.exit_stack: typing.Optional[contextlib.AsyncExitStack] = None
        self.cdes: typing.List[dict] = []
        self.cde: typing.Optional[dict] = None
        self.cde_type: typing.Optional[dict] = None
        self.ssh_client: typing.Optional[paramiko.SSHClient] = None
        self.sftp_client: typing.Optional[paramiko.sftp_client.SFTPClient] = None
        self.known_hosts_file: typing.Optional[aiofiles.tempfile.NamedTemporaryFile] = None
        self.console = rich.console.Console()
        self._fd = sys.stdin.fileno()
        self._tcattr = termios.tcgetattr(self._fd)
        self.terminal_process = None

    @property
    def cde_name(self: 'Cli') -> typing.Optional[str]:
        return self.cde['name'] if self.cde is not None else None

    @property
    def is_cde_running(self: 'Cli') -> bool:
        if self.cde is None:
            return None
        if not self.cde['exists_remotely']:
            return False
        return self.cde['value']['is-running'] and self.cde['provisioning_state'] == 'READY'

    @property
    def hostname(self: 'Cli') -> typing.Optional[str]:
        return self.cde['value']['hostname'] if self.cde is not None else None

    @property
    def local_source_directory(self: 'Cli') -> typing.Optional[pathlib.Path]:
        return pathlib.Path(os.path.expandvars(self.cde['source_directory'])) if self.cde else None

    @property
    def local_output_directory(self: 'Cli') -> typing.Optional[pathlib.Path]:
        return pathlib.Path(os.path.expandvars(self.cde['output_directory'])) if self.cde and self.cde.get('output_directory') else None

    async def run(self: 'Cli') -> None:
        try:
            self.loop = asyncio.get_running_loop()
            self.loop.add_signal_handler(
                signal.SIGWINCH,
                self._window_resized,
            )
            self.key_queue = asyncio.Queue()
            await self._parse_arguments()
            # print version after parse_arguments to avoid duplication when using "--version"
            rich.print(f'Cloudomation devstack-cli {version.MAJOR}+{version.BRANCH_NAME}.{version.BUILD_DATE}.{version.SHORT_SHA}')
            rich.print('''[bold white on blue]                                                                
                   :=+********+=:                               
                -+****************+-                            
              =**********************=                          
            :**************************:                        
           -****************************-:=+****+=:             
          .**************=-*************************:           
          =**************.  -************************-          
          ***************     -********++*************          
         .**************=       ::..     *************          
      .=****************:               *************:          
     =**************=-.               .**************+=:        
   .************+-.                  .*******************+:     
   **************=:                   +********************+    
  =*****************+=:                +*********************   
  **********************:               +********************=  
  **********************=      .--::..   *********************  
  =**********************    .=*******************************  
   **********************.  =********************************=  
   .+********************+=*********************************+   
     -*****************************************************=    
       -+************************************************=.     
          :-=+**************************************+=-.        
                                                                ''')  # noqa: W291
            async with self._key_press_to_queue(), \
                    aiohttp.ClientSession(trust_env=True) as self.session, \
                    contextlib.AsyncExitStack() as self.exit_stack:
                await self._load_global_config()
                await self._check_config()
                await self._print_help()
                await self._process_args()
                while True:
                    key_press = await self.key_queue.get()
                    await self._handle_key_press(key_press)
        except InitializationError as ex:
            logger.error(ex)  # noqa: TRY400
        except Exception:
            logger.exception('Unhandled exception')

    def _window_resized(self: 'Cli', *args, **kwargs) -> None:
        if self.terminal_process is None:
            return
        terminal_size = shutil.get_terminal_size()
        self.terminal_process.change_terminal_size(terminal_size.columns, terminal_size.lines)

    async def _parse_arguments(self: 'Cli') -> None:
        config_home = os.environ.get('XDG_CONFIG_HOME', '$HOME/.config')
        default_config_file = pathlib.Path(os.path.expandvars(config_home)) / 'devstack-cli.conf'
        parser = argparse.ArgumentParser(
            fromfile_prefix_chars='@',
            #formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument(
            '-c', '--config-file',
            type=str,
            help='path to a devstack-cli configuration file',
            default=str(default_config_file),
        )
        parser.add_argument(
            '--workspace-url',
            type=str,
            help='the URL of your Cloudomation workspace',
        )
        parser.add_argument(
            '-u', '--user-name',
            type=str,
            help='a user name to authenticate to the Cloudomation workspace',
        )
        parser.add_argument(
            '--maximum-uptime-hours',
            type=int,
            help='the number of hours before an CDE is automatically stopped',
        )
        parser.add_argument(
            '-n', '--cde-name',
            type=str,
            help='the name of the CDE',
        )
        parser.add_argument(
            '-s', '--start',
            action='store_true',
            help='start CDE',
        )
        parser.add_argument(
            '--stop',
            action='store_true',
            help='stop CDE',
        )
        parser.add_argument(
            '-w', '--wait-running',
            action='store_true',
            help='wait until CDE is running. implies "--start".',
        )
        parser.add_argument(
            '-o', '--connect',
            action='store_true',
            help='connect to CDE. implies "--start" and "--wait-running".',
        )
        parser.add_argument(
            '-p', '--port-forwarding',
            action='store_true',
            help='enable port-forwarding. implies "--start", "--wait-running", and "--connect".',
        )
        parser.add_argument(
            '-f ', '--file-sync',
            action='store_true',
            help='enable file-sync implies "--start", "--wait-running", and "--connect".',
        )
        parser.add_argument(
            '-l', '--logs',
            action='store_true',
            help='enable following logs implies "--start", "--wait-running", and "--connect".',
        )
        parser.add_argument(
            '-t', '--terminal',
            action='store_true',
            help='open interactive terminal implies "--start", "--wait-running", and "--connect".',
        )
        parser.add_argument(
            '-q', '--quit',
            action='store_true',
            help='exit after processing command line arguments.',
        )

        # parser.add_argument(
        #     '-s', '--source-directory',
        #     type=str,
        #     help='a local directory where the sources of the CDE will be stored',
        # )
        # parser.add_argument(
        #     '-o', '--output-directory',
        #     type=str,
        #     help='a local directory where the outputs of the CDE will be stored',
        # )
        # parser.add_argument(
        #     '--remote-source-directory',
        #     type=str,
        #     help='a remote directory where the sources of the CDE are stored',
        # )
        # parser.add_argument(
        #     '--remote-output-directory',
        #     type=str,
        #     help='a remote directory where the outputs of the CDE are stored',
        # )
        # parser.add_argument(
        #     '--remote-username',
        #     type=str,
        #     help='the username on the CDE',
        # )
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='enable debug logging',
        )
        parser.add_argument(
            '-V', '--version',
            action='version',
            version=f'Cloudomation devstack-cli {version.MAJOR}+{version.BRANCH_NAME}.{version.BUILD_DATE}.{version.SHORT_SHA}',
        )
        self.args = parser.parse_args()

        if self.args.port_forwarding:
            self.args.connect = True
        if self.args.file_sync:
            self.args.connect = True
        if self.args.logs:
            self.args.connect = True
        if self.args.terminal:
            self.args.connect = True
        if self.args.connect:
            self.args.wait_running = True
        if self.args.wait_running:
            self.args.start = True

        if self.args.verbose:
            logger.setLevel(logging.DEBUG)
            json_logger.setLevel(logging.DEBUG)
            asyncssh.set_log_level(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
            json_logger.setLevel(logging.INFO)
            asyncssh.set_log_level(logging.WARNING)

    @contextlib.asynccontextmanager
    async def _key_press_to_queue(self: 'Cli'):
        self._fd = sys.stdin.fileno()
        self._tcattr = termios.tcgetattr(self._fd)
        tty.setcbreak(self._fd)
        def on_stdin() -> None:
            self.loop.call_soon_threadsafe(self.key_queue.put_nowait, sys.stdin.buffer.raw.read(1).decode())
        self.loop.add_reader(sys.stdin, on_stdin)
        try:
            yield
        finally:
            self.loop.remove_reader(sys.stdin)
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._tcattr)

    async def _load_global_config(self: 'Cli') -> None:
        self.config_file = pathlib.Path(os.path.expandvars(self.args.config_file))
        self.config_file.parent.mkdir(parents=True, exist_ok=True)  # make sure the config directory exists
        self.config = configparser.ConfigParser()
        if not self.config_file.exists():
            logger.info('No configuration file exists at "%s". Creating a new configuration.', self.config_file)
        else:
            logger.info('Loading configuration from %s', self.config_file)
            async with aiofiles.open(self.config_file, mode='r') as f:
                config_str = await f.read()
            self.config.read_string(config_str, source=self.config_file)
        self.config.setdefault('global', {})

        workspace_url = self.args.workspace_url or self.config['global'].get('workspace_url')
        if not workspace_url:
            workspace_url = self._console_input('Enter the URL of your Cloudomation workspace: ', prefill='https://')
        self.config['global']['workspace_url'] = workspace_url
        self.workspace_url = yarl.URL(workspace_url)

        user_name = self.args.user_name or self.config['global'].get('user_name')
        if not user_name:
            user_name = self._console_input(f'Enter your user-name to authenticate to {workspace_url}: ')
        self.config['global']['user_name'] = user_name

        self.password = os.environ.get('DEVSTACK_CLI_PASSWORD')
        if not self.password:
            self.password = self._console_input(f'Enter your password to authenticate "{user_name}" to {workspace_url}: ', password=True)
        self.twofa_code = self._console_input('Enter a current two-factor authentication code (if enabled): ', password=True)

        maximum_uptime_hours = self.args.maximum_uptime_hours or self.config['global'].get('maximum_uptime_hours')
        if not maximum_uptime_hours:
            while True:
                maximum_uptime_hours = self._console_input('How many hours should an CDE remain started until it is automatically stopped: ', prefill='8')
                try:
                    int(maximum_uptime_hours)
                except ValueError:
                    logger.error('"%s" is not a valid number', maximum_uptime_hours)  # noqa: TRY400
                else:
                    break
        self.config['global']['maximum_uptime_hours'] = maximum_uptime_hours

        await self._write_config_file()

    async def _write_config_file(self: 'Cli') -> None:
        logger.debug('Writing configuration file %s', self.config_file)
        config_str = io.StringIO()
        self.config.write(config_str)
        async with aiofiles.open(self.config_file, mode='w') as f:
            await f.write(config_str.getvalue())

    def _console_input(self: 'Cli', prompt: str, *, password: bool = False, prefill: str = '') -> str:
        self.loop.remove_reader(sys.stdin)
        termios.tcsetattr(self._fd, termios.TCSADRAIN, self._tcattr)
        readline.set_startup_hook(lambda: readline.insert_text(prefill))
        try:
            response = self.console.input(prompt, password=password)
        finally:
            readline.set_startup_hook()
        tty.setcbreak(self._fd)
        def on_stdin() -> None:
            self.loop.call_soon_threadsafe(self.key_queue.put_nowait, sys.stdin.read(1))
        self.loop.add_reader(sys.stdin, on_stdin)
        return response

    async def _check_config(self: 'Cli') -> None:
        logger.debug('Checking if Cloudomation workspace at %s is alive', self.config['global']['workspace_url'])
        try:
            response = await self.session.get(
                url=self.workspace_url / 'api/latest/alive',
            )
        except aiohttp.client_exceptions.ClientConnectorError  as ex:
            raise InitializationError(f'Failed to verify Cloudomation workspace alive: {ex!s}') from ex
        if response.status != 200:
            raise InitializationError(f'Failed to verify Cloudomation workspace alive: {response.reason} ({response.status}):\n{await response.text()}')
        workspace_info = await response.json()
        logger.info('Connected to Cloudomation workspace %s', self.workspace_url)
        json_logger.debug(json.dumps(workspace_info, indent=4, sort_keys=True))

        logger.debug('Logging in as "%s" to Cloudomation workspace at %s', self.config['global']['user_name'], self.config['global']['workspace_url'])
        response = await self.session.post(
            url=self.workspace_url / 'api/latest/auth/login',
            json={
                'user_name': self.config['global']['user_name'],
                'password': self.password,
                'twofa_code': self.twofa_code,
                'authentication_method': 'cloudomation',
            },
        )
        if response.status != 200:
            raise InitializationError(f'Failed to login to Cloudomation workspace: {response.reason} ({response.status}):\n{await response.text()}')
        self.user_info = await response.json()
        logger.info('Logged in to Cloudomation workspace')
        json_logger.debug(json.dumps(self.user_info, indent=4, sort_keys=True))

        response = await self.session.get(
            url=self.workspace_url / 'api/latest/object_template/cde-type',
            params={
                'by': 'name',
            },
        )
        if response.status != 200:
            raise InitializationError(f'Failed to fetch "cde-type" object template: {response.reason} ({response.status}):\n{await response.text()}\nIs the "DevStack" bundle installed?')
        self.cde_type_template = (await response.json())['object_template']
        logger.debug('The "cde-type" object template')
        json_logger.debug(json.dumps(self.cde_type_template, indent=4, sort_keys=True))

        response = await self.session.get(
            url=self.workspace_url / 'api/latest/object_template/cde',
            params={
                'by': 'name',
            },
        )
        if response.status != 200:
            raise InitializationError(f'Failed to fetch "cde" object template: {response.reason} ({response.status}):\n{await response.text()}\nIs the "DevStack" bundle installed?')
        self.cde_template = (await response.json())['object_template']
        logger.debug('The "cde" object template')
        json_logger.debug(json.dumps(self.cde_template, indent=4, sort_keys=True))

        response = await self.session.get(
            url=self.workspace_url / 'api/latest/custom_object',
            params={
                'filter': json.dumps({
                    'field': 'object_template_id',
                    'op': 'eq',
                    'value': self.cde_type_template['id'],
                }),
                'plain': 'true',
            },
        )
        if response.status != 200:
            raise InitializationError(f'Failed to fetch "cde-type" custom objects: {response.reason} ({response.status}):\n{await response.text()}')
        self.cde_types = await response.json()
        logger.debug('The "cde-type" custom objects')
        json_logger.debug(json.dumps(self.cde_types, indent=4, sort_keys=True))

        # logger.info('Using configuration of CDE "%s"', self.cde_name)
        # json_logger.debug(json.dumps(self.cde_config, indent=4, sort_keys=True))

    async def _print_help(self: 'Cli') -> None:
        await self._update_cde_list()
        await self._check_background_tasks()
        table = rich.table.Table(title='Help')
        table.add_column('Key', style='cyan bold')
        table.add_column('Function')
        table.add_column('Status')

        # global commands
        table.add_row('h, [SPACE]', 'Print [cyan bold]h[/cyan bold]elp and status')
        table.add_row('v', 'Toggle [cyan bold]v[/cyan bold]erbose debug logs', '[green]on' if logger.getEffectiveLevel() == logging.DEBUG else '[red]off')
        table.add_row('q, [ESC]', '[cyan bold]Q[/cyan bold]uit')
        table.add_row('#', 'DEBUG')
        table.add_row('n', 'Create [cyan bold]n[/cyan bold]ew CDE')

        # CDE selection
        if self.cdes:
            table.add_section()
            table.add_row('', '== CDE selection ==')
        for i, cde in enumerate(self.cdes.values(), start=1):
            cde_type = await self._get_cde_type_of_cde(cde)
            if not cde_type:
                continue
            cde_type_name = cde_type['name']
            if self.cde and self.cde['name'] == cde['name']:
                table.add_row(str(i), f"Select \"{cde['name']}\" ({cde_type_name}) CDE", f"[{cde['status_color']}]{cde['status']} [italic default](selected)")
            else:
                table.add_row(str(i), f"Select \"{cde['name']}\" ({cde_type_name}) CDE", f"[{cde['status_color']}]{cde['status']}")

        # CDE operations
        table.add_section()
        table.add_row('', '== CDE operations ==')
        if self.cde:
            table.add_row('w', f'[cyan bold]W[/cyan bold]ait for "{self.cde_name}" CDE to be running')
            if self.cde['status'] == 'running':
                table.add_row('o', f"C[cyan bold]o[/cyan bold]nnect to \"{self.cde['name']}\" CDE")
            elif self.cde['status'] == 'connected':
                table.add_row('o', f"Disc[cyan bold]o[/cyan bold]nnect from \"{self.cde['name']}\" CDE")
            else:
                table.add_row('o', f"Connect to \"{self.cde['name']}\" CDE", 'N/A: CDE is not running', style='bright_black italic')
            table.add_row('c', f"[cyan bold]C[/cyan bold]onfigure \"{self.cde['name']}\" CDE")
            if self.cde['status'] in ('stopped', 'deleted'):
                table.add_row('s', f'[cyan bold]S[/cyan bold]tart "{self.cde_name}" CDE')
            elif self.cde['status'] in ('running', 'connected'):
                table.add_row('s', f'[cyan bold]S[/cyan bold]top "{self.cde_name}" CDE')
            else:
                table.add_row('s', 'Start/stop CDE', 'N/A: CDE is transitioning', style='bright_black italic')
            table.add_row('d', f'[cyan bold]D[/cyan bold]elete "{self.cde_name}" CDE')
        else:
            table.add_row('w', 'Wait for CDE to be running', 'N/A: no CDE selected', style='bright_black italic')
            table.add_row('o', 'Connect to CDE', 'N/A: no CDE selected', style='bright_black italic')
            table.add_row('c', 'Configure CDE', 'N/A: no CDE selected', style='bright_black italic')
            table.add_row('s', 'Start/stop CDE', 'N/A: no CDE selected', style='bright_black italic')
            table.add_row('d', 'Delete CDE', 'N/A: no CDE selected', style='bright_black italic')

        # CDE connection
        table.add_section()
        table.add_row('', '== CDE connection ==')
        if self.cde and self.cde['status'] == 'connected':
            table.add_row('p', 'Toggle [cyan bold]p[/cyan bold]ort forwarding', '[red]off' if self.port_forwarding_task is None else '[green]on')
            table.add_row('f', 'Toggle [cyan bold]f[/cyan bold]ile sync', '[red]off' if self.sync_task is None else '[green]on')
            table.add_row('l', 'Toggle following [cyan bold]l[/cyan bold]ogs', '[red]off' if self.logs_task is None else '[green]on')
            table.add_row('t', 'Open an interactive terminal session on the CDE')
        else:
            table.add_row('p', 'Toggle port forwarding', 'N/A: not connected', style='bright_black italic')
            table.add_row('f', 'Toggle file sync', 'N/A: not connected', style='bright_black italic')
            table.add_row('l', 'Toggle following logs', 'N/A: not connected', style='bright_black italic')
            table.add_row('t', 'Open an interactive terminal session on the CDE', 'N/A: not connected', style='bright_black italic')
        rich.print(table)

    async def _update_cde_list(self: 'Cli') -> None:
        logger.info('Fetching updated CDE list from Cloudomation workspace')
        try:
            response = await self.session.get(
                url=self.workspace_url / 'api/latest/custom_object',
                params={
                    'filter': json.dumps({
                        'and': [
                            {
                                'field': 'object_template_id',
                                'op': 'eq',
                                'value': self.cde_template['id'],
                            },
                            {
                                'field': 'created_by',
                                'op': 'eq',
                                'value': self.user_info['identity_id'],
                            },
                        ],
                    }),
                    'plain': 'true',
                },
            )
        except (aiohttp.ClientError, aiohttp.ClientResponseError) as ex:
            logger.error('Failed to fetch CDE list: %s', str(ex))  # noqa: TRY400
            return
        if response.status != 200:
            logger.error('Failed to fetch CDE list: %s (%s):\n%s', response.reason, response.status, await response.text())
            return
        response = await response.json()
        self.cdes = {
            cde['name']: {
                **cde,
                'exists_remotely': True,
            }
            for cde
            in response
        }
        # combine with CDE infos from local config file
        for cde_config_key, cde_config_value in self.config.items():
            if not cde_config_key.startswith('cde.'):
                continue
            cur_cde_name = cde_config_key[4:]
            self.cdes.setdefault(cur_cde_name, {}).update({
                **cde_config_value,
                'name': cur_cde_name,
                'exists_locally': True,
            })
        # enrich CDE infos with:
        # - combined status: provisioning_state & is-running & exists locally only
        # - exists_locally: cde name present in config file
        # - exists_remotely: remote config exists
        for cde in self.cdes.values():
            cde.setdefault('exists_remotely', False)
            cde.setdefault('exists_locally', False)
            if not cde['exists_locally']:
                cde['status'] = 'not configured'
                cde['status_color'] = 'yellow'
            elif not cde['exists_remotely']:
                cde['status'] = 'deleted'
                cde['status_color'] = 'red'
            elif cde['provisioning_state'] == 'READY':
                if cde['value']['is-running']:
                    if cde['value'].get('hostname'):
                        if self.ssh_client is None or self.cde is None or self.cde['name'] != cde['name']:
                            cde['status'] = 'running'
                            cde['status_color'] = 'green'
                        else:
                            cde['status'] = 'connected'
                            cde['status_color'] = 'green bold'
                    else:
                        cde['status'] = 'starting'
                        cde['status_color'] = 'blue'
                else:
                    cde['status'] = 'stopped'
                    cde['status_color'] = 'red'
            elif cde['provisioning_state'].endswith('_FAILED'):
                cde['status'] = cde['provisioning_state'].lower()
                cde['status_color'] = 'red'
            else:
                cde['status'] = cde['provisioning_state'].lower()
                cde['status_color'] = 'blue'

        logger.debug('Your CDEs')
        json_logger.debug(json.dumps(self.cdes, indent=4, sort_keys=True))

        if self.cde:
            try:
                # update selected cde info from fetched list
                await self._select_cde(self.cde_name, quiet=True)
            except KeyError:
                logger.warning('Selected CDE "%s" does not exist any more. Unselecting.', self.cde_name)
                self.cde = None

    async def _check_background_tasks(self: 'Cli') -> None:
        if self.sync_task is not None and self.sync_task.done():
            self.sync_task = None
        if self.port_forwarding_task is not None and self.port_forwarding_task.done():
            self.port_forwarding_task = None
        if self.logs_task is not None and self.logs_task.done():
            self.logs_task = None
        if self.ssh_client is not None:
            transport = self.ssh_client.get_transport()
            if transport.is_active():
                try:
                    transport.send_ignore()
                except EOFError:
                    # connection is closed
                    logger.warning('SSH connection is not alive, disconnecting.')
                    self.ssh_client.close()
                    self.ssh_client = None
            else:
                logger.warning('SSH connection is not alive, disconnecting.')
                self.ssh_client.close()
                self.ssh_client = None
        if self.ssh_client is None:
            # we are not connected to any cde. make sure background tasks are cancelled
            if self.sync_task:
                self.sync_task.cancel()
                self.sync_task = None
            if self.port_forwarding_task:
                self.port_forwarding_task.cancel()
                self.port_forwarding_task = None
            if self.logs_task:
                self.logs_task.cancel()
                self.logs_task = None
            if self.sftp_client is not None:
                self.sftp_client.close()
                self.sftp_client = None


    async def _get_cde_type_of_cde(self: 'Cli', cde: dict) -> typing.Optional[dict]:
        if cde['exists_remotely']:
            try:
                cde_type = next(cde_type for cde_type in self.cde_types if cde_type['id'] == cde['value']['cde-type'])
            except StopIteration:
                logger.error('CDE type ID "%s" not found', cde['value']['cde-type'])  # noqa: TRY400
                return None
        elif cde['exists_locally']:
            try:
                cde_type = next(cde_type for cde_type in self.cde_types if cde_type['name'] == cde['cde_type'])
            except StopIteration:
                logger.error('CDE type "%s" not found', cde['cde_type'])  # noqa: TRY400
                return None
        else:
            logger.error('CDE does not exist')
            return None
        return cde_type

    async def _process_args(self: 'Cli') -> None:
        if self.args.cde_name:
            await self._select_cde(self.args.cde_name)
        elif 'last_cde_name' in self.config['global']:
            await self._select_cde(self.config['global']['last_cde_name'])

        if self.args.start:
            await self._start_cde()
        elif self.args.stop:
            await self._stop_cde()

        if self.args.wait_running and self.cde['status'] == 'not configured':
            await self._configure_cde()

        if self.args.wait_running and self.cde['status'] != 'running':
            await self._wait_running()

        if self.args.connect:
            await self._connect_cde()

        if self.args.port_forwarding:
            await self._start_port_forwarding()

        if self.args.file_sync:
            await self._start_sync()

        if self.args.logs:
            await self._start_logs()

        if self.args.terminal:
            await self._open_terminal()

        if self.args.quit:
            raise KeyboardInterrupt

    async def _handle_key_press(self: 'Cli', key_press: str) -> None:
        if key_press in ('h', ' '):
            await self._print_help()
        elif key_press == 'v':
            if logger.getEffectiveLevel() == logging.INFO:
                logger.info('Enabling debug logs')
                logger.setLevel(logging.DEBUG)
            else:
                logger.info('Disabling debug logs')
                logger.setLevel(logging.INFO)
        elif key_press == 'q':
            raise asyncio.CancelledError
        elif key_press == '\x1b':  # escape
            await asyncio.sleep(0)  # event loop tick for queue.put_nowait be handled
            if self.key_queue.empty():
                # single escape press
                raise asyncio.CancelledError
            # escape sequence
            seq = ''
            while not self.key_queue.empty():
                seq += await self.key_queue.get()
                await asyncio.sleep(0)  # event loop tick for queue.put_nowait be handled
            logger.warning('Ignoring escape sequence "%s"', seq)
        elif key_press == '#':
            if self.cde:
                logger.info('CDE config')
                json_logger.info(json.dumps(self.cde, indent=4, sort_keys=True))
            if self.cde_type:
                logger.info('CDE type config')
                json_logger.info(json.dumps(self.cde_type, indent=4, sort_keys=True))
        elif key_press == 'n':
            await self._create_cde()
        elif key_press in (str(i) for i in range(1, len(self.cdes)+1)):
            cde_name = list(self.cdes.values())[int(key_press)-1]['name']
            await self._select_cde(cde_name)
        elif key_press == 'w':
            await self._wait_running()
        elif key_press == 'o':
            await self._connect_disconnect_cde()
        elif key_press == 'c':
            await self._configure_cde()
        elif key_press == 's':
            await self._start_stop_cde()
        elif key_press == 'd':
            await self._delete_cde()
        elif key_press == 'p':
            await self._toggle_port_forwarding()
        elif key_press == 'f':
            await self._toggle_sync()
        elif key_press == 'l':
            await self._toggle_logs()
        elif key_press == 't':
            await self._open_terminal()
        elif key_press == '\x0a':  # return
            rich.print('')
        else:
            logger.warning('Unknown keypress "%s" (%d)', key_press if key_press in string.printable else '?', ord(key_press))

    async def _create_cde(self: 'Cli') -> None:
        logger.info('Creating new CDE')
        table = rich.table.Table(title='CDE types')
        table.add_column('Key', style='cyan bold')
        table.add_column('Name')
        table.add_column('Description')
        for i, cde_type in enumerate(self.cde_types, start=1):
            table.add_row(str(i), cde_type['name'], cde_type['description'])
        table.add_row('ESC', 'Cancel')
        rich.print(table)
        logger.info('Choose a CDE type (1-%d):', len(self.cde_types))
        key_press = await self.key_queue.get()
        if key_press == chr(27):
            logger.warning('Aborting')
            return
        try:
            cde_type = self.cde_types[int(key_press)-1]
        except (IndexError, ValueError):
            logger.error('Invalid choice "%s"', key_press)  # noqa: TRY400
            return
        cde_name = self._console_input('Choose a name for your CDE: ', prefill=f"{self.user_info['name']}-{cde_type['name']}")
        await self._create_cde_api_call(cde_name, cde_type['id'])
        await self._update_cde_list()
        await self._select_cde(cde_name)

    async def _create_cde_api_call(self: 'Cli', cde_name: str, cde_type_id: str) -> None:
        maximum_uptime_hours = int(self.config['global'].get('maximum_uptime_hours', '8'))
        stop_at = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=maximum_uptime_hours)).isoformat()
        try:
            response = await self.session.post(
                url=self.workspace_url / 'api/latest/custom_object',
                json={
                    'name': cde_name,
                    'object_template_id': self.cde_template['id'],
                    'value': {
                        'cde-type': cde_type_id,
                        'user': self.user_info['identity_id'],
                        'feature-branch-mapping': None,
                        'stop-at': stop_at,
                    },
                },
                params={
                    'plain': 'true',
                },
            )
        except (aiohttp.ClientError, aiohttp.ClientResponseError) as ex:
            logger.error('Failed to create CDE: %s', str(ex))  # noqa: TRY400
            return
        if response.status != 200:
            logger.error('Failed to create CDE: %s (%s):\n%s', response.reason, response.status, await response.text())
            return

    async def _select_cde(self: 'Cli', cde_name: str, *, quiet: bool = False) -> None:
        if self.cde is not None and self.cde['name'] != cde_name and self.ssh_client is not None:
            await self._disconnect_cde()
        try:
            self.cde = self.cdes[cde_name]
        except IndexError:
            logger.error('Cannot select CDE "%s". No such CDE', cde_name)  # noqa: TRY400
            return
        if not quiet:
            logger.info('Selecting "%s" CDE', self.cde_name)
        self.cde_type = await self._get_cde_type_of_cde(self.cde)
        self.config['global']['last_cde_name'] = self.cde_name
        await self._write_config_file()

    async def _wait_running(self: 'Cli') -> None:
        logger.info('Waiting for CDE "%s" to reach status running...', self.cde_name)
        while True:
            await asyncio.sleep(10)
            await self._update_cde_list()
            if self.cde['status'] == 'running':
                break
            if self.cde['status'].endswith('_failed') or self.cde['status'] in {'not configured', 'deleted', 'connected', 'stopped'}:
                logger.error('CDE "%s" failed to reach status running and is now in status "%s".', self.cde_name, self.cde['status'])
                return
        logger.info('CDE "%s" is now running', self.cde_name)

    async def _connect_disconnect_cde(self: 'Cli') -> None:
        await self._update_cde_list()
        if not self.cde:
            logger.error('No CDE is selected. Cannot connect.')
            return
        if self.cde['status'] == 'running':
            await self._connect_cde()
        elif self.cde['status'] == 'connected':
            await self._disconnect_cde()
        else:
            logger.error('CDE is not running. Cannot connect.')
            return

    async def _connect_cde(self: 'Cli') -> None:
        logger.info('Connecting to CDE')
        known_hosts = await self._get_known_hosts()
        if known_hosts is None:
            logger.error('Cannot connect to CDE. Host-key not found.')
            return
        self.known_hosts_file = await _create_temp_file(exit_stack=self.exit_stack, content=known_hosts)
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_host_keys(self.known_hosts_file.name)
        try:
            self.ssh_client.connect(
                hostname=self.hostname,
                username=self.cde_type['value']['remote-username'],
                timeout=30,
            )
        except TimeoutError:
            logger.error('Timeout while connecting to CDE. Is your CDE running?')  # noqa: TRY400
            self.ssh_client = None
            return
        transport = self.ssh_client.get_transport()
        transport.set_keepalive(30)
        self.sftp_client = paramiko.sftp_client.SFTPClient.from_transport(transport)
        logger.info('Connected to CDE')

    async def _get_known_hosts(self: 'Cli') -> typing.Optional[str]:
        if not self.cde:
            logger.error('No CDE is selected. Cannot fetch host-key.')
            return None
        if not self.is_cde_running:
            logger.error('CDE is not running. Cannot fetch host-key.')
            return None
        if not self.cde['value']['hostkey']:
            logger.error('CDE record does not contain a hostkey.')
            return None
        if self.cde['value']['hostkey'].startswith(self.cde['value']['hostname']):
            return self.cde['value']['hostkey']
        return f"{self.cde['value']['hostname']} {self.cde['value']['hostkey']}"

    async def _disconnect_cde(self: 'Cli') -> None:
        logger.info('Disconnecting from CDE')
        await self._stop_port_forwarding()
        await self._stop_sync()
        await self._stop_logs()
        if self.sftp_client is not None:
            self.sftp_client.close()
            self.sftp_client = None
        if self.ssh_client is not None:
            self.ssh_client.close()
            self.ssh_client = None
        self.known_hosts_file = None
        logger.debug('Disconnected from CDE')

    async def _configure_cde(self: 'Cli') -> None:
        await self._update_cde_list()
        if not self.cde:
            logger.error('No CDE is selected. Cannot configure CDE.')
            return
        cde_config_key = f'cde.{self.cde_name}'
        if cde_config_key not in self.config:
            logger.info('Creating new configuration for CDE "%s".', self.cde_name)
            self.config[cde_config_key] = {
                'cde_type': self.cde_type['name'],
            }
        source_directory = self._console_input(
            f'Choose a local directory where the sources of the "{self.cde_name}" CDE will be stored: ',
            prefill=self.config[cde_config_key].get('source_directory', f'$HOME/{self.cde_type["name"].replace(" ", "-")}'),
        )
        self.config[cde_config_key]['source_directory'] = source_directory
        while True:
            output_directory = self._console_input(
                f'Choose a local directory where the outputs of the "{self.cde_name}" CDE will be stored: ',
                prefill=self.config[cde_config_key].get('output_directory', f'$HOME/{self.cde_type["name"].replace(" ", "-")}-output'),
            )
            if (
                    _is_relative_to(source_directory, output_directory)
                    or _is_relative_to(output_directory, source_directory)
            ):
                logger.error('Source-directory and output-directory must not overlap!')
            else:
                break
        self.config[cde_config_key]['output_directory'] = output_directory
        while True:
            maximum_uptime_hours = self._console_input(
                'How many hours should this CDE remain started until it is automatically stopped: ',
                prefill=self.config['global'].get('maximum_uptime_hours', '8'),
            )
            try:
                int(maximum_uptime_hours)
            except ValueError:
                logger.error('"%s" is not a valid number', maximum_uptime_hours)  # noqa: TRY400
            else:
                break
        self.config[cde_config_key]['maximum_uptime_hours'] = maximum_uptime_hours

        await self._write_config_file()
        logger.info('CDE "%s" configured.', self.cde_name)

    async def _start_stop_cde(self: 'Cli') -> None:
        await self._update_cde_list()
        if not self.cde:
            logger.error('No CDE is selected. Cannot start/stop CDE.')
            return
        if self.cde['status'] in ('stopped', 'deleted'):
            await self._start_cde()
        elif self.cde['status'] in ('running', 'connected'):
            await self._stop_cde()

    async def _start_cde(self: 'Cli') -> None:
        logger.info('Start CDE')
        if not self.cde['exists_remotely']:
            await self._create_cde_api_call(self.cde['name'], self.cde_type['id'])
        else:
            await self._start_cde_api_call()

    async def _stop_cde(self: 'Cli') -> None:
        logger.info('Stop CDE')
        await self._stop_cde_api_call()
        # cde was running, is now stopping
        if self.sync_task:
            self.sync_task.cancel()
            self.sync_task = None
        if self.port_forwarding_task:
            self.port_forwarding_task.cancel()
            self.port_forwarding_task = None
        if self.logs_task:
            self.logs_task.cancel()
            self.logs_task = None
        if self.ssh_client is not None:
            self.ssh_client.close()
            self.ssh_client = None

    async def _start_cde_api_call(self: 'Cli') -> None:
        maximum_uptime_hours = int(self.config['global'].get('maximum_uptime_hours', '8'))
        stop_at = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=maximum_uptime_hours)).isoformat()
        try:
            response = await self.session.patch(
                url=self.workspace_url / 'api/latest/custom_object' / self.cde['id'],
                json={
                    'value': {
                        'is-running': True,
                        'stop-at': stop_at,
                    },
                },
            )
        except (aiohttp.ClientError, aiohttp.ClientResponseError) as ex:
            logger.error('Failed to start CDE: %s', str(ex))  # noqa: TRY400
            return
        if response.status != 200:
            logger.error('Failed to start CDE: %s (%s):\n%s', response.reason, response.status, await response.text())
            return

    async def _stop_cde_api_call(self: 'Cli') -> None:
        try:
            response = await self.session.patch(
                url=self.workspace_url / 'api/latest/custom_object' / self.cde['id'],
                json={
                    'value': {
                        'is-running': False,
                    },
                },
            )
        except (aiohttp.ClientError, aiohttp.ClientResponseError) as ex:
            logger.error('Failed to stop CDE: %s', str(ex))  # noqa: TRY400
            return
        if response.status != 200:
            logger.error('Failed to stop CDE: %s (%s):\n%s', response.reason, response.status, await response.text())
            return

    async def _delete_cde(self: 'Cli') -> None:
        await self._update_cde_list()
        if not self.cde:
            logger.error('No CDE is selected. Cannot delete CDE.')
            return
        logger.info('Deleting CDE "%s"', self.cde_name)
        try:
            response = await self.session.delete(
                url=self.workspace_url / 'api/latest/custom_object' / self.cde['id'],
                params={
                    'permanently': 'true',
                },
            )
        except (aiohttp.ClientError, aiohttp.ClientResponseError) as ex:
            logger.error('Failed to delete CDE: %s', str(ex))  # noqa: TRY400
            return
        if response.status != 204:
            logger.error('Failed to delete CDE: %s (%s)', response.reason, response.status)
            return
        if self.sync_task:
            self.sync_task.cancel()
            self.sync_task = None
        if self.port_forwarding_task:
            self.port_forwarding_task.cancel()
            self.port_forwarding_task = None
        if self.logs_task:
            self.logs_task.cancel()
            self.logs_task = None
        if self.ssh_client is not None:
            self.ssh_client.close()
            self.ssh_client = None

    #####
    ##### PORT FORWARDING
    #####
    async def _toggle_port_forwarding(self: 'Cli') -> None:
        await self._update_cde_list()
        if self.port_forwarding_task is None:
            await self._start_port_forwarding()
        else:
            await self._stop_port_forwarding()

    async def _start_port_forwarding(self: 'Cli') -> None:
        if not self.cde:
            logger.error('No CDE is selected. Cannot start port forwarding.')
            return
        if not self.is_cde_running:
            logger.error('CDE is not running. Cannot start port forwarding.')
            return
        if self.ssh_client is None:
            logger.error('Not connected to CDE. Cannot start port forwarding.')
            return
        self.port_forwarding_task = asyncio.create_task(self._bg_port_forwarding())

    async def _stop_port_forwarding(self: 'Cli') -> None:
        if self.port_forwarding_task is None:
            return
        self.port_forwarding_task.cancel()
        self.port_forwarding_task = None

    async def _bg_port_forwarding(self: 'Cli') -> None:
        remote_username = ensure_valid_username(self.cde_type['value']['remote-username'])
        hostname = ensure_valid_hostname(self.hostname)
        service_ports = self.cde_type['value'].get('service-ports')
        if service_ports is None:
            service_ports = [
                '8443:443',
                5678,
                6678,
                7678,
                8678,
                3000,
                2022,
            ]
        service_ports = [
            (port, port) if isinstance(port, int) else tuple(map(int, port.split(':', 1)))
            for port
            in service_ports
        ]
        for port in service_ports:
            if port[0] < 1 or port[0] > 65535:
                raise ValueError(f'Invalid port: "{port[0]}". Only numbers between 1 and 65535 are allowed.')
            if port[1] < 1 or port[1] > 65535:
                raise ValueError(f'Invalid port: "{port[1]}". Only numbers between 1 and 65535 are allowed.')
        while True:
            logger.info('Starting port forwarding of %s', ', '.join(str(port[0]) for port in service_ports))
            try:
                await run_subprocess(
                    'ssh',
                    [
                        '-o', 'ConnectTimeout=10',
                        '-o', f'UserKnownHostsFile={self.known_hosts_file.name}',
                        '-NT',
                        f'{remote_username}@{hostname}',
                        *itertools.chain.from_iterable([
                            ('-L', f'{port[0]}:localhost:{port[1]}')
                            for port
                            in service_ports
                        ]),

                    ],
                    name='Port forwarding',
                    capture_stdout=False,
                )
            except asyncio.CancelledError:
                logger.info('Port forwarding interrupted')
                raise
            except SubprocessError as ex:
                logger.error('Port forwarding failed:\n%s: %s', type(ex).__name__, str(ex))  # noqa: TRY400
                logger.info('Will retry port forwarding in %s seconds', RETRY_DELAY_SECONDS)
                await asyncio.sleep(RETRY_DELAY_SECONDS)
                await self._check_background_tasks()
            except Exception:
                logger.exception('Port forwarding failed')
                logger.info('Will retry port forwarding in %s seconds', RETRY_DELAY_SECONDS)
                await asyncio.sleep(RETRY_DELAY_SECONDS)
                await self._check_background_tasks()
            else:
                logger.info('Port forwarding done')
                break

    #####
    ##### FILE SYNC
    #####
    async def _toggle_sync(self: 'Cli') -> None:
        await self._update_cde_list()
        if self.sync_task is None:
            await self._start_sync()
        else:
            await self._stop_sync()

    async def _start_sync(self: 'Cli') -> None:
        if not self.cde:
            logger.error('No CDE is selected. Cannot start file sync.')
            return
        if not self.is_cde_running:
            logger.error('CDE is not running. Cannot start file sync.')
            return
        if self.sftp_client is None:
            logger.error('Not connected to CDE. Cannot start file sync.')
            return
        self.sync_task = asyncio.create_task(self._bg_sync())

    async def _stop_sync(self: 'Cli') -> None:
        if self.sync_task is None:
            return
        self.sync_task.cancel()
        self.sync_task = None

    async def _bg_sync(self: 'Cli') -> None:
        while True:
            logger.info('Starting file sync')
            try:
                await self._init_local_cache()
            except OSError as ex:
                logger.error('Failed to initialize local cache: %s', str(ex))  # noqa: TRY400
                return
            filesystem_event_queue = asyncio.Queue()
            filesystem_watch_task = asyncio.create_task(
                self._watch_filesystem(
                    queue=filesystem_event_queue,
                ),
            )
            if self.local_output_directory:
                remote_sync_task = asyncio.create_task(
                    self._remote_sync(),
                )
            else:
                remote_sync_task = None
            background_sync_task = None
            try:
                while True:
                    filesystem_events = []
                    if background_sync_task is not None:
                        background_sync_task.cancel()
                        with contextlib.suppress(asyncio.CancelledError):
                            await background_sync_task
                    background_sync_task = asyncio.create_task(self._background_sync())
                    filesystem_events.append(await filesystem_event_queue.get())
                    logger.debug('first event, debouncing...')
                    # debounce
                    await asyncio.sleep(EVENT_DEBOUNCE_SECONDS)
                    logger.debug('collecting changes')
                    while not filesystem_event_queue.empty():
                        filesystem_events.append(filesystem_event_queue.get_nowait())
                    for event in filesystem_events:
                        logger.debug('non-unique event: %s', event)
                    # remove duplicates
                    events = [
                        event
                        for i, event
                        in enumerate(filesystem_events)
                        if _get_event_significant_path(event) not in (
                            _get_event_significant_path(later_event)
                            for later_event
                            in filesystem_events[i+1:]
                        )
                    ]
                    for i, event in enumerate(events, start=1):
                        logger.debug('unique event [%d/%d]: %s', i, len(events), event)
                        await self._process_sync_event(event)
            except asyncio.CancelledError:
                logger.info('File sync interrupted')
                raise
            except OSError as ex:
                logger.error('File sync failed: %s', str(ex))  # noqa: TRY400
                logger.info('Will retry file sync in %s seconds', RETRY_DELAY_SECONDS)
                await asyncio.sleep(RETRY_DELAY_SECONDS)
                await self._check_background_tasks()
            except Exception:
                logger.exception('File sync failed')
                logger.info('Will retry file sync in %s seconds', RETRY_DELAY_SECONDS)
                await asyncio.sleep(RETRY_DELAY_SECONDS)
                await self._check_background_tasks()
            else:
                logger.info('File sync stopped')
                break
            finally:
                filesystem_watch_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await filesystem_watch_task
                if remote_sync_task is not None:
                    remote_sync_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await remote_sync_task
                if background_sync_task is not None:
                    background_sync_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await background_sync_task

    async def _init_local_cache(self: 'Cli') -> None:
        self.local_source_directory.mkdir(parents=True, exist_ok=True)
        logger.debug('Listing remote items')
        try:
            listing = self.sftp_client.listdir_attr(self.cde_type['value']['remote-source-directory'])
        except FileNotFoundError as ex:
            raise InitializationError(f"Remote source directory {self.cde_type['value']['remote-source-directory']} does not exist") from ex

        logger.info('Processing %d remote items...', len(listing))
        for file_info in rich.progress.track(
                sequence=sorted(
                    listing,
                    key=lambda file_info: file_info.filename.casefold(),
                ),
                description='Processing remote items',
        ):
            logger.info('Processing "%s"', file_info.filename)
            try:
                result = await self._process_remote_item(file_info)
            except SubprocessError as ex:
                logger.error('Processing of remote item failed:\n%s: %s', type(ex).__name__, str(ex))  # noqa: TRY400
            except Exception:
                logger.exception('Processing of remote item failed')
            else:
                logger.info(result)

    async def _process_remote_item(self: 'Cli', file_info: paramiko.sftp_attr.SFTPAttributes) -> str:
        filename = file_info.filename

        if file_info.st_mode & stat.S_IFDIR:
            # check if .git exists
            try:
                git_stat = self.sftp_client.stat(f"{self.cde_type['value']['remote-source-directory']}/{filename}/.git")
            except FileNotFoundError:
                pass
            else:
                if git_stat.st_mode & stat.S_IFDIR:
                    repo_dir = self.local_source_directory / filename
                    if not repo_dir.exists():
                        return await self._process_remote_item_clone(file_info.filename)
                    return f'Repository "{filename}" already exists'
            return await self._process_remote_item_copy_dir(file_info.filename)
        return await self._process_remote_item_copy_file(file_info.filename)

    async def _process_remote_item_copy_dir(self: 'Cli', filename: str) -> str:
        remote_username = ensure_valid_username(self.cde_type['value']['remote-username'])
        hostname = ensure_valid_hostname(self.hostname)
        remote_source_directory = ensure_valid_path(self.cde_type['value']['remote-source-directory'])
        await run_subprocess(
            'rsync',
            [
                '-e', f'ssh -o ConnectTimeout=10 -o UserKnownHostsFile={self.known_hosts_file.name}',
                '--archive',
                '--checksum',
                f'{remote_username}@{hostname}:{remote_source_directory}/{filename}/',
                str(self.local_source_directory / filename),
            ],
            name='Copy remote directory',
        )
        return f'Copied directory "{filename}"'

    async def _process_remote_item_copy_file(self: 'Cli', filename: str) -> str:
        remote_source_directory = ensure_valid_path(self.cde_type['value']['remote-source-directory'])
        await self.loop.run_in_executor(
            executor=None,
            func=functools.partial(
                self.sftp_client.get,
                remotepath=f'{remote_source_directory}/{filename}',
                localpath=str(self.local_source_directory / filename),
            ),
        )
        return f'Copied file "{filename}"'

    async def _process_remote_item_clone(self: 'Cli', filename: str) -> str:
        remote_username = ensure_valid_username(self.cde_type['value']['remote-username'])
        hostname = ensure_valid_hostname(self.hostname)
        remote_source_directory = ensure_valid_path(self.cde_type['value']['remote-source-directory'])
        await run_subprocess(
            'git',
            [
                'clone',
                '-q',
                f'{remote_username}@{hostname}:{remote_source_directory}/{filename}',
            ],
            name='Git clone',
            cwd=self.local_source_directory,
            env={
                'GIT_SSH_COMMAND': f'ssh -o ConnectTimeout=10 -o UserKnownHostsFile={self.known_hosts_file.name}',
            },
        )
        ssh_stdin, ssh_stdout, ssh_stderr = await self.loop.run_in_executor(
            executor=None,
            func=functools.partial(
                self.ssh_client.exec_command,
                shlex.join([
                    'git',
                    '-C',
                    f'{remote_source_directory}/{filename}',
                    'config',
                    '--get',
                    'remote.origin.url',
                ]),
            ),
        )
        upstream = ssh_stdout.readline().strip()
        await run_subprocess(
            'git',
            [
                'remote',
                'set-url',
                'origin',
                upstream,
            ],
            name='Git remote set-url',
            cwd=self.local_source_directory / filename,
            env={
                'GIT_SSH_COMMAND': f'ssh -o ConnectTimeout=10 -o UserKnownHostsFile={self.known_hosts_file.name}',
            },
        )
        return f'Cloned repository "{filename}"'

    async def _background_sync(self: 'Cli') -> None:
        remote_username = ensure_valid_username(self.cde_type['value']['remote-username'])
        hostname = ensure_valid_hostname(self.hostname)
        remote_source_directory = ensure_valid_path(self.cde_type['value']['remote-source-directory'])
        logger.debug('Starting background sync')
        self.local_source_directory.mkdir(parents=True, exist_ok=True)
        with contextlib.suppress(OSError):
            self.sftp_client.mkdir(remote_source_directory)
        file_sync_exclusions = self.cde_type['value'].get('file-sync-exclusions')
        if file_sync_exclusions is None:
            file_sync_exclusions = [
                'build-cache-*',  # TODO: make exclusions configurable
                'dev-tool/config',
                'alembic.ini',
                'cypress/screenshots',
                'cypress/videos',
                'flow_api',
                '.git',
                '__pycache__',
                '.cache',
                'node_modules',
                '.venv',
                'bundle-content',  # until https://app.clickup.com/t/86bxn0exx
                'cloudomation-fe/build',
                'devstack-self-service-portal/vite-cache',
                'devstack-self-service-portal/dist',
                'documentation/generator/generated',
                'version.py',
                'instantclient-basic-linux.x64.zip',
                'msodbcsql.deb',
                'auth/report',
                'cloudomation-fe/.env',
                'cloudomation/tmp_git_task',
                'cloudomation/tmp',
                'cloudomation/notifications',
                'documentation/versioned_docs',
            ]
        try:
            await run_subprocess(
                'rsync',
                [
                    '-e', f'ssh -o ConnectTimeout=10 -o UserKnownHostsFile={self.known_hosts_file.name}',
                    '--archive',
                    '--delete',
                    '--checksum',  # do not compare timestamps. new CDE template will have all timestamps new,
                                   # but we only want to copy if the content is different
                    '--ignore-times',  # we also use this to avoid syncing timestamps on all directories
                    *itertools.chain.from_iterable([
                        ('--exclude', exclusion)
                        for exclusion
                        in file_sync_exclusions
                    ]),
                    '--human-readable',
                    '--verbose',
                    f'{self.local_source_directory}/',
                    f'{remote_username}@{hostname}:{remote_source_directory}',
                ],
                name='Background sync',
                print_to_debug_log=True,
            )
        except asyncio.CancelledError:
            logger.debug('Background sync interrupted')
            raise
        except SubprocessError as ex:
            logger.error('Background sync failed:\n%s: %s', type(ex).__name__, str(ex))  # noqa: TRY400
        except Exception:
            logger.exception('Background sync failed')
        else:
            logger.info('Background sync done')

    async def _reverse_background_sync(self: 'Cli') -> None:
        remote_username = ensure_valid_username(self.cde_type['value']['remote-username'])
        hostname = ensure_valid_hostname(self.hostname)
        remote_output_directory = ensure_valid_path(self.cde_type['value']['remote-output-directory'])
        logger.debug('Starting reverse background sync')
        with contextlib.suppress(OSError):
            self.sftp_client.mkdir(remote_output_directory)
        self.local_output_directory.mkdir(parents=True, exist_ok=True)
        try:
            await run_subprocess(
                'rsync',
                [
                    '-e', f'ssh -o ConnectTimeout=10 -o UserKnownHostsFile={self.known_hosts_file.name}',
                    '--archive',
                    '--exclude', '__pycache__',
                    '--human-readable',
                    f'{remote_username}@{hostname}:{remote_output_directory}/',
                    str(self.local_output_directory),
                ],
                name='Reverse background sync',
            )
        except asyncio.CancelledError:
            logger.debug('Reverse background sync interrupted')
            raise
        except SubprocessError as ex:
            logger.error('Reverse background sync failed:\n%s: %s', type(ex).__name__, str(ex))  # noqa: TRY400
        except Exception:
            logger.exception('Reverse background sync failed')
        else:
            logger.debug('Reverse background sync done')

    async def _watch_filesystem(
            self: 'Cli',
            queue: asyncio.Queue,
    ) -> None:
        handler = FileSystemEventHandlerToQueue(queue, self.loop)
        filesystem_observer = watchdog.observers.Observer()
        filesystem_observer.schedule(
            event_handler=handler,
            path=str(self.local_source_directory),
            recursive=True,
        )
        filesystem_observer.start()
        logger.info('Filesystem watches established')
        try:
            await self.loop.run_in_executor(
                executor=None,
                func=filesystem_observer.join,
            )
        finally:
            filesystem_observer.stop()
            filesystem_observer.join(3)

    async def _remote_sync(self: 'Cli') -> None:
        while True:
            await self._reverse_background_sync()
            await asyncio.sleep(10)

    async def _process_sync_event(self: 'Cli', event: watchdog.events.FileSystemEvent) -> None:
        local_path = pathlib.Path(event.src_path)
        relative_path = local_path.relative_to(self.local_source_directory)
        remote_path = f"{self.cde_type['value']['remote-source-directory']}/{relative_path}"
        if isinstance(event, watchdog.events.DirCreatedEvent):
            await self._remote_directory_create(remote_path)
        elif isinstance(event, watchdog.events.DirDeletedEvent):
            await self._remote_directory_delete(remote_path)
        elif isinstance(event, watchdog.events.FileCreatedEvent):
            await self._remote_file_create(remote_path)
        elif isinstance(event, watchdog.events.FileModifiedEvent):
            stat = local_path.stat()
            times = (stat.st_atime, stat.st_mtime)
            await self._remote_file_copy(event.src_path, remote_path, times)
        elif isinstance(event, watchdog.events.FileDeletedEvent):
            await self._remote_file_delete(remote_path)
        elif isinstance(event, watchdog.events.FileMovedEvent):
            dest_local_path = pathlib.Path(event.dest_path)
            dest_relative_path = dest_local_path.relative_to(self.local_source_directory)
            dest_remote_path = f"{self.cde_type['value']['remote-source-directory']}/{dest_relative_path}"
            stat = dest_local_path.stat()
            times = (stat.st_atime, stat.st_mtime)
            await self._remote_file_move(remote_path, dest_remote_path, times)

    async def _remote_directory_create(self: 'Cli', remote_path: str) -> None:
        logger.info('Create directory: "%s" (remote)', remote_path)
        try:
            self.sftp_client.mkdir(remote_path)
        except OSError:
            logger.exception('-> failed')
            try:
                stat = self.sftp_client.stat(remote_path)
            except FileNotFoundError:
                logger.info('-> remote directory does not exist')
            else:
                logger.info('-> remote directory already exists:\n%s', stat)

    async def _remote_directory_delete(self: 'Cli', remote_path: str) -> None:
        logger.info('Delete directory: "%s" (remote)', remote_path)
        try:
            self.sftp_client.rmdir(remote_path)
        except FileNotFoundError:
            logger.exception('-> remote directory does not exist')
        except OSError:
            logger.exception('-> failed')

    async def _remote_file_create(self: 'Cli', remote_path: str) -> None:
        logger.info('Create file: "%s" (remote)', remote_path)
        self.sftp_client.putfo(io.BytesIO(), remote_path)

    async def _remote_file_copy(self: 'Cli', local_path: str, remote_path: str, times: typing.Tuple[int, int]) -> None:
        logger.info('Copy file: "%s" (local) -> "%s" (remote)', local_path, remote_path)
        self.sftp_client.put(local_path, remote_path)
        self.sftp_client.utime(remote_path, times)

    async def _remote_file_delete(self: 'Cli', remote_path: str) -> None:
        logger.info('Delete file: "%s" (remote)', remote_path)
        try:
            self.sftp_client.remove(remote_path)
        except FileNotFoundError:
            logger.info('-> remote file does not exist')

    async def _remote_file_move(self: 'Cli', remote_path: str, dest_remote_path: str, times: typing.Tuple[int, int]) -> None:
        logger.info('Move file: "%s" (remote) -> "%s" (remote)', remote_path, dest_remote_path)
        self.sftp_client.rename(remote_path, dest_remote_path)
        self.sftp_client.utime(dest_remote_path, times)

    #####
    ##### LOGS
    #####
    async def _toggle_logs(self: 'Cli') -> None:
        await self._update_cde_list()
        if self.logs_task is None:
            await self._start_logs()
        else:
            await self._stop_logs()

    async def _start_logs(self: 'Cli') -> None:
        if not self.cde:
            logger.error('No CDE is selected. Cannot follow logs.')
            return
        if not self.is_cde_running:
            logger.error('CDE is not running. Cannot follow logs.')
            return
        if self.ssh_client is None:
            logger.error('Not connected to CDE. Cannot follow logs.')
            return
        self.logs_task = asyncio.create_task(self._bg_logs())

    async def _stop_logs(self: 'Cli') -> None:
        if self.logs_task is None:
            return
        self.logs_task.cancel()
        self.logs_task = None

    async def _bg_logs(self: 'Cli') -> None:
        while True:
            logger.info('Following logs')
            try:
                async with asyncssh.connect(
                        self.hostname,
                        connect_timeout=10,
                        known_hosts=self.known_hosts_file.name,
                        username=self.cde_type['value']['remote-username'],
                        term_type=os.environ.get('TERM'),
                ) as conn:
                    await conn.run(input='dev.sh logs\n', stdout=sys.stdout, stderr=sys.stderr, recv_eof=False)
            except asyncio.CancelledError:
                logger.info('Following logs interrupted')
                raise
            except Exception:
                logger.exception('Following logs failed')
                logger.info('Will retry following logs in %s seconds', RETRY_DELAY_SECONDS)
                await asyncio.sleep(RETRY_DELAY_SECONDS)
                await self._check_background_tasks()
            else:
                logger.info('Stopped following logs')
                break

    #####
    ##### TERMINAL
    #####
    async def _open_terminal(self: 'Cli') -> None:
        await self._update_cde_list()
        if not self.cde:
            logger.error('No CDE is selected. Cannot open terminal.')
            return
        if not self.is_cde_running:
            logger.error('CDE is not running. Cannot open terminal.')
            return
        if self.ssh_client is None:
            logger.error('Not connected to CDE. Cannot open terminal.')
            return
        while True:
            logger.info('Opening interactive terminal (press CTRL+D or enter "exit" to close)')
            await self._reset_keyboard()
            _fd = sys.stdin.fileno()
            _tcattr = termios.tcgetattr(_fd)
            tty.setcbreak(_fd)
            try:
                terminal_size = shutil.get_terminal_size()
                async with asyncssh.connect(
                        self.hostname,
                        connect_timeout=10,
                        known_hosts=self.known_hosts_file.name,
                        username=self.cde_type['value']['remote-username'],
                        term_type=os.environ.get('TERM'),
                        term_size=(terminal_size.columns, terminal_size.lines),
                ) as conn:
                    try:
                        self.terminal_process = await conn.create_process(
                            stdin=os.dup(sys.stdin.fileno()),
                            stdout=os.dup(sys.stdout.fileno()),
                            stderr=os.dup(sys.stderr.fileno()),
                        )
                        await self.terminal_process.wait()
                    finally:
                        self.terminal_process = None
            except asyncio.CancelledError:
                logger.info('Interactive terminal interrupted')
                raise
            except Exception:
                logger.exception('Interactive terminal failed')
                logger.info('Will retry interactive terminal in %s seconds', RETRY_DELAY_SECONDS)
                await asyncio.sleep(RETRY_DELAY_SECONDS)
                await self._check_background_tasks()
            else:
                logger.info('Interactive terminal closed')
                break
            finally:
                termios.tcsetattr(_fd, termios.TCSADRAIN, _tcattr)
                await self._setup_keyboard()

    async def _setup_keyboard(self: 'Cli') -> None:
        self._fd = sys.stdin.fileno()
        self._tcattr = termios.tcgetattr(self._fd)
        tty.setcbreak(self._fd)
        def on_stdin() -> None:
            self.loop.call_soon_threadsafe(self.key_queue.put_nowait, sys.stdin.read(1))
        self.loop.add_reader(sys.stdin, on_stdin)

    async def _reset_keyboard(self: 'Cli') -> None:
        self.loop.remove_reader(sys.stdin)
        termios.tcsetattr(self._fd, termios.TCSADRAIN, self._tcattr)

def main() -> None:
    cli = Cli()
    signal.signal(signal.SIGINT, functools.partial(sigint_handler, cli=cli))
    with contextlib.suppress(asyncio.CancelledError):
        asyncio.run(cli.run())
    logger.info('Bye!')


if __name__ == '__main__':
    main()
