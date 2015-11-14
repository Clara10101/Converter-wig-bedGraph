import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="input files", type=argparse.FileType('r'), required=True)
args = parser.parse_args()

def check_type(line):
    """
    Checks format of the file
    :param line: first line of the file
    :type line: str
    :return: 2 if file type is .bedGraph, 1 if .wig, else 0
    """
    file_type = None
    proper_formats = {"bedGraph" : 2, "wiggle_0" : 1}
    new_track_line = ""
    if "type=" in line:
        p = line.find("type=")
        file_type = line[p + 5: p + 13]
        if file_type == "bedGraph":
            new_track_line = line.replace("bedGraph", "wiggle_0")
        elif file_type == "wiggle_0":
            new_track_line = line.replace("wiggle_0", "bedGraph")
    #check file format
    if file_type in proper_formats:
        return proper_formats[file_type], new_track_line
    return 0, new_track_line
    
  
  def convert_to_bedGraph(file, new_track_line):
    """
    Converts wig to bedGraph
    :param file: wig file
    :param new_track_line: first line with changed type declaration
    """
    possible_types = {"fixedStep": 1, "variableStep": 0}
    current_type = None
    output_file = open(remove_extension_form_file_name(file.name) + ".bedGraph", "w")
    output_file.write(new_track_line + "\n")
    # okreslenie czy fixedStep, czy variableStep
    for line in file:
        actual_line = line.split()
        if actual_line[0] == "fixedStep":
            current_type = possible_types["fixedStep"]
            chrN = actual_line[1][6:]
            start = int(actual_line[2][6:])
            step = int(actual_line[3][5:])
            if "span" in line:
                span = int(actual_line[4][5:])
            else:
                span = 1
        elif actual_line[0] == "variableStep":
            current_type = possible_types["variableStep"]
            chrN = actual_line[1][6:]
            step = 0
            if "span" in line:
                span = int(actual_line[2][5:])
            else:
                span = 1
        else:
            if current_type == 0:
                start = int(actual_line[0])
                value = actual_line[1]
            elif current_type == 1:
                value = actual_line[0]
            else:
                #input file is not correct
                print >> sys.stderr, "Exception: infut file is nit correct"
                sys.exit(1)
            output_file.write(chrN + "\t" + str(start - 1) + "\t" + str(start - 1 + span) + "\t" + value + "\n")
            start += step


def convert_to_wig(file, new_track_line):
    """
    Converts bedGraph to wig fixedStep
    :param file: bedGraph file
    :param new_track_line: first line with changed type declaration
    """
    output_file = open(remove_extension_form_file_name(file.name) + ".wig", "w")
    output_file.write(new_track_line + "\n")
    for line in file:
        actual_line = line.split()
        if len(actual_line) >= 4:
            chrom = actual_line[0]
            start = int(actual_line[1])
            end = int(actual_line[2])
            value = actual_line[3]
            output_file.write("fixedStep chrom=" + chrom + " start=" + str(start + 1) + " step=1 span=" + str(
                end - start) + "\n" + value + "\n")
        else:
            print >> sys.stderr, "Exception: input file is not correct"
            sys.exit(1)
            
            
def remove_extension_form_file_name(file_name):
    """
    :param file_name: file name
    :type file_name: str
    :return: file name without extention
    """
    if '.' in file_name:
        return '.'.join(file_name.split('.')[:-1])
    else:
        return file_name
        
        
with args.input as f:
    current_type, new_track_line = check_type(f.readline().strip())
    if current_type == 1:
        #.wig to .bedGraph
        convert_to_bedGraph(f, new_track_line)
    elif current_type == 2:
        #.bedGraph to .wig fixedStep
        convert_to_wig2(f, new_track_line)
    else:
        print >> sys.stderr, "Exception: input file is not correct"
        sys.exit(1)
