#!/usr/bin/env python3
"""EverDrive X7 Autoboot OS: quiet v3 patch for SMSOS v1.04.
Usage: python3 tools/build_patch.py STOCK_SMSOS.BIN OUTPUT_SMSOS.BIN
Requires Python 3; no third-party packages.
"""
import hashlib
from pathlib import Path
import sys

STOCK_SHA256='c261956de0ff81132b780abe706d7080c4a9e847a44c796f110a54247bfe53cd'
ORIGIN=0x7421

def make_payload():
    code=bytearray(); labels={}; fixups=[]
    def emit(s): code.extend(bytes.fromhex(s))
    def word(n): code.extend((n&65535).to_bytes(2,'little'))
    def label(s): labels[s]=ORIGIN+len(code)
    def target(op,s):
        emit(op); fixups.append((len(code),s)); word(0)
    def relative(op,s):
        emit(op)
        delta=labels[s]-(ORIGIN+len(code)+1)
        assert -128<=delta<=127
        code.append(delta&255)
    def call(n): emit('cd'); word(n)
    def ptr(n): emit('21'); word(n); emit('39')
    def check(): emit('7d b7'); target('c2','error')

    # Stock main enters only after its unchanged initialization succeeds.
    label('entry')
    emit('21 17 ff 39 f9 dd 21 00 00 dd 39')
    # 233-byte frame: uint16 index, 2 reserved bytes, 229-byte descriptor.
    emit('af 32 5a c6') # Disable in-game menu in the registry.
    emit('21 00 00 e5 e5'); call(0x437c); emit('f1 f1'); check()
    # fatReadDir(0): stock traversal indexes the root across its cluster chain.
    emit('dd 36 00 00 dd 36 01 00')
    label('scan')
    emit('dd 6e 00 dd 66 01 ed 5b f9 c9 b7 ed 52')
    target('d2','not_found') # index >= directory entry count.
    # Read a descriptor from the 32-bit entry ID in the stock index table.
    ptr(4); emit('e5')
    emit('dd 6e 00 dd 66 01 29 29 ed 5b 00 ca 19')
    emit('5e 23 56 23 4e 23 46 c5 d5')
    call(0x4858); emit('f1 f1 f1'); check()
    ptr(232); emit('7e b7'); target('c2','next') # Directory flag E4.
    ptr(4); emit('7e fe 2e'); target('ca','next') # Dot/AppleDouble names.
    target('cd','match_name'); emit('7d b7'); target('c2','selected')
    label('next')
    emit('dd 34 00'); target('c2','scan')
    emit('dd 34 01'); target('c3','scan')
    label('selected')
    ptr(4); emit('af f5 33 e5'); call(0x2dda); emit('f1 33'); check()
    call(0x2f20) # Original ROM loader/handoff; successful launch never returns.
    target('c3','error')
    label('not_found'); emit('2e f0')
    label('error')
    # Keep useful stock error reporting on failure, with no normal progress UI.
    emit('7d f5 33'); call(0x3057); emit('33')
    label('stop'); emit('f3 76'); target('c3','stop')

    # HL = descriptor name. Return L=1 for a regular .gg filename, else zero.
    # Raw FAT short names contain eleven padded bytes, e.g. 'SONIC   GG '.
    # Compact only matching SFNs; dotted long names remain byte-for-byte intact.
    label('match_name')
    emit('e5 11 0b 00 19 7e b7'); target('c2','long_name')
    emit('2b 7e fe 20'); target('c2','long_name')
    emit('2b 7e f6 20 fe 67'); target('c2','long_name')
    emit('2b 7e f6 20 fe 67'); target('c2','long_name')
    # Verify the basename has no dot, distinguishing an SFN from a dotted LFN.
    emit('e1 e5 06 08')
    label('check_base')
    emit('7e fe 2e'); target('ca','long_name')
    emit('23'); relative('10','check_base')
    emit('e1 54 5d 06 08') # HL=base; DE=output; B=8.
    label('copy_base')
    emit('7e fe 20'); target('ca','append_ext')
    emit('23 12 13'); relative('10','copy_base')
    label('append_ext')
    emit('3e 2e 12 13 3e 47 12 13 12 13 af 12 2e 01 c9')

    label('long_name')
    emit('e1 06 d0 0e 00') # Restore base, bounded scan through name field.
    label('find_end')
    emit('7e b7'); target('ca','name_end')
    emit('23 0c'); relative('10','find_end')
    target('c3','no_match') # Unterminated descriptor.
    label('name_end')
    emit('79 fe 04'); target('da','no_match')
    emit('2b 7e f6 20 fe 67'); target('c2','no_match')
    emit('2b 7e f6 20 fe 67'); target('c2','no_match')
    emit('2b 7e fe 2e'); target('c2','no_match')
    emit('2e 01 c9')
    label('no_match'); emit('2e 00 c9')

    for pos,name in fixups: code[pos:pos+2]=labels[name].to_bytes(2,'little')
    assert ORIGIN+len(code)<0x7bf0, 'Payload overlaps stock font'
    return bytes(code),labels

def patch(stock):
    if hashlib.sha256(stock).hexdigest()!=STOCK_SHA256:
        raise ValueError('Input must be the supplied stock v1.04 BIN.')
    b=bytearray(stock); payload,labels=make_payload()
    assert b[ORIGIN:ORIGIN+len(payload)]==b'\xff'*len(payload)
    b[ORIGIN:ORIGIN+len(payload)]=payload
    assert b[0x15a2:0x15aa]==bytes.fromhex('21 d1 15 e5 cd 0b 0a f1')
    b[0x15a2:0x15aa]=bytes(8) # Remove OS init text, retain stock blank flush.
    assert b[0x15bc:0x15bf]==bytes.fromhex('21 00 00')
    b[0x15bc:0x15bf]=b'\xc3'+labels['entry'].to_bytes(2,'little')
    # Original initialization, warnings, FAT/SD code, mapper detection and
    # game loader remain unchanged. No AB2 or other progress messages.
    b[0x7ffa:0x7ffc]=(sum(b[:0x7ff0])&65535).to_bytes(2,'little')
    assert len(b)==65536
    return bytes(b)

if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit(__doc__)
    result=patch(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(hashlib.sha256(result).hexdigest())
