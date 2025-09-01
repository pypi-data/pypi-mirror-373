import pandas as pd
import os, xml
import subprocess
from typing import List, Dict, Union, Optional, Any
# force XML to import etree
from xml.etree import ElementTree

# Utility functions
def normalize_device_ids(device_ids: Optional[Union[int, List[int]]]) -> Optional[List[int]]:
    """Normalize device IDs to a consistent list format.
    
    Args:
        device_ids: Single device ID or list of device IDs
        
    Returns:
        List of device IDs or None if the input was None
    """
    if device_ids is None:
        return None
    return [device_ids] if not isinstance(device_ids, list) else device_ids

def memory_to_gb(value_kb: Union[int, str]) -> float:
    """Convert memory value in KB to GB.
    
    Args:
        value_kb: Memory value in KB, can be int or string
        
    Returns:
        Memory value in GB, rounded to 2 decimal places
    """
    if isinstance(value_kb, str):
        value_kb = int(value_kb.split()[0])
    return round(int(value_kb) / 1024, 2)

def format_key(key: str, pretty: bool = True) -> str:
    """Format key names for consistent display.
    
    Args:
        key: The key to format
        pretty: If True, use human-readable format; otherwise, use code-friendly format
        
    Returns:
        Formatted key
    """
    if pretty:
        return key.replace('_', ' ').title().replace('Gpu', 'GPU')
    return key.lower().replace(' ', '_').replace('(','').replace(')','')

def safe_subprocess_call(command: Union[List[str], str], shell: bool = False) -> Optional[str]:
    """Execute subprocess command with proper error handling.
    
    Args:
        command: Command to execute (list or string)
        shell: Whether to use shell execution
        
    Returns:
        Command output as string or None if command failed
    """
    try:
        return subprocess.check_output(command, shell=shell).decode("utf-8")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def count_cuda_devices() -> int:
    """Count the number of available CUDA devices using nvidia-smi.
    
    Returns:
        int: Number of available CUDA devices, or 0 if none found
        
    Examples:
        >>> from nbqol import devices
        >>> num_devices = devices.count_cuda_devices()
        >>> print(f"Found {num_devices} CUDA devices")
    """
    command = ["nvidia-smi", "--query-gpu=gpu_name", 
               "--format=csv,noheader,nounits"]
    
    output = safe_subprocess_call(command)
    if output:
        return len(output.strip().split("\n"))
    return 0  # no gpus if nvidia-smi fails to run

