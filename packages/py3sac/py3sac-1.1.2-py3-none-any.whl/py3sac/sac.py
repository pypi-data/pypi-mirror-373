"""
This module is an interface for SAC related operations.
"""

from os.path import os, dirname, basename
from posix import remove, getcwd
import re
import subprocess
from tempfile import gettempdir

from py3sacio.py3sacio import SacFile
from pyutils.dep import check_executable
from pyutils.fs import remove_files
from pyutils.nmath import get_locmaxs, get_globmax,calc_moving_average_list
from pyutils.tuple_file import file2tuples


class Sac(object):
    '''
    Represents a SAC execution instance.
    Ad-hoc class, not fully implementing SAC bindings.
    It maintains a queue of commands to execute.
    To queue a raw command you may call add_cmd().
    But rather use auto-formatting methods to enqueue a command (e.g. read() for READ command).
    '''

    # TODO: argument checking and SacException on error

    def __init__(self):
        '''
        Constructor
        '''
        self.cmds = []
        self.process = None

    def color(self, on=True, increment=False, inc_list=None):
        """
        Adds a COLOR SAC command to the queue.
        on: bool True of False.
        inc_list: add an INCREMENT LIST 
        COLOR ON INCREMENT LIST BLACK BLUE BLACK BLACK BLACK BLUE
        """
        params = "ON" if on else "OFF"
        if increment:
            params += " INCREMENT"
        if inc_list is not None:
            str_l=" LIST"
            for s in inc_list.split():
                str_l += " "+s
            params += str_l
        self.add_cmd("color", params)
        return self

    def qdp(self, val):
        """
        Adds a QDP SAC command to the queue.
        val -- Must be "ON" or "OFF"
        """
        self.add_cmd("qdp", val)
        return self
       
    def read(self, *tracef):
        """
        Adds a READ SAC command to the queue.
        tracef -- List of SAC files to read.
        """
        files = ""
        for f in tracef:
            if(f):
                files += f + " "
        self.add_cmd("read", files)
        return self
        
    def write(self, tracef="over", *more_traces):
        """
        Adds a WRITE SAC command to the queue.
        tracef -- (optional) a file to write in. By default, the last file read will be written.
        more_traces -- (optional) List of files to write if there is more. 
        """
        params = tracef
        if(more_traces != None):
            for t in more_traces:
                if(t):
                    params += " " + t
        self.add_cmd("write", params)
        return self
    
    def title(self, title, location, size):
        """
        Adds a TITLE SAC command to the queue.
        title -- Must be str: ON, OFF or arbitrary title text.
        location -- Title location (str TOP|BOTTOM|RIGHT|LEFT) 
        size -- str TINY|SMALL|MEDIUM|LARGE
        """
        if(title not in ("ON","on","OFF","off")):
            title = '"' + title + '"'
        self.add_cmd(self.__format_params("title", title=title, location=location,
                                        size=size))
        return self
    
    def bandpass(self, bandpass="butter", npoles=2, passes=1, v1=0.1, v2=0.4):
        """Adds a BANDPASS SAC command to the queue.
        bandpass -- String BUTTER, BESSEL, C1 or C2.
        npoles -- Number of poles.
        passes -- Number of passes (1 or 2)
        corners v1, v2 -- Two floats v1 and v2 (corner frequencies in Hz)
        """
        self.add_cmd(self.__format_params("bandpass", bandpass=bandpass,
                                        npoles=str(npoles),
                                        passes=str(passes),
                                        corners=str(v1) + " " + str(v2)))
        return self
        
    def ppk(self, bell):
        """Adds a PPK SAC command to the queue.
        bell -- String ON of OFF.
        """
        self.add_cmd("ppk", "bell " + bell)
        return self
    
    def cut(self, start, end, start_offset=0, end_offset=0):
        """Adds a CUT SAC command to the queue.
        start -- Start time of cut in seconds or a header reference in B|E|O|A|F|T[0-9].
        end -- End time of cut in seconds or a header reference in B|E|O|A|F|T[0-9].
        start_offset -- (optional) offset time (seconds) relative to start time.
        end_offset -- (optional) offset time (seconds) relative to end time.
        """
        try:
            if(self.__is_valid_cut_ref(start)):
                start = start + " "+str(start_offset)
            else:
                start += start_offset
            if(self.__is_valid_cut_ref(end)):
                end = end + " "+str(end_offset)
            else:
                end += end_offset
        except Exception:
            raise SacException("Error: Sac.cut() invalid argument list.")
        self.add_cmd("cut", str(start) + " " + str(end))
        return self
    
    def cut_on(self):
        """Adds a CUT SAC command to the queue.
        Sets the last cut ON with the same cut times.
        """
        self.add_cmd("cut", "on")
    
    def cut_off(self):
        """Adds a CUT SAC command to the queue.
        Sets the last cut OFF.
        """
        self.add_cmd("cut", "off")
    
    def cut_points(self, start, n, offset=0):
        """Adds a CUT SAC command to the queue.
        Cuts n points from start time (one point being separated from the previous by a time defined by the sac trace delta header).
        start -- Start time of cut in seconds or a header reference in B|E|O|A|F|T[0-9].
        offset -- (optional) offset time (seconds) relative to start time.
        n -- The number of points from the start to the end cut.
        """
        try:
            if(self.__is_valid_cut_ref(start)):
                start = start + " "+str(offset)
            else:
                start += offset
            n=int(n)
        except Exception:
            raise SacException("Error: Sac.cut_points() invalid argument list.")
        self.add_cmd(self.__format_params("cut",cut=start,N=n))
        return self
    
    def rmean(self):
        """Adds a RMEAN SAC command to the queue."""
        self.add_cmd("rmean")
        return self
    
    def reverse(self):
        """Adds a REVERSE SAC command to the queue."""
        self.add_cmd("reverse")
        return self  
    
    def rtrend(self, quiet=True, verbose=False):
        """Adds a RTREND SAC command to the queue.
            quiet -- on or off str.
            verbose -- on or off str.
        """
        params = " "
        if(quiet): params += "quiet "
        if(verbose): params += "verbose" 
        self.add_cmd("rtrend", params)
        
        
    
    def div(self, *values):
        """Adds a DIV SAC command to the queue.
        values -- Values to divide files by, the first one for the first file read, the nth one for the nth file read.
        """
        val_str = ""
        for v in values:
            val_str += str(v) + " "
        self.add_cmd("div", val_str)
        return self
        
    def mul(self, *values):
        """Adds a MUL SAC command to the queue.
        values -- Values to multiply files by, the first one for the first file read, the nth one for the nth file read.
        """
        val_str = ""
        for v in values:
            val_str += str(v) + " "
        self.add_cmd("mul", val_str)
        return self

    def add(self, *values):
        """Adds a MUL SAC command to the queue.
        values -- Values to multiply files by, the first one for the first file read, the nth one for the nth file read.
        """
        val_str = ""
        for v in values:
            val_str += str(v) + " "
        self.add_cmd("add", val_str)
        return self

    def addf(self, *filelist, newhdr="off"):
        """Adds a ADDF SAC command to the queue.
        filelist -- SAC files.
        newhdr -- String ON or OFF.
        """
        filelist_str = ""
        for _file in filelist:
            filelist_str += _file + " "
        self.add_cmd("addf", self.__format_params(newhdr=newhdr) + " " + filelist_str)
        return self
            
    def rotate(self, rtype, val, polarity=None):
        """Adds a ROTATE SAC command to the queue.
        rtype -- String TO, TO GCP or THROUGH.
        val -- Angle in degrees (ignored if rtype == "TO GCP").
        polarity -- (Optional) String NORMAL or REVERSED.
        """
        if(rtype == "TO GCP" or rtype == "to gcp"):
            params = rtype
        else:
            params = rtype + " " + str(val)
        if(polarity != None):
            params += " " + polarity
        self.add_cmd("rotate", params)
        return self
        
    def rotateTo(self, val, polarity=None):
        """Adds a ROTATE TO SAC command to the queue.
        Helper calling self.rotate("TO", val, polarity)
        val -- Angle in degrees.
        polarity -- (optional) String NORMAL or REVERSED.
        """
        self.rotate("to", val, polarity)
        return self
    
    def taper(self, ttype=None, width=None):
        """Adds a TAPER SAC command to the queue.
        ttype -- String HANNING, HAMMING or COSINE.
        width -- Value between 0.0 and 0.5.
        """
        if ttype is None and width is None:
            self.add_cmd("taper")
        else:
            if not isinstance(ttype, str):
                raise ValueError('ttype must be a str')
            if not isinstance(width, float):
                raise ValueError('width must be float')
            self.add_cmd("taper", self.__format_params(type=ttype, width=str(width)))
        return self
        
    def transfer(self, from_type, to_type, freq_lims, from_options=None, to_options=None,
                 prew="off"):
        """Adds a TRANSFER SAC command to the queue.
        from_type -- String for type of deconvolution (EVALRESP... see SAC help).
        to_type -- String for type of convolution (EVALRESP... see SAC help).
        freq_lims -- List of f1, f2, f3, f4 frequency numbers.
        from_options -- (Optional) Dictionary of options for deconvolution (e.g. {fname: "my_resp_file_path"}). 
        to_options -- (Optional)  Dictionary of options for convolution.
        """
        params = {}
        params["from"] = from_type + " "
        if(from_options != None):
            for k in from_options:
                params["from"] += str(k) + "  " + from_options[k]
        params["to"] = to_type
        if(to_options != None):
            for k in to_options:
                params["to"] += str(k) + "  " + to_options[k]
        params["to"] += " freq "    
        for f in freq_lims:
            params["to"] += str(f) + " "
        params["to"] += " prew " + prew
        self.add_cmd("transfer", self.__format_params("from", **params))
        return self

    def decimate(self, n, dfilter="on"):
        """Adds a DECIMATE SAC command to the queue.
        n -- Factor of decimation (integer in range 2 to 7).
        dfilter -- String ON or OFF.
        """
        self.add_cmd(self.__format_params("decimate", decimate=str(n), filter=dfilter))
        return self

    def chnhdr(self, files=None, **fields):
        """Adds a CHNHDR SAC command to the queue.
        files -- (Optional) List of integers indicating the file headers to be changed.
        fields -- Unpacked dictionary of fields and values (e.g. sac.chnhdr(T1=2) to edit field T1).
        """
        params = self.__format_params_cmd_less(**fields)
        if(files):
            params = "file ".join(files)+" "+params
        self.add_cmd("chnhdr", params)
        return self

    def writehdr(self, type='commit'):
        """Adds a WRITEHDR SAC command to the queue.

        Args:
            type: (str)
                The type of save (see SAC doc).
        """
        self.add_cmd("writehdr", type)
        return self

    def envelope(self):
        """Adds an ENVELOPE SAC command to the queue."""
        self.add_cmd("envelope")
        return self
        
    def quit(self):
        """Adds a QUIT SAC command to the queue."""
        self.add_cmd("quit")
        return self
    
    def add_cmd(self, cmd, params=None):
        """
        Adds a SAC command to the command queue.
        Prefer auto-formatting methods if available for the command to add.
        cmd -- The SAC command.
        params -- The SAC command parameters.
        """
        if(params != None): 
            cmd += " " + params
        self.cmds.append(cmd)
        return self
    
    def print_cmds(self):
        """Prints all SAC commands in queue."""
        print("SAC> "+("\nSAC> ".join(self.cmds)))
        return self
    
    def exec_cmd(self, cmd, auto_quit=True):
        """
        Executes a single SAC command.
        N.B.: this method doesn't detect SAC errors like exec() does.
        """
        self.__init_process()
        self.process.stdin.write(cmd + "\n")
        if(auto_quit and cmd != "quit"):
            self.process.stdin.write("quit\n")

        
        
    def exec(self, forget_cmds=True, echo=False):
        """Executes all SAC commands formatted before on this Sac object.
        If a SAC error occurs, a SACException will be threw after execution of the whole SAC command queue.
        forget_cmds -- if True commands are erased from this instance after execution.
        echo -- if True the SAC commands are printed on standard output on execution.
        """
        self.__init_process()
        #if(echo): self.exec_cmd("echo ON commands")
        self.__init_transcript_file()
        for cmd in self.cmds:
            if(echo): print("SAC> "+cmd)
            self.exec_cmd(cmd, auto_quit=False)
        self.__close_transcript_file()
        self.process.stdin.close()
        if(forget_cmds):
            self.cmds = []
        exit_status = self.process.wait()
