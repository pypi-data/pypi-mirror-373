import numpy as np
import datetime   

comments="#"
delimiter=","
skip_header=0
skip_footer=0
max_rows=None
usecols=None
deletechars=" !#$%&'()*+, /:;<=>?@[\\]^{|}~"

def read_file(file_path,comments=comments,delimiter=delimiter, skip_header=skip_header,skip_footer=skip_footer,
                    max_rows=max_rows,usecols=usecols, deletechars=deletechars):
    """ Function to read data from a file
    
        args:
           \n\t- file_path (string) : file, filename, list, or generator to read.
           \n\t- comments (char) : the character used to indicate the start of a comment.
           \n\t- delimiter (char) : the string used to separate values.
           \n\t- skip_header (integer or sequence) : the number of lines to skip at the beginning of the file.
           \n\t- skip_footer (integer or sequence) : the number of lines to skip at the end of the file.
           \n\t- max_rows (integer) : the maximum number of rows to read. Must not be used with skip_footer at the same time.
           \n\t- usecols (sequence) : which columns to read, with 0 being the first. For example, usecols = (1, 4, 5) will extract the 2nd, 5th and 6th columns.
           \n\t- deletechars (string) : a string combining invalid characters that must be deleted from the names.
    
        return:
           \n\t- data (numpy array): numpy array of the data read from the file
    """          
    data=np.genfromtxt(file_path,comments=comments,delimiter=delimiter,
                        skip_header=skip_header,skip_footer=skip_footer,
                        max_rows=max_rows,usecols=usecols, deletechars=deletechars)
    
    return data
    
def write_in_file(file_path,data,delimiter=",",overwrite=False,header=None,date=True, comment="#"):
    """ Function to write data in a file
    
        args:
           \n\t- file_path (string) : path for the data file, including the filename with its extension
           \n\t- data (scalar, list or array) : the data to be written in the file
           \n\t- delimiter (char) : the delimiter to separate the column of the data
           \n\t- overwrite (boolean) : if True overwrite the existing file if any, if False, append the data to the existing file if any
           \n\t- header (string) : header to be written before the data
           \n\t- date (boolean) : date to be written at the beginning of the file
           \n\t- comment (char) : char to be written before the header and date to indicate non-data lines
    
    """        
    if file_path.split(".")[-1]=="csv":
        delimiter=","
        
    # Create file and header
    if overwrite:
        f = open(file_path, "w")
    else:
        f = open(file_path, "a")
        
    if date:
        f.write("%s %s\n"%(comment,datetime.datetime.now().strftime("%c")))
    
    if isinstance(header, str):
        for line in header.split("\n"):
            f.write(comment+" "+line+"\n")

    
    shape=np.shape(data)
    if len(shape)==0:
        f.write("%.6E\n"%(data))
    elif len(shape)==1:
        for i in range(shape[0]):
            if i==0:
                f.write("%.6E"%(data[i]))
            else:
                f.write("%s%.6E"%(delimiter,data[i]))

        f.write("\n")

    elif len(shape)==2:
        for i in range(shape[0]):
            for j in range(shape[1]):
                if j==0:
                    f.write("%.6E"%(data[i,j]))
                else:
                    f.write("%s%.6E"%(delimiter,data[i,j]))
            f.write("\n")                
    f.close()