def get_nvidia_smi(
    device_ids: Optional[Union[int, List[int]]] = None, 
    accessible: bool = False, 
    to_pandas: bool = False, 
    **kwargs
) -> Union[Dict[int, Dict[str, Any]], pd.DataFrame, pd.Series]:
    """Get NVIDIA GPU information using nvidia-smi.
    
    This function queries the NVIDIA System Management Interface to get detailed
    information about available GPUs, including memory usage, device names, and
    running processes.
    
    Args:
        device_ids: Specific device ID(s) to query. If None, query all devices.
        accessible: If True, use more code-friendly key names for the output.
        to_pandas: If True, return the results as a pandas DataFrame or Series.
        **kwargs:
            check_visible (bool): If True, only return devices in CUDA_VISIBLE_DEVICES.
            device_prefix (str): Prefix for device names (default: 'cuda:').
    
    Returns:
        Dictionary, DataFrame, or Series containing GPU information.
        
    Examples:
        >>> from nbqol import devices
        >>> # Get info for all GPUs
        >>> gpu_info = devices.get_nvidia_smi()
        >>> # Get info for specific GPU
        >>> gpu_info = devices.get_nvidia_smi(0)
        >>> # Get as pandas DataFrame
        >>> gpu_df = devices.get_nvidia_smi(to_pandas=True)
    """
    accessible_names = {
        'GPU ID': 'gpu_id',
        'GPU Name': 'name',
        'Device Name': 'device_name', 
        'Utilization (%)': 'utilization', 
        '# Processes': 'n_processes', 
        'Total Memory': 'total_memory',
        'Used Memory': 'used_memory',
        'Free Memory': 'free_memory', 
        'Used Memory (%)': 'used_memory_%',
        'Free Memory (%)': 'free_memory_%'
    }
                        
    key_outputs = [
        'Device Name', 'Used Memory', 'Total Memory', 'Free Memory', 
        'Free Memory (%)', 'Utilization (%)', '# Processes'
    ]
    
    # Get GPU information in XML format
    command = "nvidia-smi -q -x"
    gpu_info_xml = safe_subprocess_call(command, shell=True)
    if not gpu_info_xml:
        return {} if not to_pandas else pd.DataFrame()
    
    gpu_info_tree = xml.etree.ElementTree.fromstring(gpu_info_xml)

    # Check if we should respect CUDA_VISIBLE_DEVICES
    check_visible_devices = kwargs.pop('check_visible', False)
    visible_devices = range(len(gpu_info_tree.findall("gpu")))
    visible_devices_setting = os.environ.get('CUDA_VISIBLE_DEVICES', None)
    if visible_devices_setting is not None and check_visible_devices:
        visible_devices = list(map(int, visible_devices_setting.split(',')))

    device_prefix = kwargs.pop('device_prefix', 'cuda:')

    # Normalize device_ids to list format
    device_ids = normalize_device_ids(device_ids)

    # Parse GPU information
    gpu_info, device_id = {}, -1
    for gpu_i, gpu in enumerate(gpu_info_tree.findall("gpu")):
        if gpu_i in visible_devices:
            device_id += 1  # update, respecting visibility

            if device_ids is not None and gpu_i not in device_ids:
                continue  # skip if not in requested devices

            # Get basic GPU information
            device_name = f"{device_prefix}{device_id}"
            memory_info = gpu.find("fb_memory_usage")
            product_name = gpu.find("product_name").text
            gpu_id = gpu.attrib['id']  # device index, visible or not

            # Parse memory information
            used_memory = memory_to_gb(memory_info.find("used").text.split()[0])
            free_memory = memory_to_gb(memory_info.find("free").text.split()[0])
            total_memory = memory_to_gb(memory_info.find("total").text.split()[0])
            
            # Calculate percentages
            used_memory_percent = round((used_memory / total_memory) * 100, 2)
            free_memory_percent = round((free_memory / total_memory) * 100, 2) 

            # Count running processes
            processes = gpu.find("processes")
            num_processes = 0
            if processes is not None:
                num_processes = len(processes.findall("process_info"))

            # Store GPU information
            gpu_info[device_id] = {
                "GPU ID": gpu_id, 
                "GPU Name": product_name,
                "Device Name": device_name,
                "Free Memory": f"{free_memory} GB",
                "Used Memory": f"{used_memory} GB",
                "Total Memory": f"{total_memory} GB",
                "Free Memory (%)": free_memory_percent,
                "Used Memory (%)": used_memory_percent,
                "# Processes": num_processes,
            }

    # Prepare the iterator for the result
    iterator = range(len(gpu_info)) if device_ids is None else device_ids

    # Transform to accessible format if requested
    if accessible:
        gpu_info = [{accessible_names[key]: value for key, value in 
                    gpu_info[i].items()} for i in iterator]

    # Convert to pandas if requested
    if to_pandas:
        if not isinstance(gpu_info, list):
            gpu_info = list(gpu_info.values())
        if len(gpu_info) == 1:
            return pd.Series(gpu_info[0])
        else:  # return full dataframe
            return pd.DataFrame(gpu_info)
            
    return {i: gpu_info[i] for i in iterator}

def cuda_device_report(device_ids=None, simple=True, pretty=True, 
                       to_pandas=False, to_dict=False, **kwargs):
    
    if device_ids is not None:
        if not isinstance(device_ids, list):
            device_ids = [device_ids]
        if not all(isinstance(id, int) for id in list(device_ids)):
            raise ValueError('device_ids must be an integer IDs or list thereof')
    
    nvidia_smi_info = get_nvidia_smi(device_ids, not pretty, to_pandas, **kwargs)

    if to_pandas and to_dict:
        raise ValueError('to_pandas and to_dict cannot both be True...')

    if to_pandas or to_dict:
        return nvidia_smi_info

    def make_accessible(key):
        return key.lower().replace(' ', '_').replace('(','').replace(')','')

    report_keys = ['GPU Name', 'Total Memory', 'Used Memory', 
                    'Free Memory', 'Free Memory (%)'] # full

    accessible_info = {i: {make_accessible(key): val for key, val 
                           in info.items()} for i, info in nvidia_smi_info.items()}

    if not pretty:
        report_keys = [make_accessible(key) for key in report_keys]

    # give user a chance to input their own report keys
    report_keys = kwargs.pop('report_keys', report_keys)

    if device_ids is None:
        device_ids = list(nvidia_smi_info.keys())
    
    for index, id in enumerate(device_ids):
        report = accessible_info[id]
        if simple: # single-line
            print(f"({id}) {report['gpu_name']}: {report['total_memory']}"
                  + f" ({report['free_memory_%']}% Free)") # 1-line report

        else: # multi-line report
            if index > 0: # first line item
                print('') # empty seperator

            printout = '\n  '.join([f'{key}: {value}' for key, value
                                    in nvidia_smi_info[id].items() 
                                    if key in report_keys]) # parse

            
            print(f'({id})', printout) # id first, then info...   

