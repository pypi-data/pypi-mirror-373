#!/usr/bin/env python3
"""
Comprehensive test script for NB-QOL.
Run all tests or specific test suites with command-line options.
"""

import os
import sys
import time
import re
import shutil
import subprocess
import argparse
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent.absolute()

# Filter patterns for suppressing noisy output
LOG_FILTER_PATTERN = re.compile(r'time="[^"]*" level=(info|debug)\s')
ACT_FILTER_PATTERN = re.compile(r'(time=|level=|Using docker host|⚠ You are using Apple M-series chip)')


def filter_output(process, filter_pattern=LOG_FILTER_PATTERN, use_act_filter=False):
    """Filter process output to remove debug and info logs.
    
    Args:
        process: subprocess.Popen object with stdout pipe
        filter_pattern: regex pattern to match lines to filter
        use_act_filter: If True, use ACT_FILTER_PATTERN instead of the provided pattern
        
    Yields:
        Lines of output that don't match the filter pattern
    """
    pattern = ACT_FILTER_PATTERN if use_act_filter else filter_pattern
    
    for line in iter(process.stdout.readline, b''):
        line_str = line.decode('utf-8')
        if not pattern.search(line_str):
            yield line_str

class TestRunner:
    def __init__(self):
        self.results = {}

    def run_test(self, name, command, cwd=None, shell=None, filter_logs=False):
        """Run a test and record its result"""
        print(f"\n\n{'=' * 50}")
        print(f"Running {name}...")
        print(f"{'=' * 50}")
        
        start_time = time.time()
        try:
            # Determine if shell should be used
            use_shell = shell if shell is not None else isinstance(command, str)
            
            # Set environment variables for act commands
            env = os.environ.copy()
            # Set log level to warn for act commands to reduce verbosity
            if isinstance(command, list) and command and command[0] == "act":
                env["ACT_LOG"] = "warn"
                filter_logs = True
            
            if filter_logs:
                # For act commands, use Popen with output filtering
                process = subprocess.Popen(
                    command,
                    cwd=cwd or ROOT_DIR,
                    shell=use_shell,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=False,
                )
                
                # Process and filter the output - use act filter for act commands
                for line in filter_output(process, use_act_filter=command[0]=="act" if isinstance(command, list) else False):
                    sys.stdout.write(line)
                    sys.stdout.flush()
                
                # Wait for process to finish and check return code
                return_code = process.wait()
                if return_code != 0:
                    raise subprocess.CalledProcessError(return_code, command)
            else:
                # For non-act commands, use standard subprocess.run
                subprocess.run(
                    command,
                    cwd=cwd or ROOT_DIR,
                    check=True,
                    shell=use_shell,
                    env=env,
                )
            success = True
        except subprocess.CalledProcessError as e:
            print(f"Error in {name}: {e}")
            success = False
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.results[name] = {
            "success": success,
            "duration": duration,
        }
        return success

    def run_import_tests(self):
        """Run the basic import tests"""
        return self.run_test(
            "Import Tests",
            [sys.executable, "-m", "pytest", "tests/test_imports.py", "-v"],
        )
        
    def run_convert_tests(self):
        """Run the convert module tests"""
        return self.run_test(
            "Convert Tests",
            [sys.executable, "-m", "pytest", "tests/test_convert.py", "-v"],
        )
        
    def run_analyzer_tests(self):
        """Run the analyzer module tests"""
        return self.run_test(
            "Analyzer Tests",
            [sys.executable, "-m", "pytest", "tests/test_analyzer.py", "-v"],
        )

    def run_installation_tests(self):
        """Run the installation tests"""
        return self.run_test(
            "Installation Tests",
            [sys.executable, "-m", "pytest", "tests/test_installation.py", "-v"],
        )

    def build_docs(self):
        """Build the documentation"""
        return self.run_test(
            "Docs Build",
            "sphinx-build -b html . build/html",
            cwd=os.path.join(ROOT_DIR, "docs"),
        )

    def run_package_build_test(self):
        """Test building the package"""
        return self.run_test(
            "Package Build",
            ["hatch", "build"],
        )
        
    def check_act_installed(self):
        """Check if the act tool is installed"""
        try:
            subprocess.run(["which", "act"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            print("\n⚠️  Warning: 'act' is not installed. Workflow tests will be skipped.")
            print("To install act, run: brew install act (macOS)")
            print("or visit https://github.com/nektos/act for other platforms")
            return False
            
    def validate_workflow(self, workflow_name):
        """Validate a GitHub workflow file"""
        workflow_path = os.path.join(ROOT_DIR, ".github/workflows", workflow_name)
        if not os.path.exists(workflow_path):
            print(f"Error: Workflow file {workflow_path} not found")
            print("Available workflows:")
            for wf in os.listdir(os.path.join(ROOT_DIR, ".github/workflows")):
                if wf.endswith(".yml"):
                    print(f"  {wf}")
            return False
            
        # Run a simple validation check - you can expand this
        return self.run_test(
            f"Workflow Validation: {workflow_name}",
            f"cat .github/workflows/{workflow_name} | grep -n 'name:'"
        )

    def list_workflow_jobs(self, workflow_name):
        """List jobs in a GitHub workflow"""
        # Check if act is installed
        if not self.check_act_installed():
            return False
        
        # Build the command with architecture flag for M-series Macs
        cmd = ["act", "--workflows", f".github/workflows/{workflow_name}", "--list", "-q"]
        if self.is_m_series_mac():
            cmd.extend(["--container-architecture", "linux/amd64"])
            
        return self.run_test(
            f"Workflow Jobs: {workflow_name}",
            cmd,
            filter_logs=True
        )
            
    def is_m_series_mac(self):
        """Check if the system is an M-series Mac (Apple Silicon)"""
        return sys.platform == 'darwin' and os.uname().machine.startswith('arm')
            
    def test_workflow(self, workflow_name, event_file=None, dry_run=False):
        """Test a GitHub Actions workflow locally using act"""
        test_name = f"Workflow: {workflow_name}"
        if dry_run:
            test_name = f"Workflow Preview: {workflow_name}"
            
        # First validate the workflow
        if not self.validate_workflow(workflow_name):
            return False
            
        # List available jobs in the workflow
        if not self.list_workflow_jobs(workflow_name):
            return False
            
        # Check if act is installed
        if not self.check_act_installed():
            return False
            
        # Determine event type from workflow file
        workflow_path = os.path.join(ROOT_DIR, ".github/workflows", workflow_name)
        with open(workflow_path, 'r') as f:
            content = f.read()
            if 'workflow_dispatch:' in content:
                event = 'workflow_dispatch'
            elif 'pull_request:' in content:
                event = 'pull_request'
            elif 'push:' in content:
                event = 'push'
            else:
                event = 'workflow_dispatch'  # Default
        
        # Always show the workflow contents
        print(f"\nWorkflow contents: {workflow_name}")
        print("-" * 50)
        os.system(f"cat {workflow_path}")
        print("-" * 50)
        
        # Set the environment variable for the command execution
        # We'll modify the run_test method to use this environment
        
        # Build act command
        m_series_mac = self.is_m_series_mac()
        cmd = ["act", "--workflows", f".github/workflows/{workflow_name}", "-q"]
        
        # Create default event files if they don't exist
        default_event_dir = os.path.join(ROOT_DIR, ".github/workflows/test-events")
        os.makedirs(default_event_dir, exist_ok=True)
        
        # Default workflow_dispatch event for most workflows
        default_event_path = os.path.join(default_event_dir, "workflow_dispatch.json")
        if not os.path.exists(default_event_path):
            with open(default_event_path, 'w') as f:
                f.write('{\n  "inputs": {}\n}')
                
        # Special event file for publish workflow
        publish_event_path = os.path.join(default_event_dir, "workflow_dispatch_publish.json")
        if not os.path.exists(publish_event_path):
            with open(publish_event_path, 'w') as f:
                f.write('{\n  "inputs": {\n    "version": "",\n    "publish_to": "pypi"\n  }\n}')
        
        # Use the specified event file or workflow-specific default
        if event_file:
            event_path = os.path.join(ROOT_DIR, ".github/workflows/test-events", f"{event_file}.json")
            if os.path.exists(event_path):
                cmd.extend(["--eventpath", f".github/workflows/test-events/{event_file}.json"])
            else:
                cmd.extend(["--eventpath", default_event_path])
        else:
            # Use publish workflow event for publish.yml, default for others
            if workflow_name == "publish.yml":
                cmd.extend(["-e", "workflow_dispatch", "--eventpath", publish_event_path])
            else:
                cmd.extend(["-e", "workflow_dispatch", "--eventpath", default_event_path])
            
        # Add dry run flag if requested
        if dry_run:
            cmd.append("--dryrun")
        else:
            # When executing workflows for real, use privileged mode 
            # and bind the host Docker socket for better container support
            cmd.append("--privileged")
            cmd.append("--bind")
            
        # Add architecture flag for M-series Macs
        if m_series_mac:
            cmd.extend(["--container-architecture", "linux/amd64"])
            
        # Convert to string for display
        act_cmd_str = " ".join(cmd)
        print(f"Running command: {act_cmd_str}")
        
        # Actually run the workflow if not in dry run mode
        success = True
        start_time = time.time()
        if not dry_run:
            try:
                # Set environment with warn log level
                env = os.environ.copy()
                env["ACT_LOG"] = "warn"
                
                # Use Popen with output filtering for act commands
                process = subprocess.Popen(
                    cmd,
                    cwd=ROOT_DIR,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=False,
                )
                
                # Process and filter the output for act commands
                for line in filter_output(process, use_act_filter=True):
                    sys.stdout.write(line)
                    sys.stdout.flush()
                
                # Wait for process to finish and check return code
                return_code = process.wait()
                if return_code != 0:
                    raise subprocess.CalledProcessError(return_code, cmd)
                
                print(f"\n✅ Workflow {workflow_name} executed successfully")
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Workflow {workflow_name} execution failed: {e}")
                success = False
        else:
            print(f"\n✅ Workflow {workflow_name} validated successfully")
            
        end_time = time.time()
        duration = end_time - start_time
            
        # Result message for test reporting
        self.results[test_name] = {
            "success": success,
            "duration": duration,
        }
            
        return success
        
    def test_all_workflows(self, dry_run=False):
        """Test all GitHub workflows with actual execution by default"""
        workflows_dir = os.path.join(ROOT_DIR, ".github/workflows")
        
        # Skip workflow testing if no workflow files found
        if not os.path.exists(workflows_dir):
            print("No workflows directory found")
            return False
            
        # Get list of workflows
        workflows = [f for f in os.listdir(workflows_dir) if f.endswith(".yml")]
        
        if not workflows:
            print("No workflow files found")
            return False
            
        execution_mode = "EXECUTING" if not dry_run else "DRY RUN"
        print(f"\n=== GitHub Workflows ({execution_mode}) ===")
        for i, workflow in enumerate(workflows, 1):
            print(f"{i}. {workflow}")
        
        # First validate all workflows
        for workflow in workflows:
            self.validate_workflow(workflow)
        
        # Then check act is installed only once
        if not self.check_act_installed():
            return False
            
        # Then list jobs for all workflows at once
        # Build the command with architecture flag for M-series Macs
        m_series_mac = self.is_m_series_mac()
        act_cmd = ["act"]
        if m_series_mac:
            act_cmd.extend(["--container-architecture", "linux/amd64"])
            
        # List all workflows
        list_cmd = act_cmd.copy()
        list_cmd.extend(["--list", "-q"])
        self.run_test("Workflow Jobs Summary", list_cmd, filter_logs=True)
        
        # Test each workflow
        all_passed = True
        for workflow in workflows:
            result = self.test_workflow(workflow, dry_run=dry_run)
            all_passed = all_passed and result
        
        return all_passed

    def print_summary(self):
        """Print summary of all test results"""
        print("\n\n" + "=" * 80)
        print(f"{'TEST SUMMARY':^80}")
        print("=" * 80)
        print(f"{'Test':<40} {'Result':<10} {'Duration':<10}")
        print("-" * 80)
        
        all_success = True
        for name, result in self.results.items():
            status = "PASSED" if result["success"] else "FAILED"
            duration = f"{result['duration']:.2f}s"
            print(f"{name:<40} {status:<10} {duration:<10}")
            all_success = all_success and result["success"]
        
        print("=" * 80)
        print(f"Overall Status: {'SUCCESS' if all_success else 'FAILURE'}")
        print("=" * 80)
        
        return all_success
    
def clean_test_outputs(keep=[]):
    """Clean and remove test outputs"""

    # Remove build directory
    build_dir = os.path.join(ROOT_DIR, "build")
    if os.path.exists(build_dir):
        if 'build' not in keep:
            shutil.rmtree(build_dir)

    # Remove test-events directory
    dist_dir = os.path.join(ROOT_DIR, "dist")
    if os.path.exists(dist_dir):
        if 'dist' not in keep:
            shutil.rmtree(dist_dir)


def main():
    parser = argparse.ArgumentParser(description="Run tests for NB-QOL")
    parser.add_argument(
        "--all", action="store_true", default=True, help="Run all tests including workflows (default)"
    )
    parser.add_argument("--imports", action="store_true", help="Run import tests")
    parser.add_argument(
        "--convert", action="store_true", help="Run convert module tests"
    )
    parser.add_argument(
        "--analyzer", action="store_true", help="Run analyzer module tests"
    )
    parser.add_argument(
        "--installation", action="store_true", help="Run installation tests"
    )
    parser.add_argument(
        "--docs", action="store_true", help="Build documentation"
    )
    parser.add_argument(
        "--package-build", action="store_true", help="Test package building"
    )
    # Workflow testing options
    workflow_group = parser.add_argument_group("Workflow Testing")
    workflow_group.add_argument(
        "--workflows", action="store_true", help="Test all GitHub workflows (with actual execution)"
    )
    workflow_group.add_argument(
        "--workflow", help="Test a specific GitHub workflow (e.g. publish.yml, docs.yml)"
    )
    workflow_group.add_argument(
        "--event", help="Event file to use for workflow testing (without .json extension)"
    )
    workflow_group.add_argument(
        "--dry-run", action="store_true", 
        help="Only perform a dry run of the workflow without execution"
    )
    parser.add_argument(
        "--run-cleanup", default=True, action="store_true", help="Clean and remove test outputs"
    )
    
    args = parser.parse_args()
    
    # If specific tests are specified, don't run all tests
    if (args.imports or args.convert or args.analyzer or args.installation or 
        args.docs or args.package_build or args.workflow or args.workflows):
        args.all = False
    
    runner = TestRunner()
    
    # Handle workflow testing
    if args.workflow or args.workflows:
        # Use dry_run parameter if provided
        dry_run = args.dry_run
        
        if args.workflows:
            # Test all workflows
            runner.test_all_workflows(dry_run=dry_run)
        elif args.workflow:
            # Test specific workflow
            runner.test_workflow(args.workflow, args.event, dry_run=dry_run)
    else:
        # Run standard tests
        if args.all or args.imports:
            runner.run_import_tests()
            
        if args.all or args.convert:
            runner.run_convert_tests()
            
        if args.all or args.analyzer:
            runner.run_analyzer_tests()
        
        if args.all or args.installation:
            runner.run_installation_tests()
        
        if args.all or args.docs:
            runner.build_docs()
        
        if args.all or args.package_build:
            runner.run_package_build_test()
            
        # Include workflow tests in the "all" option
        if args.all:
            # Execute workflows by default
            runner.test_all_workflows(dry_run=args.dry_run)

        # Clean up test outputs
        if args.run_cleanup:
            clean_test_outputs()
    
    success = runner.print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()