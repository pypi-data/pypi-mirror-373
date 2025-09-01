class TraceNotFoundError(Exception):
    def __init__(self):
        super().__init__("Trace file not found")
