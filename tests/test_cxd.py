import pytest

__author__ = "malware4n6"
__copyright__ = "malware4n6"
__license__ = "MIT"

from cxd.colored_hex_dump import ColoredHexDump, ColorRange
from cxd.main import main

data = b'\xc4\xc0q"\x8e\xb4\xc9\x94\x06\x01\x1e0\xca\x15*\x03/L1Ku\x9d1\x16\xe7\x84\xf7^\x90\x161\x89\xc4\xa4[\x9c\r\xf4\xc0\xf1\nf\xa7\xa0\xcd\x85c\x8bw\xa1'

expected_from_file = '''00000000\t1F C1 2F 70 06 81 06 9D 50 19 89 8B 17 A7 CA EF \t../p....P.......
00000010\tE5 2B 23 14 41 53 D5 8E 02 B4 4D 11 E3 F4 FA 4B \t.+#.AS....M....K
00000020\t57 41 CF EE DA 0E BB 8D 0D 28 2D 69 34 13 10 ED \tWA.......(-i4...
00000030\t6D D8 DC 6F FD D7 D7 4B 3E C6 DB 25 55 5A 1F 76 \tm..o...K>..%UZ.v
00000040\t31 17 E0 7D 3E 78 70 42 1F C2 0B 3E F6 3F 03 FB \t1..}>xpB...>.?..
00000050\tDA 39 39 B1 0D 74 DF 78 DF 8B FA 64 3A C9 01 B1 \t.99..t.x...d:...
00000060\t5E 9E B8 C5 67 CF ED 3B 31 C6 51 BB 4F 5D FC 84 \t^...g..;1.Q.O]..
00000070\t41 3A C8 4D E9 AE C6 7C DB 14 3F 7A B7 C4 A1 95 \tA:.M...|..?z....
00000080\tBC 2E A9 A6 DE 2D 5B 76 50 CB 7C 23 FE 68 D7 3F \t.....-[vP.|#.h.?
00000090\t82 B7 B4 CA 82 F2 AC 5D 13 BE ED B3 FB F6 DE 47 \t.......].......G
000000a0\t14 DB 78 89 BC C6 54 C1 71 A8 C5 C7 47 40 CB B3 \t..x...T.q...G@..
000000b0\t4B 7C 4F 82 15 57 29 4B A8 1D 4F 02 EF CF 45 3C \tK|O..W)K..O...E<
000000c0\t0C 5F 46 91 60 30 1B 20 E8 8D 31 FE 5C B2 19 09 \t._F.`0. ..1.\\...
000000d0\t1C FF 59 CB 29 4B 1A 39 24 1E 3A 49 8C FF 7F C3 \t..Y.)K.9$.:I....
000000e0\t5E 8A C0 63 35 D0 F5 53 A7 B6 E1 DF 4F CF EB 4F \t^..c5..S....O..O
000000f0\t2D 99 F6 FA 1C FC 3E 01 8D 80 25 2C 89 01 B0 39 \t-.....>...%,...9
00000100\t18 77 B1 12 10 75 EC F1 B7 AE B9 FC 4D 42 FB B7 \t.w...u......MB..
00000110\t7A C7 28 D6 7C 27 6D 36 52 C2 81 2D F8 2A 29 E8 \tz.(.|'m6R..-.*).
00000120\t3A F7 C0 00 65 03 48 37 CA 18 9E DB C1 D6 54 85 \t:...e.H7......T.
00000130\t0C 4B 35 A4 19 48 2A 1E 90 7D 59 87 5B FB C2 3E \t.K5..H*..}Y.[..>
00000140\tE2 EE 8A A4 23 63 ED 6C B2 AC A1 FA 0F 55 8D 12 \t....#c.l.....U..
00000150\t15 A3 29 2B 42 B2 4C B9 0A 46 58 6F FF C0 5E 2A \t..)+B.L..FXo..^*
00000160\t5D 28 73 75 E3 31 2A 99 B6 9D AD BA 92 10 A2 E3 \t](su.1*.........
00000170\t02 80 7E 85 FB BB 81 0E 7E 7C 75 F4 3E 64 EE DD \t..~.....~|u.>d..
00000180\t69 7A FB CA 63 DA 58 AD C0 8D 66 09 5A 51 A3 03 \tiz..c.X...f.ZQ..
00000190\t62 A5 E3 76 B3 3F 10 C2 FF 5E 14 E4 58 63 8D FA \tb..v.?...^..Xc..
000001a0\t0D A4 26 C9 2C 8B FF F2 D9 46 97 E7 63 26 05 1F \t..&.,....F..c&..
000001b0\t2A B5 28 A3 3B 5E 71 04 7B C9 3B 3D 31 B9 93 7B \t*.(.;^q.{.;=1..{
000001c0\tAE DB 71 82 90 88 FD 1B F7 FC A1 62 93 08 58 E3 \t..q........b..X.
000001d0\t8A 52 88 39 5C 37 5F 50 02 FA 5A 10 EC 9A 28 56 \t.R.9\\7_P..Z...(V
000001e0\t22 1A 29 9F 2A 05 46 13 CD C2 15 5A 8A 7D 65 5F \t".).*.F....Z.}e_
000001f0\t19 46 A1 5E                                     \t.F.^'''.replace('\n', '')

