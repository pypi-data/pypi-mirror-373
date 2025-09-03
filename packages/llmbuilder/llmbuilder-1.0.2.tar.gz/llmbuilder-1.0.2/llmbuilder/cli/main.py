"""
Main CLI entry point for LLMBuilder.

This module defines the main command group and coordinates all subcommands.
"""

import click
from pathlib import Path
from typing import Optional

from llmbuilder import __version__
from llmbuilder.utils.logging import setup_logging
from llmbuilder.utils.config import ConfigManager
from llmbuilder.utils.colors import ColorFormatter, Color, print_header, print_info
from llmbuilder.utils.progress import spinner


@click.group()
@click.version_option(version=__version__, prog_name="llmbuilder")
@click.option(
    "--config", 
    "-c", 
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path"
)
@click.option(
    "--verbose", 
    "-v", 
    is_flag=True, 
    help="Enable verbose output"
)
@click.option(
    "--quiet", 
    "-q", 
    is_flag=True, 
    help="Suppress non-essential output"
)
@click.option(
    "--no-color",
    is_flag=True,
    help="Disable colored output"
)
@click.pass_context
def cli(ctx: click.Context, config: Optional[Path], verbose: bool, quiet: bool, no_color: bool):
    """
    LLMBuilder - Complete LLM Training and Deployment Pipeline
    
    A comprehensive toolkit for training, fine-tuning, and deploying Large Language Models.
    Supports the complete ML lifecycle from data preparation to production deployment.
    
    Examples:
        llmbuilder init my-project          # Create new project
        llmbuilder data prepare             # Process training data
        llmbuilder train start              # Start model training
        llmbuilder serve start              # Deploy model API
    
    For detailed help on any command, use: llmbuilder COMMAND --help
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Store global options in context
    ctx.obj['config_path'] = config
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet
    ctx.obj['no_color'] = no_color
    
    # Disable colors if requested
    if no_color:
        ctx.color = False
    
    # Setup logging based on verbosity
    if quiet:
        log_level = "WARNING"
    elif verbose:
        log_level = "DEBUG"
    else:
        log_level = "INFO"
    
    setup_logging(level=log_level)
    
    # Load configuration with progress indication
    if not quiet:
        with spinner("Loading configuration", color=Color.BLUE):
            config_manager = ConfigManager()
            if config:
                ctx.obj['config'] = config_manager.load_config(config)
            else:
                ctx.obj['config'] = config_manager.get_default_config()
    else:
        config_manager = ConfigManager()
        if config:
            ctx.obj['config'] = config_manager.load_config(config)
        else:
            ctx.obj['config'] = config_manager.get_default_config()


# Import and register subcommands
from llmbuilder.cli.init import init
from llmbuilder.cli.config import config
from llmbuilder.cli.data import data
from llmbuilder.cli.model import model
from llmbuilder.cli.train import train
from llmbuilder.cli.eval import eval
from llmbuilder.cli.optimize import optimize
from llmbuilder.cli.inference import inference
from llmbuilder.cli.deploy import deploy
from llmbuilder.cli.monitor import monitor
from llmbuilder.cli.vocab import vocab
from llmbuilder.cli.tools import tools
from llmbuilder.cli.help import help
from llmbuilder.cli.upgrade import upgrade
from llmbuilder.cli.migrate import migrate
from llmbuilder.cli.pipeline import pipeline

# Setup enhanced error handling
from llmbuilder.utils.error_handler import setup_error_handler
setup_error_handler()

# Register subcommands in logical order
# Core project management
cli.add_command(init)
cli.add_command(config)
cli.add_command(migrate)

# Data and model management
cli.add_command(data)
cli.add_command(model)
cli.add_command(vocab)

# Training and evaluation
cli.add_command(train)
cli.add_command(eval)
cli.add_command(optimize)

# Inference and deployment
cli.add_command(inference)
cli.add_command(deploy)

# Pipeline execution
cli.add_command(pipeline)

# Monitoring and tools
cli.add_command(monitor)
cli.add_command(tools)

# Help and maintenance
cli.add_command(help)
cli.add_command(upgrade)


# Add additional help commands at the top level
@cli.command()
def docs():
    """Show interactive documentation."""
    from llmbuilder.cli.help import HelpSystem
    help_system = HelpSystem()
    help_system.show_interactive_help()


@cli.command()
def examples():
    """Show usage examples."""
    from llmbuilder.cli.help import HelpSystem
    help_system = HelpSystem()
    help_system.show_usage_examples()


@cli.command()
def discover():
    """Discover commands by category."""
    from llmbuilder.cli.help import HelpSystem
    help_system = HelpSystem()
    help_system.show_command_discovery()


@cli.command()
def status():
    """Show system status and health information."""
    from llmbuilder.utils.status import show_system_status
    show_system_status()


@cli.command()
@click.option('--interactive', '-i', is_flag=True, help='Interactive dashboard mode')
def dashboard(interactive: bool):
    """Show interactive dashboard with system metrics."""
    if interactive:
        from llmbuilder.utils.status import show_training_dashboard
        print_info("Starting interactive dashboard (Press Ctrl+C to exit)")
        show_training_dashboard({"session_id": "demo", "model_name": "demo", "status": "idle"})
    else:
        from llmbuilder.utils.status import show_system_status
        show_system_status()


if __name__ == "__main__":
    cli()