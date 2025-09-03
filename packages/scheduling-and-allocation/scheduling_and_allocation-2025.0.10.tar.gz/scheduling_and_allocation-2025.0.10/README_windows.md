## Windows

### Python Installation

Go to [python site](https://www.python.org/) and navigate to the `Downloads` page

<img src="./document_images/python_download.png" alt="image-20250823111349808" style="zoom:33%;" />

Follow instructions for standard install

* Select admin privileges if you have them, 
* Select `add Python to path`
* **PAY VERY CLOSE ATTENTION TO WHERE IT IS INSTALLED!!**

<img src="./document_images/python_install.png" style="zoom:50%;" />



### Validation

Open a `cmd` window (got to windows search bar and type `cmd`)

<img src="./document_images/python_command_prompt.png" style="zoom:33%;" />

In the command window, type `where python`

<img src="./document_images/python_verify_version.png" style="zoom:50%;" />

The first version of python should be the one you just installed.  

If the above does not show the version of python that you installed, modify the path by...

* Open a `cmd` window

* Type `setx PATH "c:\Users\SandyLocal\AppData\Local\Programs\Python\Python313\python.exe;%PATH%"` 

  **but** use the location where *you* saved the the `python.exe` file.

Validate again.

> NOTE: if the above doesn't work, all is not lost, but the easiest method is to ask your administrator to adjust the PATH environment variables on your computer to point to the correct location of python

## Application Installation

Open a `cmd` window (got to windows search bar and type `cmd`)

Type the following in the command window

```bash
python -m pip install scheduling_and_allocation
```
```commandline
C:\>python -m pip install scheduling_and_allocation
Defaulting to user installation because normal site-packages is not writeable
Collecting scheduling_and_allocation
  Downloading scheduling_and_allocation-2025.0.8-py3-none-any.whl.metadata (1.2 kB)
Requirement already satisfied: pillow>=11.3.0 in c:\users\sandy\appdata\local\packages\pythonsoftwarefoundation.python.3.13_qbz5n2kfra8p0\localcache\local-packages\python313\site-packages (from scheduling_and_allocation) (11.3.0)
Requirement already satisfied: reportlab>=4.4.3 in c:\users\sandy\appdata\local\packages\pythonsoftwarefoundation.python.3.13_qbz5n2kfra8p0\localcache\local-packages\python313\site-packages (from scheduling_and_allocation) (4.4.3)
Requirement already satisfied: charset-normalizer in c:\users\sandy\appdata\local\packages\pythonsoftwarefoundation.python.3.13_qbz5n2kfra8p0\localcache\local-packages\python313\site-packages (from reportlab>=4.4.3->scheduling_and_allocation) (3.4.2)
Downloading scheduling_and_allocation-2025.0.8-py3-none-any.whl (554 kB)
   ---------------------------------------- 554.3/554.3 kB 11.0 MB/s  0:00:00
Installing collected packages: scheduling_and_allocation
  WARNING: The scripts Allocation.exe and Scheduler.exe are installed in 'C:\Users\Sandy\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts' which is not on PATH.
  Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
Successfully installed scheduling_and_allocation-2025.0.8

```
## Running the program(s)

Open a `cmd` window (got to windows search bar and type `cmd`)

Type the following in the command window

```bash
Scheduler
```

or

```python
Allocation
```

