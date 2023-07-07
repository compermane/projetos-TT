from ordenacao import *
from sys import settrace
import opcode

def show_trace(frame, event, arg):
    frame.f_trace_opcodes = True
    code = frame.f_code
    offset = frame.f_lasti

    with open('out.txt', 'a') as f:
        print(f"| {event:10} | {str(arg):>4} |", end = ' ', file = f)
        print(f"{str(frame.f_lineno):>10} | {frame.f_lasti:>6} |", end = '', file = f)
        print(f"{opcode.opname[code.co_code[offset]]:<18} | {str(frame.f_locals):<35} |", file = f)

    return show_trace

if __name__ == "__main__":
    header = f"| {'event':10} | {'arg':>4} | line | offset | {'opcode':^18} | {'locals':^35} |"
    
    with open('out.txt', 'w') as f:
        print(f"{header}", file = f)

    settrace(show_trace)
    v = [0, 1, 2, 3, 4, 5]
    v = bubbleSort(v)
    settrace(None)