def torch_device_report(device, readable=True, pretty=True, 
                        to_pandas=True, **extra_kwargs):
    
    from torch.cuda import get_device_properties
    from torch.cuda.memory import mem_get_info
    
    device_props = get_device_properties(device)
    device_memory = mem_get_info(device)

    free_memory = device_memory[1] - device_memory[0]

    report_info = {'gpu_name': device_props.name,
                   'total_memory': device_memory[1],
                   'used_memory': device_memory[0],
                   'free_memory': free_memory, # precalc
                   'free_memory_(%)': (device_memory[0] / 
                                       device_memory[1]) * 100}

    def key_to_title(key):
        return key.replace('_', ' ').title().replace('Gpu', 'GPU')

    def make_readable(val):
        if isinstance(val, (float, int)):
            if not val > 100.0: # percent!
                return f'{val:.1f}%'
                
            else: # convert to gigbytes
                return f'{val / 1024**3:.2f}GB'
                
        return val # original value as is

    if readable:
        report_info = {k: make_readable(v) for k,v in report_info.items()}
        
    if pretty:
        report_info = {key_to_title(k): v for k, v in report_info.items()}

    if to_pandas:
        return pd.Series(report_info)

    print('\n  '.join([f'{key}: {value}' for key, value in report_info.items()]))

def set_cuda_visibles(*args, report='torch', **kwargs) -> Optional[pd.DataFrame]:
    """Set visible CUDA devices and optionally report their status.
    
    This function sets the CUDA_VISIBLE_DEVICES environment variable to limit
    which GPUs are accessible to CUDA applications. It can also generate a report
    of the selected devices.
    
    Args:
        *args: Device IDs to make visible. Can be individual numbers or lists.
        report: Report type ('torch', 'nvidia', or None for no report).
        **kwargs:
            verbose (bool): Print device selection message.
            to_pandas (bool): Return report as pandas DataFrame (torch report only).
    
    Returns:
        Optional[pd.DataFrame]: DataFrame of device info if to_pandas=True, None otherwise.
        
    Examples:
        >>> from nbqol import devices
        >>> # Make only first GPU visible
        >>> devices.set_cuda_visibles(0)
        >>> # Make GPUs 0 and 2 visible
        >>> devices.set_cuda_visibles(0, 2)
        >>> # Disable all GPUs (use CPU only)
        >>> devices.set_cuda_visibles()
    """
    # Collect all devices from arguments
    devices = [] # iterfill
    for _, arg in enumerate(args):
        devices += [arg] if not isinstance(arg, (list, tuple)) else arg

    if kwargs.pop('verbose', False):
        print('Visible Devices:', devices)

    # Set environment variable
    if len(devices) >= 1:
        os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(list(map(str, devices)))
    else: # set to none
        os.environ['CUDA_VISIBLE_DEVICES'] = ''
        if report is not None:
            print('Running all operations on CPU')
        return None

    # No report requested
    if report is None:
        return None

    # Generate nvidia-smi report
    if report == 'nvidia':
        return cuda_device_report(devices)
        
    # Generate PyTorch report
    if report == 'torch':
        try:
            # Import here to avoid requiring torch as a dependency
            from torch.cuda import get_device_properties
            from torch.cuda.memory import mem_get_info
            
            device_reports = [] # fill
            for index, device in enumerate(devices):
                device_reports.append(torch_device_report(index))

            if kwargs.pop('to_pandas', False):
                return pd.DataFrame(device_reports)

            for id, report in enumerate(device_reports):
                print(f"({id}) {report['GPU Name']}: {report['Total Memory']}"
                    + f" ({report['Free Memory (%)']} Free)") # 1-line report
                    
        except ImportError:
            print("PyTorch not available. Use report='nvidia' instead.")
    
    return None

# Alias for backward compatibility
cuda_visibles = set_cuda_visibles