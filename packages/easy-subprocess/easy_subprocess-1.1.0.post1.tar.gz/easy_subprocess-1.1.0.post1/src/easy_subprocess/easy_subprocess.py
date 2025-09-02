import subprocess
import threading
import os
import time
import psutil
import sys
import io


class StdoutClosedError(Exception):
    pass


class ArgumentError(Exception):
    pass

        
class IStreamReader:
    def __init__(self):
        self._r, self._w = os.pipe() # takes all inputs. self.input = public pipe in.

    def __del__(self):
        os.close(self._w)
        try:
            del self._w
            del self._r
        except:
            pass        

    @property
    def input(self):
        """This is a file descriptor (not a file-like).
        It's the input end of our pipe which you give to other process
        to be used as stdout pipe for that process"""
        return self._w

    def get_byte():
        byte = os.read(self._r, 1)
        return byte

    
class NonBlockingReader(threading.Thread):
    """
    Heavily modified version of InputStreamChunker: https://stackoverflow.com/questions/3076542/how-can-i-read-all-availably-data-from-subprocess-popen-stdout-non-blocking
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    Threaded object / code that mediates reading output from a stream.

    Results can be accessed by calling one of the read methods.
    Results can be read either "asynchronously" or "synchronously" by calling the appropriate methods.
         
    License: Public domain
    Absolutely no warranty provided
    """

    ################ Reader base below
    
    def __init__(self, blocking_reader, text_mode = True, encoding = "utf-8", buffer_newlines = True, redirect_to = None, encoding_errors = "strict"):
        self.debug_log = []
        super().__init__()

        self.encoding = encoding
        self.encoding_errors = encoding_errors
        self.text_mode = text_mode
        if self.text_mode == False:
            self.encoding = None
        if text_mode == True and (not self.encoding or self.encoding == ""):
            raise ArgumentError("encoding must be specified when text_mode is True. You can also switch to binary mode by passing False to text_mode parameter")
        if self.text_mode:
            self.read_data = ""
        else:
            self.read_data = b""
        self.buffer_newlines = buffer_newlines
        if self.text_mode == False:
            self.buffer_newlines = False

        #A list of bytes captured so far. This is a "stack" of sorts. Code consuming the bytes would be responsible for disposing of the bytes.
        #However, current implementation doesn't delete the bytes after they are read.
        self._data = []
        
        self.blocking_read = blocking_reader.get_byte
        self._stop = False        
        self._data_index = 0
        self._read_bytes = 0
        self._redirectors = []
        self._stop_redirection = threading.Event()
        self._not_redirecting = threading.Event()
        self._not_redirecting.set()
        self._id = 0
        self._id_counter = 0                
        self._redirector_map = {}
        self._data_available = threading.Event()
        self._data_needed = threading.Event()
        
        if redirect_to != None:
            self.redirect_output(redirect_to)        

    def __del__(self):
        try:
            self.stop()
            for redirector in self._redirectors:
                del redirector            
        except:
            pass
        try:
            del self._data
        except:
            pass

    def run(self):
        """ Plan:  
        - We read into a "data" array
          and signal the calling code (through threading.Event flag) that
          some data is available
        - repeat until .stop() was called on the thread.
        """        
        newline = os.linesep
        newline_buffer = []
        while not self._stop:
            if self.buffer_newlines == True and self.text_mode == True: 
                while True:
                    byte = self.blocking_read()
                    char = byte.decode(self.encoding, errors = self.encoding_errors)                    
                    if char == os.linesep[len(newline_buffer)]:
                        newline_buffer.append(char)
                        if len(newline_buffer) == len(os.linesep):
                            self.write_data(b"\n")
                            for redirector in self._redirectors:
                                redirector.write_data(b"\n")                                
                            newline_buffer = []
                            break
                    elif len(newline_buffer) != 0:
                        if byte == b"":
                            continue
                        newline_buffer.append(char)
                        for char in newline_buffer:
                            byte = bytes(char, self.encoding, errors = self.encoding_errors)
                            self.write_data(byte)
                            for redirector in self._redirectors:
                                redirector.write_data(byte)
                        newline_buffer = []
                        break
                    else:
                        self.write_data(byte)
                        for redirector in self._redirectors:
                            redirector.write_data(byte)
                        break
            else:
                byte = self.blocking_read()                
                self.write_data(byte)
                for redirector in self._redirectors:
                    redirector.write_data(byte)
            
    def stop(self):
        if self._stop == False:
            for redirector in list(self._redirectors):
                self.stop_redirecting(redirector._id)
                redirector.stop()
            self._stop = True
        
    def write_data(self, byte):
        self._data.append(byte)
        if self._data_needed.is_set():
            self._data_available.set()

    def wait_data(self, wait = -1):
        if wait <= 0.1 and wait != -1:
            self._data_needed.set()
            self._data_available.wait(wait)
            self._data_needed.clear()
            self._data_available.clear()
        else:
            duration = 0
            while True:
                self._data_needed.set()
                self._data_available.wait(0.1)                
                duration += 0.1
                if self._data_available.is_set():
                    self._data_needed.clear()
                    self._data_available.clear()
                    break
                if duration >= wait and wait != -1 :
                    break
                if self._stop_redirection.is_set():
                    break
        
    def get_byte(self):
        if self._data_index < len(self._data):            
            current_index = self._data_index
            self._data_index = self._data_index + 1
            return self._data[current_index]

    def get_bytes(self):
        bytestr = b""
        while True:
            byte = self.get_byte()
            if byte != None:
                bytestr = bytestr + byte
            else:
                break
        return bytestr

    def _try_reading_until(self, seperator = "\n", data = None, seperator_buffer = []):
        seperator_buffer = list(seperator_buffer)
        if self.text_mode and type(seperator) == bytes:    
            raise ArgumentError("'seperator' argument must be of type str or the object should be initialised with the text_mode parameter set to False")
        if type(seperator) == str and data == None:
            data = ""
        elif data == None:
            data = b""
        
        found_seperator = False           
        while True:
            char = self.try_reading_exactly(1)
            if len(char) == 0:
                for char in seperator_buffer:
                    data = data + char                
                return [data, seperator_buffer]
            if char == seperator[len(seperator_buffer)]:
                seperator_buffer.append(char)                
                if len(seperator_buffer) == len(seperator):
                    found_seperator = True
                    for char in seperator_buffer:
                        data = data + char                    
                    break                
            elif len(seperator_buffer) != 0:
                seperator_buffer.append(char)
                for char in seperator_buffer:
                    data = data + char
                seperator_buffer = []
            else:
                data = data + char        
        return data

    def write_file(self, file, close_file):
        self._not_redirecting.clear()
        self.file = file
        while True:
            data = self.read_output()
            if self._stop_redirection.is_set():
                if close_file:
                    def write_handler(data):
                        raise StdoutClosedError("Can not print data. Stdout is closed because redirect_output() is called with close_file = True. Please pass False to this parameter in order to solve this problem.")
                    if file == sys.stdout:
                        file.write = write_handler                    
                    file.close()
                self._not_redirecting.set()
                break
            if len(data) != 0:
                file.write(data)
            self.wait_unread_data(-1)

    ################ essential public api below
    
    def read_output(self):
        """Basic non-blocking read. Return 0 to indefinite number of bytes/characters."""
        output = self.get_bytes()
        if self.text_mode:
            output = output.decode(self.encoding, errors = self.encoding_errors) 
        self._read_bytes += 1
        self.read_data = self.read_data + output
        return output

    def get_output(self):
        """Basic blocking read. Return 1 to indefinite number of bytes/characters."""
        while True:                
            data = self.read_output()
            if data != "" and data != b"":
                break
            self.wait_unread_data(-1)
        return data

    def try_reading_exactly(self, n):
        """Non-blocking read. Read up to n bytes/characters."""
        bytestr = b""           
        while True:
            byte = self.get_byte()
            if byte != None and len(bytestr) < n:
                bytestr = bytestr + byte
            elif byte != None:
                self._data_index = self._data_index - 1
                break
            else:
                break            
        output = bytestr
        if self.text_mode:
            output = output.decode(self.encoding, errors = self.encoding_errors)                
        self._read_bytes += 1
        self.read_data = self.read_data + output
        return output        

    def read_exactly(self, n):
        """Blocking read. Read n bytes/characters."""
        data = ""
        left_len = n
        while True:            
            output = self.try_reading_exactly(left_len)            
            data = data + output
            left_len = left_len - len(output)
            if len(data) == n:
                break
            self.wait_unread_data(-1)
        return data

    def try_reading_until(self, seperator = "\n"):
        """Non-blocking read. Read till the seperator if possible."""
        return_val = self._try_reading_until(seperator = seperator)
        if type(return_val) == list:
            data = return_val[0]
        else:
            data = return_val
        return data     
        
    def read_until(self, seperator = "\n"):
        """Blocking read. Read until the seperator is found."""
        if type(seperator) == str:
            data = ""
        else:
            data = b""        
        seperator_buffer = []          
        while True:
            return_val = self._try_reading_until(seperator = seperator, data = data, seperator_buffer = seperator_buffer)
            if type(return_val) == list:
                data = return_val[0]
                seperator_buffer = return_val[1]
            else:
                data = return_val
                break
            self.wait_unread_data(-1)           
        return data

    ################ Helper functions below
    
    def stop_redirecting(self, redirector_id):
        """Stop the redirector owning redirector_id from redirecting anymore."""
        reader = self._redirector_map[redirector_id]
        if reader._not_redirecting.is_set() == False:
            reader._stop_redirection.set()            
            if reader._not_redirecting.wait():
                reader._stop_redirection.clear()
            for redirector in self._redirectors:
                if redirector._id == redirector_id:
                    self._redirectors.remove(redirector)
            del self._redirector_map[redirector_id]
        
    def redirect_output(self, file = sys.stdout, write_history = False, close_file = True):
        """Write the output to a given file real-time. This doesn't affect the way other methods function.
        Useful for real-time output printing."""
        if not self.text_mode and isinstance(file, io.TextIOBase):
            raise ArgumentError("Given file argument is a text stream but this instance of NonBlockingReader uses binary data. Either use a binary stream or pass text_mode = True to NonBlockingReader")
        fake_reader = IStreamReader()
        reader = NonBlockingReader(fake_reader, text_mode = self.text_mode, encoding = self.encoding, buffer_newlines = self.buffer_newlines, encoding_errors = self.encoding_errors)
        self._redirectors.append(reader)
        self._id_counter += 1
        reader._id = self._id_counter
        self._redirector_map[reader._id] = reader
        if write_history:
            current_index = self._data_index
            self._data_index = 0
            old_data = self.read_exactly(current_index)
            file.write(old_data)
            self._data_index = current_index        
        t = threading.Thread(target = reader.write_file, args = (file, close_file))
        t.start()
        return reader._id
        
    def enable_output_printing(self):
        for redirector in self._redirectors:
            if redirector.file == sys.stdout:
                return
        redirector_id = self.redirect_output(file = sys.stdout, write_history = True, close_file = False)
        return redirector_id

    def disable_output_printing(self):
        for redirector in list(self._redirectors):
            if redirector.file == sys.stdout:
                self.stop_redirecting(redirector._id)

    def check_unread_data(self):
        """Checks whether or not any data in the internal buffer (._data) is yet to be read"""
        if self._read_bytes < len(self._data):
            return True
        else:
            return False

    def wait_new_data(self, wait = 0.5):
        """Wait for given amount of seconds for new output from the subprocess to be written to the internal buffer.
        Return True unless timeout"""
        current_size = len(self._data)
        self.wait_data(wait)
        new_size = len(self._data)
        if new_size > current_size:
            return True
        else:
            return False

    def wait_unread_data(self, wait = 0.5):
        """If not any unread data is available, wait until some new data to be written to the internal buffer in given amount of seconds.
        Return True unless timeout."""
        if self.check_unread_data():
            return True
        return self.wait_new_data(wait)

    def wait_incoming_data(self, interval = 0.5):
        """Keep waiting as long as some new data is written to the internal buffer at least once every "interval" seconds.
        Useful for waiting the redirected output."""
        while self.wait_new_data(interval):
            pass

    def keep_read_output(self, interval = 0.5):
        """Call read_output() once every "interval" seconds if some new data became available meanwhile.
        Return if no data arrives in "interval" seconds."""
        data = self.read_output() 
        while self.wait_unread_data(interval):
            data = data + self.read_output()
        return data

    def keep_try_reading_until(self, seperator = "\n", interval = 0.5):
        """Call try_reading_until() once every "interval" seconds if some new data became available meanwhile.
        Return if no data arrives in "interval" seconds."""
        data = self.try_reading_until(seperator = seperator)
        if seperator in data:
            return data
        while self.wait_unread_data(interval):
            data = data + self.try_reading_until(seperator = seperator)
            if seperator in data:
                return data
        return data
        
                                
