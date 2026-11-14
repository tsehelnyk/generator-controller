class _Operation:
    def __init__(self, value):
        self.value = value

class Operation:
    charging = _Operation("CHARGING")
    discharging = _Operation("DISCHARGING")
    start_charging = _Operation("START CHARGING")
    stop_charging = _Operation("STOP CHARGING")

class _OperationStep:
    def __init__(self, previousOperation, operation, nextOperation):
        self.previousOperation = previousOperation
        self.operation = operation
        self.nextOperation = nextOperation
class OperationSteps:
    charging = _OperationStep(Operation.start_charging, Operation.charging, Operation.stop_charging)
    discharging = _OperationStep(Operation.stop_charging, Operation.discharging, Operation.start_charging)
    startCharging = _OperationStep(Operation.discharging, Operation.start_charging, Operation.charging)
    stopCharging = _OperationStep(Operation.charging, Operation.stop_charging, Operation.discharging)