#         self.process.stdout.close()
        self.__find_error()
        self.process = None
        return exit_status   

    def __init_process(self):
        """
        Private method not meant to be used externally.
        Initializes SAC session process. 
        """
        if(self.process == None):
            check_executable("sac")
            self.process = subprocess.Popen(["sac"], stdin=subprocess.PIPE
#                                                 , stdout=subprocess.PIPE
                                                , universal_newlines=True)
#             for i in range(0,3):
#                 self.process.stdout.readline()   
            

    def __format_params(self, cmd_name=None, **params):
        """Formatting private helper."""
        cmd = ""
        if(cmd_name != None):
            cmd = cmd_name + " " + str(params[cmd_name]) + " "
        for key in [key for key in params.keys() if key != cmd_name]:
            cmd += key + " " + str(params[key]) + " "
        return cmd
     
    def __format_params_cmd_less(self, **params):
        """Formatting private helper."""
        return self.__format_params(None, **params)
    
    def __init_transcript_file(self):
        """
        Private method not meant to be used externally.
        Sends SAC transcript file start command. 
        """
        self.transcript_fpath = gettempdir() + os.sep + basename(getcwd()) +"_sac_transcript"
        self.process.stdin.write("transcript create file "+self.transcript_fpath+"\n")
    
    def __close_transcript_file(self):
        """
        Private method not meant to be used externally.
        Sends SAC transcript file end command. 
        """
        self.process.stdin.write("transcript close file "+self.transcript_fpath+"\n")
    
    def __find_error(self):
        """
        Private method not meant to be used externally.
        Finds SAC error in last transcript file if there is any.
        """
        lines = []
        last_line = "START"
        # search for error, if found raise SacException with command and its error
        with open(self.transcript_fpath, "r") as fd:
            while(last_line):
                last_line = fd.readline()
                if(last_line.startswith(" ERROR")): raise SacException("Sac Error:\n"+"Sac command:"+lines[-1]+" "+last_line.strip())
                lines.append(last_line)
        remove(self.transcript_fpath)
        
    def __is_valid_cut_ref(self, ref):
        return re.match(r"^(B|E|O|A|F|T[0-9])$", str(ref), re.I) != None