class EasyPopen(NonBlockingReader):
    """Use a with statement to instantiate from this class.
    Or alternatively, don't forget to call the cleanup() method at the end.
    
    Not doing this can cause your cpu to go 100% and make your computer slow.
    If this happens, you can simply restart you computer and the problem will be fixed.
    If restarting the whole PC sounds too annoying, you can do this instead:
    open up cmd and kill the program you opened with EasyPopen.
    For example, if you did EasyPopen("program.exe"), type in cmd "taskkill /f /im program.exe"
    Don't use the task manager. The task MAY be invisible in task manager.
    
    As long as you wrap the EasyPopen() call by using "with" keyword, you won't have such headaches.
    ...unless you forcefully kill the main script. This will bypass __exit__() routine of the context manager.
    
    Constructor Interface
    ----------------------
    target: this is the "args" parameter of subprocess.Popen(). But it must be a str. Not a list. shell is always enabled.
    text_mode: Boolean specifying how to communicate with the process
    encoding: specifies how to encode/decode binary data when communicating with process. Only meaningful when text_mode = True
    buffer_newlines: Boolean specifying whether or not to buffer OS's newline characters in order to standardize a potential newline when reading the process stdout.
                     Only meaningful when text_mode = True
    print_output: Boolean specifying whether or not to immediately print the output received from the process.
                  Context manager will wait a bit more before exiting in order to receive any output left.
    propagate_children: Boolean specifying whether or not to propagate the kill signal to the children of the process (recursively).
                        Note that the subprocess is actually the shell process and not the target itself. 
    initial_output: Boolean specifying whether or not to wait for the process to write the first bytes to its stdout. 
                    You can pass False to this, but waiting initially makes us sure the process is ready for interaction.
                    Nevertheless, not every program shows an initial output. That's why it's set to False by default.
    no_encoding_errors: Boolean specifying whether or not to suppress encoding errors by replacing the faulty bytes with "�"
    **kwargs: Other keyword arguments which will be passed to subprocess.Popen()
    """
    
    def __init__(self, target, text_mode = True, encoding = "utf-8", print_output = False, propagate_children = True, initial_output = False, buffer_newlines = True, no_encoding_errors = True, **kwargs):
        default_kwargs = {"shell":True, "bufsize":0, "universal_newlines":False, "stdin":subprocess.PIPE, "stdout":subprocess.PIPE, "stderr":subprocess.STDOUT}
        for default_key in dict(default_kwargs):
            if default_key in kwargs:
                del default_kwargs[default_key]
        if no_encoding_errors:
            error_handler = "replace"
        else:
            error_handler = "strict"
        blocking_reader = self.BlockingReader(self)
        super().__init__(blocking_reader, text_mode = text_mode, encoding = encoding, buffer_newlines = buffer_newlines, encoding_errors = error_handler)
        self.print_output = print_output
        if print_output == True:
            self.enable_output_printing()        
        self.daemon = True
        self._process = subprocess.Popen(target, **default_kwargs, **kwargs)
        self.children = []
        self.end_process = threading.Event()
        self.propagate_children = propagate_children
        if self.propagate_children:
            self.timer = threading.Timer(0.1, self.track_children)
            self.timer.start()        
        self.start()
        if initial_output:
            self.wait_unread_data(wait = -1)
            
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

    def __del__(self):
        if self.end_process.is_set() == False:
            self.terminate() # in case main process gets killed before cleanup is completed
            self.cleanup()

    class BlockingReader:
        def __init__(self, outer_self):
            self.outer_self = outer_self
            
        def get_byte(self):
            return self.outer_self._process.stdout.read(1)
        
    def capture_children(self):
        try:
            current_children = psutil.Process(self._process.pid).children(recursive=True)
        except psutil.NoSuchProcess:
            return
        for child in current_children:
            if not (child in self.children):
                self.children.append(child)
        
    def track_children(self):
        if self.end_process.is_set() == False:
            self.capture_children()
            self.timer = threading.Timer(0.1, self.track_children)
            self.timer.start()

    def stop_tracking(self):        
        if self.propagate_children:
            self.capture_children()                    
            self.timer.cancel()
            if self.timer.is_alive():
                self.timer.join()
                self.timer.cancel()
        
    ################ public api below
            
    def send_signal(self, signal):
        self.stop_tracking()
        for child in self.children:
            try:
                child.send_signal(signal)
            except psutil.NoSuchProcess:
                pass        
        self._process.send_signal(signal)        

    def terminate(self):
        self.stop_tracking()
        for child in self.children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass        
        self._process.terminate()        

    def kill(self):
        self.stop_tracking()
        for child in self.children:
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass        
        self._process.kill()        
            
    def cleanup(self):
        self.end_process.set()
        if self.print_output:
            self.wait_incoming_data()        
        self.stop()
        self.terminate()
        del self._process
        
    def send_input(self, data, terminator = "\n"):
        if self.end_process.is_set() == False:            
            if self.text_mode:
                data = data + terminator
                data = bytes(data, self.encoding, errors = self.encoding_errors)
            self._process.stdin.write(data)
        else:
            raise RuntimeError("process has been stopped")


def standardize_newlines(self, datastr):
    """If you pass buffer_newlines = False, you can still use this function to fix line endings yourself."""
    lines = datastr.split(os.linesep)
    datastr = "\n".join(lines)
    return datastr
