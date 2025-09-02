# easy-subprocess
easy-subprocess is a higher-level alternative to [subprocess.Popen](https://docs.python.org/3/library/subprocess.html#subprocess.Popen) with the same level of flexibility. 
Also, easy-subprocess supports both blocking and non-blocking read operations.

# Installation
```pip install easy-subprocess```

# Api Reference
_class_ easy_subprocess.**EasyPopen**(target, text_mode = True, encoding = "utf-8", print_output = False, propagate_children = True, initial_output = False, buffer_newlines = True, no_encoding_errors = True, **kwargs)

Use a with statement to instantiate from this class. Or alternatively, don't forget to call the cleanup() method at the end.
Objects of this class create a new thread and continuously check output from the target. 
Every object has its own internal buffer. When target writes output to its stdout, this data is read by the object and written to its internal buffer.
If buffer_newlines is enabled, there will be one more buffering stage before it is written to the internal buffer.
Read methods of this class will read from the internal buffer.

_target_ is a str specifying cmd/bash command or name of a program. This is actually the "args" parameter of subprocess.Popen(). Note that shell is always enabled.

_text_mode_ is a boolean specifying how to communicate with the process. 
If it's True, encoding argument must be a valid character encoding. If it's False input and output is not encoded/decoded.
If it's True, read methods return strings. If it's False, read methods return bytes. 

_encoding_ is a string specifying how to encode/decode data when communicating with process. Has no effect when text_mode = False. 
Input is encoded with encoding before being sent to process by send_input() method and output is decoded with encoding before being returned by one of the read methods.

_buffer_newlines_ is a boolean specifying whether or not to buffer operating system's newline characters in order to standardize a potential newline when reading the process' standard output.
Has no effect when text_mode = False.

_print_output_ is a boolean specifying whether or not to immediately print the output received from the process.
If it's True, enable_output_printing() method will be called. But there is one more thing this parameter does:
Context manager will wait a bit more before exiting in order to receive any output left.

_propagate_children_ is a boolean specifying whether or not to propagate the kill signal to the children of the process (recursively).
Note that the subprocess is actually the shell process (like cmd.exe) and not the target itself. target is actually a child of the shell process. 
Because of that, if this argument is False, target wont't be killed. Only the shell process. 
If this argument is True, the whole process tree whose nodes include shell process, target and all child processes of target will be destroyed except the root node (main script) when the context manager exits. 
Even a corrupted process tree can be destroyed successfully. 
Imagine this scenario: processA --> processB --> processC --> processD --> processE. 
Let's say processC  somehow died. That means processD and processE are no more part of the process tree. 
But still, these 2 processes can be and will be terminated by the context manager. Because the whole process tree is regularly monitored and all children are recorded. 

_initial_output_ is a boolean specifying whether or not to wait for the process to write the first bytes to its stdout. 
You can pass False to this, but waiting initially makes us sure the process is ready for interaction.
Nevertheless, not every program shows an initial output. That's why it's set to False by default.

_no_encoding_errors_ is a boolean specifying whether or not to suppress encoding errors by replacing the faulty bytes with "�"
Has no effect when text_mode = False.

**_kwargs_ will be passed to subprocess.Popen()

## EasyPopen Objects
All read data will be added on _read_data_ member before being returned by one of the read methods.
If text_mode is True, _read_data_ is of str type. If text_mode is False, _read_data_ is of bytes type.

EasyPopen.**read_output**()

Basic non-blocking read of the process's standard output. 
Return all available unread data right now. It can be 0 to indefinite number of bytes/characters.

EasyPopen.**send_input**(data, terminator = "\n")

Send _data_ to the standard input stream of the process. If text_mode is True, _terminator_ is automatically added to the _data_. 
If text_mode is True, _data_ is expected to be a str type. If text_mode is False, _data_ is expected to be a bytes type.

EasyPopen.**get_output**()

Basic blocking read. Return 1 to indefinite number of bytes/characters.
If no unread data is available right now, wait until some new data arrives.

EasyPopen.**try_reading_exactly**(n)

Non-blocking read. Return _n_ bytes/characters if possible. If enough data is not available, return all available data.

EasyPopen.**read_exactly**(n)

Blocking read. Return _n_ bytes/characters.
If enough unread data is not available right now, wait until enough data arrives.

EasyPopen.**try_reading_until**(seperator = "\n")

Non-blocking read. Read till the _seperator_ if possible. If _seperator_ is not found in currently available data, return all available data.

EasyPopen.**read_until**(seperator = "\n")

Blocking read. Read until the _seperator_ is found. Return value includes the _seperator_.
If _seperator_ is not found in currently available data, wait until _seperator_ arrives.

EasyPopen.**enable_output_printing**()

print process' output to main script's console real-time. This method internally calls the redirect_output() method.

EasyPopen.**disable_output_printing**()

disable output printing if enabled.

EasyPopen.**redirect_output**(file = sys.stdout, write_history = False, close_file = True)

Write the output to a given _file_ real-time (in addition to the internal buffer). Useful for logging purposes.
_file_ doesn't have to be a disk file, it can be any file-like object.
It is possible to simultaneously redirect the output to multiple files by calling this method with different file arguments.
If _write_history_ is False, previously received data won't be written to the file. 
Received means received by the internal buffer. Even if some data is unread yet but already stored in internal buffer, they won't be written to the file.
If _close_file_ is True, _file_ will be closed automatically when redirection is stopped.
Returns an int that can be passed to stop_redirecting() method.

EasyPopen.**stop_redirecting**(redirector_id)

Stop the redirector owning _redirector_id_ from redirecting anymore.

EasyPopen.**check_unread_data**()

Return True if any data in the internal buffer is yet to be read. Return False if no unread data is available.

EasyPopen.**wait_new_data**(wait = 0.5)

Wait for given amount of seconds for new output from the process to be written to the internal buffer. Pass -1 to disable timeout. Returns True unless timeout.

EasyPopen.**wait_unread_data**(wait = 0.5)

If not any unread data is available, wait until some new data to be written to the internal buffer in given amount of seconds. Pass -1 to disable timeout. Return True unless timeout.

EasyPopen.**wait_incoming_data**(interval = 0.5)

Keep waiting as long as some new data is written to the internal buffer at least once every _interval_ seconds. 

EasyPopen.**keep_read_output**(interval = 0.5)

Call EasyPopen.read_output() method once every _interval_ seconds if some new data became available meanwhile. Concatenate the data returned from each call. 
If no data arrives in _interval_ seconds, return all of the collected data.

EasyPopen.**keep_try_reading_until**(seperator = "\n", interval = 0.5)

Call EasyPopen.try_reading_until() once every _interval_ seconds if some new data became available meanwhile and seperator is not found yet. Concatenate the data returned from each call. 
If no data arrives in _interval_ seconds or seperator is found, return all of the collected data.

EasyPopen.**send_signal**(signal)

If _propagate_children_ is True, send the _signal_ to each node in the process tree except main script. If _propagate_children_ is False, only send the _signal_ to the original subprocess.

EasyPopen.**terminate**()

If _propagate_children_ is True, terminate each node in the process tree except main script. If _propagate_children_ is False, only terminate the original subprocess.
On POSIX operating systems, termination is done by sending SIGTERM signal. On Windows, Win32 API function TerminateProcess() is called.

EasyPopen.**kill**()

If _propagate_children_ is True, kill each node in the process tree except main script. If _propagate_children_ is False, only kill the original subprocess.
On POSIX operating systems, SIGKILL is sent to the process. On Windows, kill() is an alias for terminate() method.

EasyPopen.**cleanup**()

This is called by \_\_exit__() routine of the context manager. If you aren't using a with statement, you should call this when you are done with the object.
If _print_output_ is True, wait a bit more before exiting in order to receive any output left. Then, stop all output redirectors. Lastly call the terminate() method.

## Utils
_function_ easy_subprocess.**standardize_newlines**(datastr)

Even if you pass False to _buffer_newlines_ when instantiating from EasyPopen, you can still use this function to fix line endings yourself.
All operating system specific newlines in _datastr_ will be replaced with "\n" and this new version of _datastr_ will be returned.
_datastr_ should be a str type.






















