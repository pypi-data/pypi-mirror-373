import click
import subprocess
import threading
import time
import os
import signal
import sys
# Lazy import to avoid issues when binaries aren't available (e.g., in tests)
def get_binary_path():
    try:
        from ..binaries import get_binary_path as _get_binary_path
        return _get_binary_path()
    except ImportError:
        # Handle case where binaries module isn't available
        raise RuntimeError("hyperfusion binaries module not found")
from ..service.runner import GracefulRunner
from ..service.grpc_service import ExecutorService
from ..service.bus import Bus


def combine_python_udtf_sources(ctx, param, value):
    """Callback to combine CLI args with environment variable for Python UDTF files."""
    # Start with CLI arguments (if any)
    python_files = list(value) if value else []
    
    # If no CLI args provided, check environment variable directly
    if not python_files:
        env_files = os.environ.get('HYPERFUSION_PYTHON_UDTF_FILES')
        if env_files:
            # Split colon-separated paths from env var
            python_files = [p.strip() for p in env_files.split(':') if p.strip()]
    
    return tuple(python_files)


@click.group()
@click.version_option()
def main():
    """hyperfusion: High-performance SQL execution engine with UDTF support."""
    pass


@main.group()
def run():
    """Run hyperfusion services."""
    pass


@run.command()
# Python kernel specific options
@click.option('--python-kernel-port', default=50051, envvar='HYPERFUSION_PYTHON_KERNEL_PORT', help='Port for the Python kernel when started by this command (can also use HYPERFUSION_PYTHON_KERNEL_PORT env var)')
@click.option('--no-python-kernel', is_flag=True, help='Run only the SQL engine (no Python UDTF support)')
@click.option('--log-level', default='INFO', envvar='HYPERFUSION_LOG_LEVEL', help='Python kernel log level (DEBUG, INFO, WARNING, ERROR) (can also use HYPERFUSION_LOG_LEVEL env var)')
@click.option('--python-udtf-files', multiple=True, callback=combine_python_udtf_sources, help='Python files or directories containing UDTF functions to load (can also use HYPERFUSION_PYTHON_UDTF_FILES env var with colon-separated paths)')
# SQL Engine passthrough options (matching main.rs Config struct)
@click.option('--sql-dir', '-s', default='./sql', help='SQL files directory to watch', envvar='HYPERFUSION_SQL_DIR')
@click.option('--pg-host', default='127.0.0.1', help='PostgreSQL wire protocol host', envvar='HYPERFUSION_PG_HOST')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL wire protocol port', envvar='HYPERFUSION_PG_PORT')
@click.option('--api-addr', default='0.0.0.0:8080', help='API server address', envvar='HYPERFUSION_API_ADDR')
@click.option('--ui-addr', default='0.0.0.0:3000', help='UI server address', envvar='HYPERFUSION_UI_ADDR')
@click.option('--serve-ui/--no-serve-ui', default=True, help='Enable/disable embedded web UI', envvar='HYPERFUSION_SERVE_UI')
@click.option('--ui-api-host', default='http://0.0.0.0:8080', help='UI API host URL', envvar='HYPERFUSION_UI_API_HOST')
@click.option('--api-cors-origins', help='API CORS allowed origins', envvar='HYPERFUSION_API_CORS_ORIGINS')
@click.option('--grpc-kernels', default='python_kernel:localhost:50051', help='gRPC kernels configuration for engine to connect to (name:host:port)', envvar='HYPERFUSION_GRPC_KERNELS')
def default(python_kernel_port, no_python_kernel, log_level, python_udtf_files,
           sql_dir, pg_host, pg_port, api_addr, ui_addr,
           serve_ui, ui_api_host, api_cors_origins, grpc_kernels):
    """Run hyperfusion (SQL engine + Python kernel by default)."""
    processes = []
    
    def signal_handler(signum, frame):
        click.echo("\nShutting down hyperfusion...")
        for process in processes:
            if hasattr(process, 'shutdown'):
                process.shutdown()
        sys.exit(0)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start Python kernel first (if enabled)
        if not no_python_kernel:
            click.echo(f"Starting Python kernel on port {python_kernel_port}...")
            
            # Start Python service using existing components
            python_runner = start_python_service(python_kernel_port, log_level, python_udtf_files)
            processes.append(python_runner)
            
            # Give Python service time to start
            time.sleep(2)
            
            # Update grpc_kernels to match the actual Python port if different from default
            if python_kernel_port != 50051:
                grpc_kernels = f"python_kernel:localhost:{python_kernel_port}"
        
        # Start SQL engine (Rust binary)
        click.echo(f"Starting SQL engine...")
        click.echo(f"  API server: {api_addr}")
        click.echo(f"  PostgreSQL: {pg_host}:{pg_port}")
        if serve_ui:
            click.echo(f"  Web UI: {ui_addr}")
        click.echo(f"  gRPC kernels: {grpc_kernels}")
        
        binary_path = get_binary_path()
        
        # Build command with all arguments matching the Rust CLI exactly
        cmd = [str(binary_path)]
        
        # Required arguments
        cmd.extend(['--sql-dir', sql_dir])
        cmd.extend(['--pg-host', pg_host])
        cmd.extend(['--pg-port', str(pg_port)])
        cmd.extend(['--api-addr', api_addr])
        cmd.extend(['--ui-addr', ui_addr])
        
        # Boolean flag - only add if true (no value needed)
        if serve_ui:
            cmd.append('--serve-ui')
        
        cmd.extend(['--grpc-kernels', grpc_kernels])
        
        # Optional arguments
        if ui_api_host:
            cmd.extend(['--ui-api-host', ui_api_host])
        if api_cors_origins:
            cmd.extend(['--api-cors-origins', api_cors_origins])
        
        # Run the Rust binary (this will block)
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        click.echo("\nShutting down hyperfusion...")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error starting SQL engine: {e}", err=True)
        raise click.Abort()
    finally:
        # Clean up any running processes
        for process in processes:
            if hasattr(process, 'shutdown'):
                process.shutdown()