class SacException (Exception):
    def __init__(self, msg):
        pass
    
def sacio_sac2asc(sac_file, asc_file=None, line_format=None):
    """
    Converts a SAC file to an ASCII file.
    The format is an ASCII pair of time (sac.begin+sac.delta*index) and signal amplitude at this time.
    By default, the output file is the same path and name as the input one, 
    suffixing it with .asc extension.
    sac_file -- The input file.
    asc_file -- Optional argument to set the path and name of ASCII file.
    line_format -- optional format for the destination file line. E.g.: "%16.8f %16.8f" 
    """
    sac_io = SacFile(sac_file)
    if(asc_file == None):
        asc_file = sac_file + ".asc"    
    _file = open(asc_file, 'w')
    if line_format == None:
        # automatic line_format
        tdigits = len(str(sac_io.delta).split('.')[1])
        line_format = '%.'+str(tdigits)+'f %g'
    for i, amp in enumerate(sac_io.data[0]):
        _file.write((line_format+'\n') % (i*sac_io.delta+sac_io.b, amp))
    _file.close()
    return asc_file

def sacio_getsacinfo(sac_file, field):
    """ Returns the sac_file header field value if defined or None otherwise.

        NOTE: getsacinfo() function is an alias of sacio_getsacinfo().

        Examples:
        >>> import py3sac.sac as s
        >>> O = s.sacio_getsacinfo('sismos/2006319BFOBHZ.sac', 'O')
        >>> if(O is None): print('2006319BFOBHZ.sac doesn\'t contain O header')
        2006319BFOBHZ.sac doesn't contain O header
        >>> # warning: 'not O' is not equiv. to 'O is None' because O can be zero.
        >>> s.sacio_getsacinfo('sismos/2006319BFOBHZ.sac', 'NPTS')
        7241
    """
    sac_io = SacFile(sac_file)
    return eval('sac_io.' + field.lower())
 
