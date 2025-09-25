# PEGCA Energy-Efficient VM Consolidation Simulator - Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Simulator](#running-the-simulator)
6. [Output Interpretation](#output-interpretation)
7. [Troubleshooting](#troubleshooting)
8. [Performance Tuning](#performance-tuning)
9. [Advanced Usage](#advanced-usage)
10. [Monitoring and Logging](#monitoring-and-logging)

## Overview

The PEGCA (Proactive Energy-efficient VM Consolidation Algorithm) simulator is a lightweight Python application designed to simulate energy-efficient virtual machine consolidation in data centers. It uses Exponential Moving Average (EMA) prediction to proactively pack low-usage VMs onto fewer physical hosts, then powers off empty hosts to save energy while maintaining performance safety.

### Key Features
- **Predictive Analytics**: EMA-based usage prediction with configurable alpha parameter
- **Smart Consolidation**: Greedy fit-first placement algorithm targeting 80% host utilization
- **Energy Optimization**: Automatic shutdown of empty hosts with energy savings calculation
- **Performance Safety**: High-watermark monitoring with automatic target utilization adjustment
- **Simulation Environment**: Self-contained with synthetic workload generation

## System Requirements

### Minimum Requirements
- **Operating System**: Linux, macOS, or Windows
- **Python Version**: Python 3.7 or higher
- **Memory**: 512 MB RAM
- **Storage**: 10 MB free space
- **CPU**: Any modern processor (simulation is CPU-bound)

### Recommended Requirements
- **Python Version**: Python 3.9 or higher
- **Memory**: 1 GB RAM
- **Storage**: 100 MB free space
- **CPU**: Multi-core processor for faster simulation

### Dependencies
The simulator uses only Python standard library modules:
- `math` - Mathematical operations
- `random` - Random number generation
- `statistics` - Statistical calculations
- `typing` - Type hints

**No external dependencies required** - the simulator is completely self-contained.

## Installation

### Step 1: Verify Python Installation

Check if Python 3 is installed on your system:

```bash
python3 --version
```

Expected output:
```
Python 3.x.x
```

If Python 3 is not installed, install it using your system's package manager:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip
```

**macOS (using Homebrew):**
```bash
brew install python3
```

**Windows:**
Download and install from [python.org](https://www.python.org/downloads/)

### Step 2: Download the Simulator

Create a project directory and download the simulator file:

```bash
# Create project directory
mkdir pegca-simulator
cd pegca-simulator

# Download or copy pegca_sim.py to this directory
# The file should be named exactly: pegca_sim.py
```

### Step 3: Verify File Structure

Ensure your directory contains only the simulator file:

```bash
ls -la
```

Expected output:
```
total 8
-rw-r--r-- 1 user user 8156 Dec 15 10:30 pegca_sim.py
```

### Step 4: Test Installation

Run a quick test to verify the installation:

```bash
python3 pegca_sim.py
```

Expected output format:
```python
{
  'energy_kwh_total': <float>,
  'migrations_total': <int>,
  'hosts_off_final': <int>,
  'util_mean_final': <float>,
  'util_p95_final': <float>,
  'hi_watermark_breaches': <int>,
  'final_target_util': <float>
}
```

## Configuration

### Default Configuration

The simulator comes with sensible defaults in the `Config` class:

```python
class Config:
    def __init__(
        self,
        alpha: float = 0.6,                    # EMA smoothing factor
        low_usage_threshold: float = 30.0,     # CPU % threshold for consolidation
        target_util: float = 0.80,             # Target host utilization (80%)
        hi_watermark: float = 0.90,            # High-watermark threshold (90%)
        dt_hours: float = 1.0,                 # Time per cycle (1 hour)
        cycles: int = 24,                      # Number of simulation cycles
        n_hosts: int = 20,                     # Number of physical hosts
        n_vms: int = 120,                      # Number of virtual machines
        seed: int = 7,                         # Random seed for reproducibility
    ):
```

### Configuration Parameters Explained

| Parameter | Default | Description | Range |
|-----------|---------|-------------|-------|
| `alpha` | 0.6 | EMA smoothing factor (higher = more responsive) | 0.0 - 1.0 |
| `low_usage_threshold` | 30.0 | CPU % below which VMs are consolidation candidates | 0.0 - 100.0 |
| `target_util` | 0.80 | Target host utilization for placement | 0.5 - 0.95 |
| `hi_watermark` | 0.90 | Performance safety threshold | 0.8 - 1.0 |
| `dt_hours` | 1.0 | Duration of each simulation cycle | 0.1 - 24.0 |
| `cycles` | 24 | Total simulation cycles | 1 - 1000 |
| `n_hosts` | 20 | Number of physical hosts | 1 - 1000 |
| `n_vms` | 120 | Number of virtual machines | 1 - 10000 |
| `seed` | 7 | Random seed for reproducible results | Any integer |

### Customizing Configuration

To modify the configuration, edit the `Config` instantiation in the `__main__` section:

```python
if __name__ == "__main__":
    cfg = Config(
        alpha=0.7,                    # More responsive prediction
        low_usage_threshold=25.0,     # More aggressive consolidation
        target_util=0.75,             # More conservative packing
        hi_watermark=0.85,            # Stricter performance monitoring
        dt_hours=0.5,                 # 30-minute cycles
        cycles=48,                    # 24-hour simulation
        n_hosts=50,                   # Larger data center
        n_vms=300,                    # More VMs
        seed=42,                      # Different random seed
    )
```

## Running the Simulator

### Basic Execution

Run the simulator with default settings:

```bash
python3 pegca_sim.py
```

### Running with Different Configurations

#### Scenario 1: Small Data Center
```python
cfg = Config(
    n_hosts=10,
    n_vms=50,
    cycles=12,
    target_util=0.70
)
```

#### Scenario 2: Large Data Center
```python
cfg = Config(
    n_hosts=100,
    n_vms=1000,
    cycles=48,
    target_util=0.85
)
```

#### Scenario 3: High-Performance Environment
```python
cfg = Config(
    target_util=0.75,
    hi_watermark=0.80,
    low_usage_threshold=20.0
)
```

### Batch Execution

To run multiple simulations with different parameters, create a batch script:

```bash
#!/bin/bash
# batch_simulations.sh

echo "Running PEGCA simulations..."

# Simulation 1: Default
echo "=== Default Configuration ==="
python3 pegca_sim.py > results_default.txt

# Simulation 2: Conservative
echo "=== Conservative Configuration ==="
python3 -c "
from pegca_sim import Config, simulate
cfg = Config(target_util=0.70, hi_watermark=0.80)
result = simulate(cfg)
print(result)
" > results_conservative.txt

# Simulation 3: Aggressive
echo "=== Aggressive Configuration ==="
python3 -c "
from pegca_sim import Config, simulate
cfg = Config(target_util=0.90, low_usage_threshold=40.0)
result = simulate(cfg)
print(result)
" > results_aggressive.txt

echo "All simulations completed!"
```

Make the script executable and run:
```bash
chmod +x batch_simulations.sh
./batch_simulations.sh
```

## Output Interpretation

### Output Format

The simulator produces a dictionary with the following metrics:

```python
{
    'energy_kwh_total': 15.432,           # Total energy saved (kWh)
    'migrations_total': 45,               # Total VM migrations performed
    'hosts_off_final': 8,                 # Number of hosts powered off
    'util_mean_final': 0.7845,            # Mean utilization of active hosts
    'util_p95_final': 0.9234,             # 95th percentile utilization
    'hi_watermark_breaches': 3,           # Performance threshold violations
    'final_target_util': 0.76             # Final target utilization (after adjustments)
}
```

### Metric Explanations

#### Energy Metrics
- **`energy_kwh_total`**: Total energy saved in kilowatt-hours
  - Calculated as: `Σ(P_idle × T_cycle) / 1000` for all OFF hosts
  - Higher values indicate better energy efficiency

#### Migration Metrics
- **`migrations_total`**: Total number of VM migrations performed
  - Indicates consolidation activity
  - Higher values suggest more aggressive consolidation

#### Host Utilization Metrics
- **`hosts_off_final`**: Number of hosts powered off at simulation end
  - Direct measure of consolidation success
  - Higher values indicate better resource efficiency

- **`util_mean_final`**: Average CPU utilization of active hosts
  - Target is around 0.80 (80%)
  - Values significantly below 0.80 may indicate over-consolidation

- **`util_p95_final`**: 95th percentile CPU utilization
  - Indicates peak load distribution
  - Values above 0.90 suggest potential performance risks

#### Performance Metrics
- **`hi_watermark_breaches`**: Number of times hosts exceeded 90% utilization
  - Lower values indicate better performance safety
  - High values may suggest need for more conservative settings

- **`final_target_util`**: Final target utilization after automatic adjustments
  - Starts at 0.80, decreases by 0.02 for each breach
  - Minimum value is 0.70
  - Lower final values indicate performance issues during simulation

### Performance Analysis

#### Good Performance Indicators
- `energy_kwh_total` > 0 (energy savings achieved)
- `hosts_off_final` > 0 (consolidation successful)
- `util_mean_final` between 0.70 and 0.85 (good utilization)
- `hi_watermark_breaches` < 5 (few performance violations)
- `final_target_util` close to 0.80 (stable operation)

#### Warning Signs
- `util_mean_final` < 0.60 (under-utilization)
- `util_p95_final` > 0.95 (high peak loads)
- `hi_watermark_breaches` > 10 (frequent performance issues)
- `final_target_util` < 0.72 (significant performance degradation)

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "python3: command not found"
**Problem**: Python 3 is not installed or not in PATH

**Solution**:
```bash
# Check if Python 3 is installed
which python3

# If not found, install Python 3
# Ubuntu/Debian:
sudo apt install python3

# macOS:
brew install python3

# Windows: Download from python.org
```

#### Issue 2: "No such file or directory: pegca_sim.py"
**Problem**: File not found in current directory

**Solution**:
```bash
# Check current directory
pwd

# List files
ls -la

# Navigate to correct directory
cd /path/to/pegca-simulator

# Verify file exists
ls -la pegca_sim.py
```

#### Issue 3: "Permission denied"
**Problem**: File permissions issue

**Solution**:
```bash
# Make file readable
chmod 644 pegca_sim.py

# Or make executable
chmod 755 pegca_sim.py
```

#### Issue 4: Simulation runs but produces unexpected results
**Problem**: Configuration or logic issues

**Solutions**:
1. **Check random seed**: Ensure `seed` parameter is set for reproducible results
2. **Verify parameters**: Ensure all parameters are within valid ranges
3. **Check initial conditions**: Verify `n_hosts` and `n_vms` are reasonable
4. **Monitor output**: Look for warning signs in the output metrics

#### Issue 5: Simulation takes too long to run
**Problem**: Large simulation parameters

**Solutions**:
1. **Reduce scale**: Decrease `n_hosts` and `n_vms`
2. **Reduce cycles**: Decrease `cycles` parameter
3. **Check system resources**: Ensure adequate CPU and memory

### Debug Mode

To enable detailed debugging, modify the simulator to add print statements:

```python
def simulate(cfg: Config) -> Dict[str, float]:
    print(f"Starting simulation with {cfg.n_hosts} hosts and {cfg.n_vms} VMs")
    print(f"Configuration: alpha={cfg.alpha}, target_util={cfg.target_util}")
    
    # ... existing code ...
    
    for t in range(cfg.cycles):
        print(f"Cycle {t+1}/{cfg.cycles}")
        
        # ... existing code ...
        
        if breach:
            print(f"High watermark breach detected! Adjusting target_util to {cfg.target_util}")
```

## Performance Tuning

### Optimization Strategies

#### 1. Parameter Tuning

**For Higher Energy Savings:**
```python
cfg = Config(
    target_util=0.85,              # Higher packing density
    low_usage_threshold=25.0,      # More aggressive consolidation
    alpha=0.7                      # More responsive prediction
)
```

**For Better Performance Safety:**
```python
cfg = Config(
    target_util=0.75,              # More conservative packing
    hi_watermark=0.85,             # Stricter performance monitoring
    alpha=0.5                      # More stable prediction
)
```

**For Balanced Operation:**
```python
cfg = Config(
    target_util=0.80,              # Balanced packing
    hi_watermark=0.90,             # Standard performance monitoring
    alpha=0.6                      # Standard prediction responsiveness
)
```

#### 2. Scale Optimization

**Small Data Centers (1-50 hosts):**
- Use default parameters
- Monitor for over-consolidation
- Consider shorter cycle times

**Medium Data Centers (50-200 hosts):**
- Increase `target_util` to 0.82-0.85
- Use longer cycle times (2-4 hours)
- Monitor peak utilization carefully

**Large Data Centers (200+ hosts):**
- Use higher `target_util` (0.85-0.90)
- Implement batch processing
- Consider parallel simulation runs

#### 3. Workload-Specific Tuning

**Predictable Workloads:**
```python
cfg = Config(
    alpha=0.8,                     # High responsiveness
    target_util=0.85               # Aggressive packing
)
```

**Variable Workloads:**
```python
cfg = Config(
    alpha=0.4,                     # Stable prediction
    target_util=0.75,              # Conservative packing
    hi_watermark=0.85              # Stricter monitoring
)
```

**High-Performance Workloads:**
```python
cfg = Config(
    target_util=0.70,              # Very conservative
    hi_watermark=0.80,             # Strict monitoring
    low_usage_threshold=20.0       # Only very low usage VMs
)
```

## Advanced Usage

### Custom Workload Generation

To modify the synthetic workload, edit the `synth_drift` function:

```python
def synth_drift(t: int) -> float:
    """Custom workload pattern."""
    # Add your custom workload logic here
    base_load = 20.0
    daily_pattern = 15.0 * math.sin(2 * math.pi * (t % 24) / 24.0)
    weekly_pattern = 10.0 * math.sin(2 * math.pi * (t % 168) / 168.0)
    noise = random.uniform(-5.0, 5.0)
    
    return base_load + daily_pattern + weekly_pattern + noise
```

### Custom Host Configurations

To modify host specifications, edit the `Host` instantiation:

```python
# Custom host with different specifications
hosts = []
for i in range(cfg.n_hosts):
    if i < cfg.n_hosts // 2:
        # High-performance hosts
        hosts.append(Host(
            hid=i,
            cpu_cap=200.0,
            mem_cap=200.0,
            power_idle_watts=200.0,
            power_peak_watts=500.0
        ))
    else:
        # Standard hosts
        hosts.append(Host(
            hid=i,
            cpu_cap=100.0,
            mem_cap=100.0,
            power_idle_watts=120.0,
            power_peak_watts=300.0
        ))
```

### Integration with External Systems

#### CSV Output
Add CSV output functionality:

```python
import csv

def save_results_to_csv(results: Dict[str, float], filename: str):
    """Save simulation results to CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=results.keys())
        writer.writeheader()
        writer.writerow(results)

# Usage
if __name__ == "__main__":
    cfg = Config()
    results = simulate(cfg)
    save_results_to_csv(results, 'pegca_results.csv')
    print(results)
```

#### JSON Output
Add JSON output functionality:

```python
import json

def save_results_to_json(results: Dict[str, float], filename: str):
    """Save simulation results to JSON file."""
    with open(filename, 'w') as jsonfile:
        json.dump(results, jsonfile, indent=2)

# Usage
if __name__ == "__main__":
    cfg = Config()
    results = simulate(cfg)
    save_results_to_json(results, 'pegca_results.json')
    print(results)
```

### Batch Processing

Create a batch processing script for multiple simulations:

```python
# batch_processor.py
from pegca_sim import Config, simulate
import json
import time

def run_batch_simulations():
    """Run multiple simulations with different parameters."""
    
    # Define parameter sets
    parameter_sets = [
        {"target_util": 0.70, "name": "conservative"},
        {"target_util": 0.80, "name": "balanced"},
        {"target_util": 0.90, "name": "aggressive"},
        {"alpha": 0.4, "name": "stable_prediction"},
        {"alpha": 0.8, "name": "responsive_prediction"},
        {"low_usage_threshold": 20.0, "name": "strict_consolidation"},
        {"low_usage_threshold": 40.0, "name": "loose_consolidation"},
    ]
    
    results = []
    
    for params in parameter_sets:
        print(f"Running simulation: {params['name']}")
        
        # Create config with custom parameters
        cfg = Config(**{k: v for k, v in params.items() if k != 'name'})
        
        # Run simulation
        start_time = time.time()
        result = simulate(cfg)
        end_time = time.time()
        
        # Add metadata
        result['simulation_name'] = params['name']
        result['execution_time'] = round(end_time - start_time, 2)
        result['parameters'] = {k: v for k, v in params.items() if k != 'name'}
        
        results.append(result)
        
        print(f"Completed in {result['execution_time']} seconds")
        print(f"Energy saved: {result['energy_kwh_total']} kWh")
        print(f"Hosts powered off: {result['hosts_off_final']}")
        print("-" * 50)
    
    # Save all results
    with open('batch_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Batch processing completed. Results saved to batch_results.json")
    
    # Print summary
    print("\n=== SUMMARY ===")
    for result in results:
        print(f"{result['simulation_name']}: "
              f"{result['energy_kwh_total']} kWh saved, "
              f"{result['hosts_off_final']} hosts off")

if __name__ == "__main__":
    run_batch_simulations()
```

## Monitoring and Logging

### Basic Logging

Add logging functionality to track simulation progress:

```python
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pegca_simulation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def simulate_with_logging(cfg: Config) -> Dict[str, float]:
    """Simulation with detailed logging."""
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting PEGCA simulation")
    logger.info(f"Configuration: {cfg.__dict__}")
    
    # ... existing simulation code ...
    
    for t in range(cfg.cycles):
        logger.info(f"Cycle {t+1}/{cfg.cycles} started")
        
        # ... existing code ...
        
        if breach:
            logger.warning(f"High watermark breach in cycle {t+1}")
            logger.info(f"Target utilization adjusted to {cfg.target_util}")
        
        logger.info(f"Cycle {t+1} completed: {len(plan)} migrations, {len(off)} hosts off")
    
    logger.info(f"Simulation completed: {total_kwh} kWh saved")
    return result
```

### Performance Monitoring

Add performance monitoring to track simulation metrics:

```python
import time
import psutil
import os

def monitor_simulation_performance():
    """Monitor system performance during simulation."""
    process = psutil.Process(os.getpid())
    
    start_time = time.time()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    def get_metrics():
        current_time = time.time()
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent = process.cpu_percent()
        
        return {
            'elapsed_time': round(current_time - start_time, 2),
            'memory_usage_mb': round(current_memory, 2),
            'memory_delta_mb': round(current_memory - start_memory, 2),
            'cpu_percent': round(cpu_percent, 2)
        }
    
    return get_metrics

# Usage in simulation
def simulate_with_monitoring(cfg: Config) -> Dict[str, float]:
    """Simulation with performance monitoring."""
    monitor = monitor_simulation_performance()
    
    # ... existing simulation code ...
    
    for t in range(cfg.cycles):
        metrics = monitor()
        print(f"Cycle {t+1}: {metrics}")
        
        # ... existing code ...
    
    return result
```

### Real-time Visualization

For real-time monitoring, you can add simple text-based visualization:

```python
def print_simulation_status(cycle: int, total_cycles: int, 
                          migrations: int, hosts_off: int, 
                          energy_saved: float, target_util: float):
    """Print real-time simulation status."""
    progress = (cycle / total_cycles) * 100
    bar_length = 30
    filled_length = int(bar_length * cycle // total_cycles)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    print(f"\rProgress: |{bar}| {progress:.1f}% "
          f"Cycle: {cycle}/{total_cycles} "
          f"Migrations: {migrations} "
          f"Hosts OFF: {hosts_off} "
          f"Energy: {energy_saved:.2f} kWh "
          f"Target: {target_util:.2f}", end='', flush=True)

# Usage in simulation loop
for t in range(cfg.cycles):
    # ... existing code ...
    
    print_simulation_status(
        cycle=t+1,
        total_cycles=cfg.cycles,
        migrations=len(plan),
        hosts_off=len(off),
        energy_saved=total_kwh,
        target_util=cfg.target_util
    )
```

## Conclusion

This deployment guide provides comprehensive instructions for installing, configuring, and running the PEGCA Energy-Efficient VM Consolidation simulator. The simulator is designed to be lightweight, self-contained, and easy to deploy in any environment with Python 3.7 or higher.

### Key Takeaways

1. **Simple Installation**: No external dependencies required
2. **Flexible Configuration**: Easily tunable parameters for different scenarios
3. **Comprehensive Output**: Detailed metrics for performance analysis
4. **Scalable**: Can handle small to large data center simulations
5. **Reproducible**: Deterministic results with configurable random seeds

### Next Steps

1. Start with default configuration to understand baseline performance
2. Experiment with different parameter sets for your specific use case
3. Use batch processing for comprehensive parameter analysis
4. Implement monitoring and logging for production-like environments
5. Consider integration with external systems for real-world deployment

For additional support or questions, refer to the troubleshooting section or modify the simulator code according to your specific requirements.