def test_bad_params():
    ranges = [ColorRange(0, 4, 'red'),
                ColorRange(4, 4, 'green'),
                ColorRange(0, 4, 'blue')]
    with pytest.raises(AssertionError):
        _ = ColoredHexDump(ranges=ranges, chunk_length=-1, address_shift=0,
                        default_color='white', shadow_color='dark_grey',
                        address_color='cyan', enable_shadow_bytes=True,
                        hide_null_lines=True, memorize_last_color_range=False)
    with pytest.raises(AssertionError):
        _ = ColoredHexDump(ranges=ranges, chunk_length=16, replace_not_printable='QWERTY', address_shift=0,
                        default_color='white', shadow_color='dark_grey',
                        address_color='cyan', enable_shadow_bytes=True,
                        hide_null_lines=True, memorize_last_color_range=False)

def test_simple_output(capsys):
    ranges = [ColorRange(0, 4, 'red'),
                ColorRange(4, 4, 'green'),
                ColorRange(8, 4, 'blue')]
    cxd = ColoredHexDump(ranges=ranges, chunk_length=16, address_shift=0,
                        default_color='white', shadow_color='dark_grey',
                        address_color='cyan', enable_shadow_bytes=True,
                        hide_null_lines=True)
    cxd.print(data)
    captured = capsys.readouterr()
    assert '00000000\tC4 C0 71 22 8E B4 C9 94 06 01 1E 30 CA 15 2A 03 \t..q".......0..*.' in captured.out
    assert '00000010\t2F 4C 31 4B 75 9D 31 16 E7 84 F7 5E 90 16 31 89 \t/L1Ku.1....^..1.' in captured.out
    assert '00000020\tC4 A4 5B 9C 0D F4 C0 F1 0A 66 A7 A0 CD 85 63 8B \t..[......f....c.' in captured.out


def test_stop_at_first_color_found_false(capsys):
    ranges = [ColorRange(0, 4, 'red'),
                ColorRange(4, 4, 'green'),
                ColorRange(8, 4, 'blue')]
    cxd = ColoredHexDump(ranges=ranges, chunk_length=16, address_shift=0,
                        default_color='white', shadow_color='dark_grey',
                        address_color='cyan', enable_shadow_bytes=True,
                        stop_at_first_color_found=False, hide_null_lines=True)
    cxd.print(data)
    captured = capsys.readouterr()
    assert '00000000\tC4 C0 71 22 8E B4 C9 94 06 01 1E 30 CA 15 2A 03 \t..q".......0..*.' in captured.out
    assert '00000010\t2F 4C 31 4B 75 9D 31 16 E7 84 F7 5E 90 16 31 89 \t/L1Ku.1....^..1.' in captured.out
    assert '00000020\tC4 A4 5B 9C 0D F4 C0 F1 0A 66 A7 A0 CD 85 63 8B \t..[......f....c.' in captured.out

def test_overlap(capsys):
    ranges = [ColorRange(0, 4, 'red'),
                ColorRange(4, 4, 'green'),
                ColorRange(0, 4, 'blue')]
    cxd = ColoredHexDump(ranges=ranges, chunk_length=16, address_shift=0,
                        default_color='white', shadow_color='dark_grey',
                        address_color='cyan', enable_shadow_bytes=True,
                        hide_null_lines=True, memorize_last_color_range=False)
    cxd.print(data)
    captured = capsys.readouterr()
    assert '00000000\tC4 C0 71 22 8E B4 C9 94 06 01 1E 30 CA 15 2A 03 \t..q".......0..*.' in captured.out
    assert '00000010\t2F 4C 31 4B 75 9D 31 16 E7 84 F7 5E 90 16 31 89 \t/L1Ku.1....^..1.' in captured.out
    assert '00000020\tC4 A4 5B 9C 0D F4 C0 F1 0A 66 A7 A0 CD 85 63 8B \t..[......f....c.' in captured.out


def test_main(capsys):
    # capsys is a pytest fixture that allows asserts against stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(['-d', './tests/random.bin'])
    captured = capsys.readouterr()
    assert expected_from_file in captured.out.replace('\n', '')

def test_file(capsys):
    ranges = [ColorRange(0, 4, 'red'),
                ColorRange(4, 4, 'green'),
                ColorRange(8, 4, 'blue')]
    cxd = ColoredHexDump(ranges=ranges, chunk_length=16, address_shift=0,
                        default_color='white', shadow_color='dark_grey',
                        address_color='cyan', enable_shadow_bytes=True,
                        hide_null_lines=True)
    cxd.print_file('./tests/random.bin')
    captured = capsys.readouterr()
    assert expected_from_file in captured.out.replace('\n', '')