# forcing sacio use
sac2asc = sacio_sac2asc
getsacinfo = sacio_getsacinfo

def extbin_sac2asc(sac_file, asc_file=None):
    """ deprecated """
    check_executable("nsac2asc")
    if(asc_file == None):
        asc_file = sac_file + ".asc"
    cwd = os.getcwd()
    print("nsac2asc " + sac_file)
    if(dirname(sac_file) != ''):
        os.chdir(dirname(sac_file))
    os.system("nsac2asc " + basename(sac_file) + " " + basename(asc_file))
    os.chdir(cwd)
    return asc_file

def extbin_getsacinfo(sac_file, field):
    """ deprecated """
    check_executable("getsacinfo")
    cwd = os.getcwd()
    os.chdir(dirname(sac_file))
    res = subprocess.getoutput("getsacinfo " + basename(sac_file) + " " + field).strip()
    os.chdir(cwd)
    return res

def get_locmaxs_sacf(trace_sac):
    """
    Does the same as get_locmaxs() (pyutils.nmath module) but reading the x,y values in SAC file trace_sac.
    Returns a list of tuples (x,y) which are the local maximums.
    If none found, returns an empty list.
    trace_sac -- SAC trace file path.
    """
    asc_trace = sac2asc(trace_sac)
    f = open(asc_trace)
    xy_tuple_list = [(float(t[0]), float(t[1])) for t in [l.split() for l in f.readlines()]]
#     print(xy_tuple_list)
    f.close()
    return get_locmaxs(xy_tuple_list)

def get_globmax_sacf(trace_sac):
    """
    Does the same as get_globmax() (pyutils.nmath module) but reading the x,y values in SAC file trace_sac.
    Returns the tuple (x,y) which is the global maximum or None if none found.
    trace_sac -- SAC trace file path.
    """
    asc_trace = sac2asc(trace_sac)
    f = open(asc_trace)
    xy_tuple_list = [(float(t[0]), float(t[1])) for t in [l.split() for l in f.readlines()]]
#     print(xy_tuple_list)
    f.close()
    return get_globmax(xy_tuple_list)

def calc_moving_average(sac_trace, window_sz):
    """
    Computes the moving average for the trace sac_trace (SAC file).
    Returns a list of tuples (x,y) for this average.
    """
    asc_trace = sac2asc(sac_trace)
    xy_tuples = file2tuples(asc_trace)
    avg_trace = calc_moving_average_list(xy_tuples, window_sz)
    remove_files(asc_trace)
    return avg_trace



