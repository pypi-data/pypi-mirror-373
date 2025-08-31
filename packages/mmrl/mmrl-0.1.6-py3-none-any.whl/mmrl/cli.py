import os
import subprocess
import argparse
import tempfile
from pathlib import Path

import yaml
from config.schema import AppConfig
from experiments.run_inventory_mm import run_backtest


def _resolve_config_path(config: str) -> str:
    p = Path(config)
    if p.exists():
        return str(p)
    # Fallback: generate a default config file in a temp dir
    cfg = AppConfig()
    temp_dir = Path(tempfile.mkdtemp(prefix="mmrl_cfg_"))
    out = temp_dir / "inventory.yaml"
    with open(out, "w") as f:
        yaml.safe_dump(cfg.model_dump(), f, sort_keys=False)
    return str(out)


def backtest(config="configs/inventory.yaml"):
    """Run a single backtest using the given config."""
    cfg_path = _resolve_config_path(config)
    with open(cfg_path, 'r') as f:
        cfg = yaml.safe_load(f)
    run_backtest(cfg)


def grid(config="configs/inventory.yaml"):
    """Run a grid search using the given config."""
    env = os.environ.copy()
    env["MMRL_CONFIG"] = _resolve_config_path(config)
    subprocess.run(["python3", "experiments/grid_search_inventory_mm.py"], check=True, env=env)


def train(config="configs/inventory.yaml"):
    """Train PPO on the market making env."""
    env = os.environ.copy()
    env["MMRL_CONFIG"] = _resolve_config_path(config)
    subprocess.run(["python3", "experiments/train_ppo.py"], check=True, env=env)


def evaluate(config="configs/inventory.yaml"):
    """Evaluate rule-based vs PPO and log to MLflow."""
    env = os.environ.copy()
    env["MMRL_CONFIG"] = _resolve_config_path(config)
    subprocess.run(["python3", "experiments/evaluate_agents.py"], check=True, env=env)


