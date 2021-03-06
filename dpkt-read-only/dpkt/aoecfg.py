# By Ed Cashin (ed.cashin at acm dot org), committed by Andrew Fleenor

'''ATA over Ethernet ATA command'''

import dpkt

class AOECFG(dpkt.Packet):
    __hdr__ = (
        ('bufcnt', 'H', 0),
        ('fwver', 'H', 0),
        ('scnt', 'B', 0),
        ('aoeccmd', 'B', 0),
        ('cslen', 'H', 0),
        )


if __name__ == '__main__':
    import unittest

    class AOECFGTestCase(unittest.TestCase):
        def test_AOECFG(self):
            s = '\x01\x02\x03\x04\x05\x06\x11\x12\x13\x14\x15\x16\x88\xa2\x10\x00\x00\x01\x02\x01\x80\x00\x00\x00\x12\x34\x00\x00\x00\x00\x04\x00' + '\0xed' * 1024
            aoecfg = AOECFG(s[14+10:])
            self.failUnless(aoecfg.bufcnt == 0x1234)

    unittest.main()
