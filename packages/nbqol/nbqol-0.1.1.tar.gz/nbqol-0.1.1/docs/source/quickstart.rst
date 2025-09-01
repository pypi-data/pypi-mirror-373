Quickstart
==========

NB-QOL provides various utilities to enhance your Jupyter notebook workflow. Here are some common use cases:

CUDA Device Management
-------------------------

Check and manage your CUDA devices:

.. code-block:: python

   from nbqol import devices
   
   # List all available CUDA devices
   devices.cuda_device_report()
   
   # Select specific CUDA devices to use
   devices.set_cuda_visibles(0, 1)  # Use CUDA devices 0 and 1

IPython Configuration
------------------------

Configure IPython environment:

.. code-block:: python

   import nbqol
   
   # Enable autoreload to automatically reload modules during development
   nbqol.set_autoreload('complete')
   
   # Hide warning messages
   nbqol.hide_warnings()
   
   # Get environment settings
   env_settings = nbqol.get_main_env_settings()
   
   # Alternative: use the options module directly
   from nbqol import options
   options.set_autoreload('complete')

Path Operations
----------------

Work with notebook paths:

.. code-block:: python

   import nbqol
   
   # Get the path of the current notebook
   nb_path = nbqol.notebook_path()
   
   # Find the Git repository root
   git_root = nbqol.path_to_git_root()
   
   # Add git root to Python path
   nbqol.add_git_root_to_sys_path()
   
   # Alternative: use the env module directly
   from nbqol import env
   nb_path = env.notebook_path()

Styling Notebooks
-------------------

Apply CSS styling to your notebooks:

.. code-block:: python

   import nbqol
   
   # Auto-detect environment and apply appropriate styling
   nbqol.auto_style()
   
   # Alternative: use the stylizer module directly
   from nbqol import stylizer
   stylizer.auto_style()
   
   # Load specific VSCode styles
   from nbqol.styles import load_vscode_styles
   load_vscode_styles()

Notebook Conversion
---------------------

Convert notebooks to different formats or clean them up:

.. code-block:: python

   import nbqol
   
   # Convert notebook to VSCode-compatible Python script
   nbqol.convert_to_vscode_script('my_notebook.ipynb', 'my_script.py')
   
   # Clean a notebook by removing intermediates and large outputs
   nbqol.clean_notebook('my_notebook.ipynb', remove_intermediates=True, remove_large_outputs=True)
   
   # Convert notebook with customized options
   nbqol.convert_notebook('my_notebook.ipynb', to_format='html', 
                         clean_options={'remove_markdown': True})
   
   # Alternative: use the process module directly
   from nbqol.process import reformat
   reformat.convert_to_vscode_script('my_notebook.ipynb', 'my_script.py')

Notebook Analysis
------------------

Analyze, execute, and verify notebooks:

.. code-block:: python

   import nbqol
   
   # Execute a notebook and save the result
   nbqol.execute_notebook('my_notebook.ipynb', 'executed_notebook.ipynb')
   
   # Check if a notebook runs without errors
   success, message = nbqol.check_notebook_runs('my_notebook.ipynb')
   
   # Verify that certain variables exist in the notebook
   results = nbqol.verify_notebook_variables('my_notebook.ipynb', ['df', 'model'])
   
   # Analyze cell dependencies in a notebook
   dependencies = nbqol.notebook_cell_dependencies('my_notebook.ipynb')
   
   # Compare two notebooks
   differences = nbqol.compare_notebooks('notebook1.ipynb', 'notebook2.ipynb')
   
   # Alternative: use the process module directly
   from nbqol.process import analyze
   analyze.execute_notebook('my_notebook.ipynb', 'executed_notebook.ipynb')

Output Capture
--------------

Capture and manage output streams:

.. code-block:: python

   import nbqol
   
   # Capture output from code execution
   with nbqol.capture_output() as captured:
       print("This will be captured")
       import logging
       logging.warning("This warning will also be captured")
   
   print("Captured stdout:", captured.stdout)
   print("Captured stderr:", captured.stderr)
   print("Captured logs:", captured.logs)
   
   # Alternative: use the outputs module directly
   from nbqol.outputs import capture_output
   with capture_output() as captured:
       print("Alternative capture method")