@run.command()
@click.option('--port', default=50051, envvar='HYPERFUSION_PYTHON_KERNEL_PORT', help='gRPC server port (can also use HYPERFUSION_PYTHON_KERNEL_PORT env var)')
@click.option('--log-level', default='INFO', envvar='HYPERFUSION_LOG_LEVEL', help='Log level (DEBUG, INFO, WARNING, ERROR) (can also use HYPERFUSION_LOG_LEVEL env var)')
@click.option('--python-udtf-files', multiple=True, callback=combine_python_udtf_sources, help='Python files or directories containing UDTF functions to load (can also use HYPERFUSION_PYTHON_UDTF_FILES env var with colon-separated paths)')
def python_kernel(port, log_level, python_udtf_files):
    """Run only the Python UDTF kernel (for development/testing)."""
    click.echo(f"Starting Python kernel on port {port}...")
    
    # Start Python service directly
    runner = start_python_service(port, log_level, python_udtf_files)
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\nShutting down Python kernel...")
        runner.shutdown()


def start_python_service(port: int, log_level: str, python_udtf_files: tuple = ()):
    """Start the Python gRPC service using existing components."""
    import asyncio
    import logging
    
    # Configure logging
    logging.basicConfig(level=getattr(logging, log_level.upper()))
    logger = logging.getLogger(__name__)
    
    # Load UDTF files before starting the service
    from ..service.udtf_loader import load_udtf_files
    
    # python_udtf_files already contains combined CLI args and env var from callback
    successful_modules, error_messages = load_udtf_files(list(python_udtf_files) if python_udtf_files else None)
    
    if error_messages:
        for error_msg in error_messages:
            click.echo(f"UDTF Error: {error_msg}", err=True)
        if not successful_modules:
            click.echo("Failed to load any UDTF files, continuing without UDTFs...", err=True)
    
    if successful_modules:
        click.echo(f"Loaded {len(successful_modules)} UDTF modules")
    
    # Create service components (reuse existing architecture)
    bus = Bus()
    executor_service = ExecutorService(bus)
    
    # Create MainService to handle function execution (this was missing!)
    from ..service.main_service import MainService
    from ..udtf.registry import registry
    main_service = MainService(
        bus=bus,
        logger=logger,
        grpc_service=executor_service,
        registry=registry
    )
    
    # Create and start the runner
    runner = GracefulRunner(logger)
    
    # Start the service in a separate thread
    def run_service():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def start_async_server():
            # Configure the async gRPC server with existing logic
            import grpc
            from ..service.hyperfusion_pb2_grpc import add_ExecutionServiceServicer_to_server
            
            server = grpc.aio.server()
            add_ExecutionServiceServicer_to_server(executor_service, server)
            server.add_insecure_port(f'[::]:{port}')
            await server.start()
            
            try:
                await server.wait_for_termination()
            finally:
                await server.stop(grace=5)
        
        try:
            loop.run_until_complete(start_async_server())
        finally:
            loop.close()
    
    service_thread = threading.Thread(target=run_service, daemon=True)
    service_thread.start()
    
    return runner


# For simplicity, make 'default' the main run command
# Users will use 'hyperfusion run default' or 'hyperfusion run python-kernel'


@main.command()
def version():
    """Show version information for all components."""
    click.echo(f"hyperfusion Package: {get_package_version()}")
    
    # Show Rust binary version
    try:
        binary_path = get_binary_path()
        result = subprocess.run([str(binary_path), '--version'], 
                              capture_output=True, text=True, check=True)
        click.echo(f"SQL Engine: {result.stdout.strip()}")
    except Exception as e:
        # Be more generic to catch any error and continue gracefully
        click.echo(f"SQL Engine: Version unavailable (binary not found or not accessible)")
    
    click.echo("Python Kernel: Available")


def get_package_version():
    """Get the package version."""
    try:
        from .._version import __version__
        return __version__
    except ImportError:
        return "Unknown"


if __name__ == '__main__':
    main()