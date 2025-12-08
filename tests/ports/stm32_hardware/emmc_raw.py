import pyb


class Test:
    def __init__(self, length, offset):
        self.length = length
        self.offset = offset

        self.mmcard = pyb.MMCard()
        if not self.mmcard.power(1):
            raise RuntimeError("MMCard initialization failed")

    @staticmethod
    def make_raw(buf, i):
        m = len(buf) // 64
        for n in range(m):
            buf[n * 64 : n * 64 + 64] = (
                f":{i * m + n:9}:AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz\n".encode()
            )

    def write_data(self):
        buf = memoryview(bytearray(512))

        for i in range(self.length):
            self.make_raw(buf, i)
            self.mmcard.writeblocks(self.offset + i, buf)

    def read_data(self):
        buf = memoryview(bytearray(512))

        for i in range(self.length):
            # re-create the expected data
            self.make_raw(buf, i)

            # don't re-use the read buffer since this seems to make the issue
            # far more common
            read_buf = memoryview(bytearray(512))
            self.mmcard.readblocks(self.offset + i, read_buf)

            if buf != read_buf:
                print(f"FAIL: {i}")
                exp = buf.hex()
                got = read_buf.hex()
                print(f"exp: ({len(buf)}):", exp)
                print(f"got: ({len(buf)}): ", end="")

                # print the mis-matched characters in red
                for e, g in zip(exp, got):
                    if e != g:
                        print(f"\033[91m{g}\033[0m", end="")
                    else:
                        print(f"{g}", end="")
                print()

                return False

        print("Success")
        return True


if __name__ == "__main__":
    test = Test(64, 0)
    test.write_data()

    while test.read_data():
        pass
