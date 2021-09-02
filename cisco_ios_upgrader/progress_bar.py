class Bar(object):
    def __init__(self, peername, filename) -> None:
        self.hostname = peername[0]
        self.filename = filename
        self.bar = progressbar.ProgressBar(redirect_stdout=True, max_value=100, widgets=[progressbar.Bar(left=f"{self.hostname} | {self.filename}: "), progressbar.Percentage(), progressbar.Timer(format=" Elapsed Time: %(elapsed)s")])

    def progress4(self, filename, size, sent, peername):
        self.bar.update(float(sent)/float(size)*100)