def analyze(returns_file, risk_free_rate=0.02, periods_per_year=252, output_file=None, plot=False):
    """Analyze strategy performance using comprehensive metrics."""
    try:
        import pandas as pd
        import numpy as np
        from utils.metrics import calculate_all_metrics, print_metrics_summary, calculate_rolling_metrics
        
        # Load returns data
        print(f"Loading returns from: {returns_file}")
        df = pd.read_csv(returns_file)
        
        # Try to identify returns column
        returns_col = None
        for col in ['returns', 'return', 'pnl', 'profit_loss', 'daily_return']:
            if col in df.columns:
                returns_col = col
                break
        
        if returns_col is None:
            # Use first numeric column
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                returns_col = numeric_cols[0]
                print(f"Using column '{returns_col}' as returns")
            else:
                print("Error: No numeric columns found in the file")
                return
        
        returns = df[returns_col].values
        
        # Remove any NaN values
        returns = returns[~np.isnan(returns)]
        
        if len(returns) == 0:
            print("Error: No valid returns data found")
            return
        
        print(f"Analyzing {len(returns)} periods of returns data...")
        
        # Calculate all metrics
        metrics = calculate_all_metrics(
            returns=returns,
            risk_free_rate=risk_free_rate,
            periods_per_year=periods_per_year
        )
        
        # Print summary
        print_metrics_summary(metrics)
        
        # Save to file if requested
        if output_file:
            metrics_df = pd.DataFrame([metrics])
            metrics_df.to_csv(output_file, index=False)
            print(f"\nMetrics saved to: {output_file}")
        
        # Generate plots if requested
        if plot:
            try:
                import matplotlib.pyplot as plt
                
                # Create performance plots
                fig, axes = plt.subplots(2, 2, figsize=(15, 10))
                fig.suptitle('Strategy Performance Analysis', fontsize=16)
                
                # 1. Equity Curve
                equity_curve = np.cumprod(1 + returns)
                axes[0, 0].plot(equity_curve, linewidth=2)
                axes[0, 0].set_title('Equity Curve')
                axes[0, 0].set_xlabel('Period')
                axes[0, 0].set_ylabel('Portfolio Value')
                axes[0, 0].grid(True, alpha=0.3)
                
                # 2. Returns Distribution
                axes[0, 1].hist(returns, bins=50, alpha=0.7, edgecolor='black')
                axes[0, 1].axvline(returns.mean(), color='red', linestyle='--', 
                                   label=f'Mean: {returns.mean():.4f}')
                axes[0, 1].set_title('Returns Distribution')
                axes[0, 1].set_xlabel('Return')
                axes[0, 1].set_ylabel('Frequency')
                axes[0, 1].grid(True, alpha=0.3)
                axes[0, 1].legend()
                
                # 3. Rolling Sharpe Ratio
                rolling_metrics = calculate_rolling_metrics(returns, window=min(60, len(returns)//4))
                if len(rolling_metrics) > 0:
                    axes[1, 0].plot(rolling_metrics.index, rolling_metrics['rolling_sharpe'], 
                                    linewidth=2, label='Rolling Sharpe')
                    axes[1, 0].axhline(y=0, color='black', linestyle='-', alpha=0.3)
                    axes[1, 0].axhline(y=1, color='green', linestyle='--', alpha=0.5, label='Sharpe = 1')
                    axes[1, 0].set_title('Rolling Sharpe Ratio')
                    axes[1, 0].set_xlabel('Period')
                    axes[1, 0].set_ylabel('Sharpe Ratio')
                    axes[1, 0].grid(True, alpha=0.3)
                    axes[1, 0].legend()
                
                # 4. Rolling Volatility
                if len(rolling_metrics) > 0:
                    axes[1, 1].plot(rolling_metrics.index, rolling_metrics['rolling_volatility'], 
                                    linewidth=2, color='orange', label='Rolling Volatility')
                    axes[1, 1].set_title('Rolling Volatility')
                    axes[1, 1].set_xlabel('Period')
                    axes[1, 1].set_ylabel('Annualized Volatility')
                    axes[1, 1].grid(True, alpha=0.3)
                    axes[1, 1].legend()
                
                plt.tight_layout()
                plt.show()
                
            except ImportError:
                print("Warning: matplotlib not available for plotting")
    except Exception as e:
        print(f"Error during analysis: {e}")


def report(run_dir_or_csv: str, output_html: str = 'report.html') -> None:
    """Generate a simple HTML report from a run_dir or CSV path."""
    import pandas as pd
    from pathlib import Path
    from utils.metrics import calculate_all_metrics
    p = Path(run_dir_or_csv)
    if p.is_dir():
        csv = p / 'inventory_mm_run.csv'
    else:
        csv = p
    df = pd.read_csv(csv)
    returns = df['pnl'].diff().fillna(0.0).values
    metrics = calculate_all_metrics(returns)
    html = f"""
    <html><head><title>MMRL Report</title></head><body>
    <h1>MMRL Report</h1>
    <p>Source: {csv}</p>
    <h2>Metrics</h2>
    <pre>{metrics}</pre>
    </body></html>
    """
    Path(output_html).write_text(html)
    print(f"Report saved to {output_html}")


def main():
    parser = argparse.ArgumentParser(description="Market Making RL CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Backtest command
    backtest_parser = subparsers.add_parser('backtest', help='Run a single backtest')
    backtest_parser.add_argument('--config', default='configs/inventory.yaml', help='Path to YAML config')
    
    # Grid command
    grid_parser = subparsers.add_parser('grid', help='Run a grid search')
    grid_parser.add_argument('--config', default='configs/inventory.yaml', help='Path to YAML config')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train PPO on the market making env')
    train_parser.add_argument('--config', default='configs/inventory.yaml', help='Path to YAML config')
    
    # Evaluate command
    evaluate_parser = subparsers.add_parser('evaluate', help='Evaluate rule-based vs PPO and log to MLflow')
    evaluate_parser.add_argument('--config', default='configs/inventory.yaml', help='Path to YAML config')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze strategy performance using comprehensive metrics')
    analyze_parser.add_argument('returns_file', help='Path to CSV file with returns data')
    analyze_parser.add_argument('--risk-free-rate', type=float, default=0.02, help='Annual risk-free rate (default: 0.02)')
    analyze_parser.add_argument('--periods-per-year', type=int, default=252, help='Number of periods per year (default: 252 for daily)')
    analyze_parser.add_argument('--output-file', help='Output file for metrics (optional)')
    analyze_parser.add_argument('--plot', action='store_true', help='Generate performance plots')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate an HTML report from a run_dir or CSV')
    report_parser.add_argument('source', help='Path to run_dir or CSV file')
    report_parser.add_argument('--out', default='report.html', help='Output HTML path')

    # Data fetch command
    fetch_parser = subparsers.add_parser('fetch-data', help='Fetch sample trades via CCXT and save to Parquet')
    fetch_parser.add_argument('--exchange', default='binance', help='Exchange id (ccxt)')
    fetch_parser.add_argument('--symbol', default='BTC/USDT', help='Symbol to fetch')
    fetch_parser.add_argument('--limit', type=int, default=1000, help='Number of trades to fetch')
    fetch_parser.add_argument('--out', default='data/trades.parquet', help='Output Parquet path')
    fetch_parser.add_argument('--since', type=int, default=None, help='Timestamp (ms) to start fetching from')
    fetch_parser.add_argument('--max-pages', type=int, default=10, help='Max pagination pages')

    # Stream command
    stream_parser = subparsers.add_parser('stream', help='Run a data adapter stream with a chosen agent')
    stream_parser.add_argument('--adapter', required=True, help="Dotted path 'module:Class'")
    stream_parser.add_argument('--agent', default='inventory', help='Agent name (inventory, naive, avellaneda, meanrev, momentum)')
    stream_parser.add_argument('--out', default='results/stream_run', help='Output directory')
    stream_parser.add_argument('--adapter-kv', nargs='*', help='Adapter params as key=value')

    # Pipeline command
    pipeline_parser = subparsers.add_parser('pipeline', help='End-to-end: fetch/stream → backtest → report')
    pipeline_parser.add_argument('--adapter', help="Dotted 'module:Class' (omit to use synthetic backtest)")
    pipeline_parser.add_argument('--agent', default='inventory', help='Agent for stream/backtest')
    pipeline_parser.add_argument('--out', default='results/pipeline_run', help='Output directory')
    pipeline_parser.add_argument('--adapter-kv', nargs='*', help='Adapter params as key=value')
    pipeline_parser.add_argument('--report', action='store_true', help='Generate HTML report at the end')

    # Config validate/schema commands
    subparsers.add_parser('config-validate', help='Validate current config file against schema')
    schema_parser = subparsers.add_parser('config-schema', help='Print JSON schema for configuration')
    
    args = parser.parse_args()
    
    if args.command == 'backtest':
        backtest(args.config)
    elif args.command == 'grid':
        grid(args.config)
    elif args.command == 'train':
        train(args.config)
    elif args.command == 'evaluate':
        evaluate(args.config)
    elif args.command == 'analyze':
        analyze(args.returns_file, args.risk_free_rate, args.periods_per_year, args.output_file, args.plot)
    elif args.command == 'report':
        report(args.source, args.out)
    elif args.command == 'fetch-data':
        from adapters.ccxt_loader import fetch_trades_to_parquet
        out = fetch_trades_to_parquet(args.exchange, args.symbol, args.limit, args.out, args.since, args.max_pages)
        print(f"Saved to {out}")
    elif args.command == 'config-validate':
        from config.schema import load_config as load_cfg_model
        cfg_path = os.environ.get('MMRL_CONFIG', 'configs/inventory.yaml')
        _ = load_cfg_model(cfg_path)
        print(f"Config '{cfg_path}' is valid ✅")
    elif args.command == 'config-schema':
        import json
        from config.schema import export_json_schema
        print(json.dumps(export_json_schema(), indent=2))
    elif args.command == 'stream':
        from mmrl.data import load_adapter
        from mmrl.stream.runner import run_stream
        # Load base config
        cfg_path = os.environ.get('MMRL_CONFIG', _resolve_config_path('configs/inventory.yaml'))
        with open(cfg_path, 'r') as f:
            cfg = yaml.safe_load(f)
        # Parse adapter params
        params = {}
        if args.adapter_kv:
            for kv in args.adapter_kv:
                if '=' in kv:
                    k, v = kv.split('=', 1)
                    params[k] = v
        adapter = load_adapter(args.adapter, **params)
        res = run_stream(adapter, args.agent, cfg, Path(args.out))
        print(f"Stream completed -> {res.run_dir}")
        print(res.metrics)
    elif args.command == 'pipeline':
        # Load base config
        cfg_path = os.environ.get('MMRL_CONFIG', _resolve_config_path('configs/inventory.yaml'))
        with open(cfg_path, 'r') as f:
            cfg = yaml.safe_load(f)
        run_dir = None
        if args.adapter:
            from mmrl.data import load_adapter
            from mmrl.stream.runner import run_stream
            params = {}
            if args.adapter_kv:
                for kv in args.adapter_kv:
                    if '=' in kv:
                        k, v = kv.split('=', 1)
                        params[k] = v
            adapter = load_adapter(args.adapter, **params)
            res = run_stream(adapter, args.agent, cfg, Path(args.out))
            run_dir = res.run_dir
        else:
            # Synthetic backtest
            rd, _ = run_backtest(cfg)
            run_dir = rd
        if args.report:
            from mmrl.report import generate_report
            html = generate_report(str(run_dir))
            print(f"Report -> {html}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()