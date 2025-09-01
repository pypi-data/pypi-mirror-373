#!/usr/bin/env python3
"""
EvoSphere Server Command

Standalone server launcher for EvoSphere API.
Provides web interface access to all patent innovations.

Authors: Krishna Bajpai and Vedanshi Gupta
"""

import sys
import click
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from evosphere.api.server import start_server
except ImportError as e:
    print(f"Error: Could not import EvoSphere server: {e}")
    print("Please ensure EvoSphere is properly installed with server dependencies:")
    print("pip install 'evosphere[server]'")
    sys.exit(1)

@click.command()
@click.option('--host', default='localhost', help='Server host address')
@click.option('--port', default=8000, type=int, help='Server port number')
@click.option('--enable-all', is_flag=True, help='Enable all patent components')
@click.option('--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']), help='Logging level')
@click.option('--workers', default=1, type=int, help='Number of worker processes')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
def main(host, port, enable_all, log_level, workers, reload):
    """
    EvoSphere API Server
    
    Launch the EvoSphere REST API server for web-based access to all
    six patent-pending innovations: HQESE, MRAEG, EvoByte, SEPD, EDAL, CECE.
    
    Examples:
        # Start basic server
        evosphere-server
        
        # Start with all components enabled
        evosphere-server --enable-all
        
        # Start on custom host/port
        evosphere-server --host 0.0.0.0 --port 8080
        
        # Development mode with auto-reload
        evosphere-server --reload --log-level DEBUG
    """
    
    click.echo("🚀 EvoSphere API Server")
    click.echo("=" * 40)
    click.echo(f"Host: {host}")
    click.echo(f"Port: {port}")
    click.echo(f"Workers: {workers}")
    click.echo(f"Log Level: {log_level}")
    click.echo(f"All Components: {'Enabled' if enable_all else 'On Demand'}")
    click.echo(f"Reload: {'Enabled' if reload else 'Disabled'}")
    click.echo("=" * 40)
    
    if enable_all:
        click.echo("🧬 Initializing all patent components...")
        click.echo("   ⚛️  HQESE - Quantum Evolution Engine")
        click.echo("   🕸️  MRAEG - Adaptive Graph Networks")
        click.echo("   🔧 EvoByte - Bio-Compiler System")
        click.echo("   🧭 SEPD - Pathway Designer")
        click.echo("   📡 EDAL - Data Assimilation Layer")
        click.echo("   🔗 CECE - Cross-Scale Coupling Engine")
    
    click.echo(f"\n🌐 Starting server at http://{host}:{port}")
    click.echo(f"📚 API docs available at http://{host}:{port}/docs")
    click.echo(f"📖 ReDoc available at http://{host}:{port}/redoc")
    click.echo("\n💡 Press Ctrl+C to stop the server")
    
    try:
        if workers > 1:
            # Multi-worker setup (requires gunicorn)
            try:
                import gunicorn.app.wsgiapp as wsgi
                
                sys.argv = [
                    'gunicorn',
                    '--bind', f'{host}:{port}',
                    '--workers', str(workers),
                    '--worker-class', 'uvicorn.workers.UvicornWorker',
                    '--log-level', log_level.lower(),
                    'evosphere.api.server:create_app()'
                ]
                
                wsgi.run()
            
            except ImportError:
                click.echo("⚠️  Gunicorn not available. Running single worker...")
                start_server(host=host, port=port, enable_all=enable_all, log_level=log_level)
        
        else:
            # Single worker with uvicorn
            import uvicorn
            from evosphere.api.server import create_app
            
            app = create_app(enable_all_components=enable_all)
            
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level=log_level.lower(),
                reload=reload
            )
    
    except KeyboardInterrupt:
        click.echo("\n👋 EvoSphere server stopped")
    
    except Exception as e:
        click.echo(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
