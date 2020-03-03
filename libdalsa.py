from pygigev import PyGigEV as pgv


# Utilties
def ipAddr_from_string(s):
  "Convert dotted IPv4 address to integer."
  return reduce(lambda a,b: a<<8 | b, map(int, s.split(".")))

def ipAddr_to_string(ip):
  "Convert 32-bit integer to dotted IPv4 address."
  return ".".join(map(lambda n: str(ip>>n & 0xFF), [24,16,8,0]))

class Camera:
    def __init__(self):
        self.ctx = pgv()
        num_camera_found = self.ctx.GevDeviceCount()
        self.ip_info = {}
        self.ip_info[0] = ipAddr_to_string(self.ctx.GevGetCameraList()[1]['host']['ipAddr'])

    def __del__(self):
        self.disconnect()

    def connect(self, id=0):

        status = self.ctx.GevOpenCamera()
        # get image parameters - returns python object of params
        self.params = self.ctx.GevGetImageParameters()
        self.ctx.GevInitializeImageTransfer(1)
        # self.ctx.GevStartImageTransfer(-1)
        # print("Initial image parameters:")
        # print(self.params)
        return status

    def disconnect(self):
        self.ctx.GevStopImageTransfer()
        status = self.ctx.GevCloseCamera()
        return status

    def get_image(self):

        # self.ctx.GevStartImageTransfer(0)
        img = self.ctx.GevGetImageBuffer().reshape(self.params['height'], self.params['width'])
        # self.ctx.GevStopImageTransfer()
        return img
