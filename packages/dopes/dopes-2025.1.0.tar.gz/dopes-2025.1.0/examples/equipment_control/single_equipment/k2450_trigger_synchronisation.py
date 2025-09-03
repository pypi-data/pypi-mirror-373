# =============================================================================
# 1. Import classes and parameters definition
# =============================================================================

import pyvisa

timeout=10e-3
address="GPIB0::24::INSTR"
compliance=1e-3
bias_levels=[5,0]

# =============================================================================
# 2. List  available connections
# =============================================================================
rm=pyvisa.ResourceManager()
list_connections= rm.list_resources()
print("-------------------------------------------------\n Available connections: %s"%str(list_connections))


# =============================================================================
# 3. Connection to the equipment
# =============================================================================

k2450 = rm.open_resource(address)
k2450.timeout=timeout
k2450.write("*RST")

# =============================================================================
# 4. Definition of the bias levels
# =============================================================================

k2450.write("SOUR:CONF:LIST:CRE 'biasLevel'")
k2450.write("SOUR:FUNC VOLT")
k2450.write("SENS:FUNC 'CURR'")
k2450.write("SOUR:VOLT:LEVEL %E"%bias_levels[0])
k2450.write("SOUR:VOLT:ILIM %E"%compliance)
k2450.write("SOUR:CONF:LIST:STORE 'biasLevel'")

k2450.write("SOUR:FUNC VOLT")
k2450.write("SENS:FUNC 'CURR'")
k2450.write("SOUR:VOLT:LEVEL %E"%bias_levels[1])
k2450.write("SOUR:VOLT:ILIM %E"%compliance)
k2450.write("SOUR:CONF:LIST:STORE 'biasLevel'")

# =============================================================================
# 5. Definition of the trigger model
# =============================================================================

k2450.write("DIG:LINE1:MODE TRIG, IN")
k2450.write("TRIG:DIG1:IN:CLEAR")
k2450.write("TRIG:DIG1:IN:EDGE RISING")
k2450.write("DIG:LINE2:MODE TRIG, IN")
k2450.write("TRIG:DIG2:IN:CLEAR")
k2450.write("TRIG:DIG2:IN:EDGE FALLING")

k2450.write("TRIG:LOAD 'EMPTY'")
k2450.write("TRIGger:BLOCk:WAIT 1, DIGio1, Enter")
k2450.write("TRIG:BLOCK:CONF:RECALL 2, 'biasLevel', 1")
k2450.write("TRIGger:BLOCk:WAIT 3, DIGio2, Enter")
k2450.write("TRIG:BLOCK:CONF:RECALL 4, 'biasLevel', 2")
k2450.write("TRIGger:BLOCk:BRANch:ALWays 5, 1")

# =============================================================================
# 6. Initialization of the trigger
# =============================================================================

k2450.write("INITIATE")
# k2450.write("ABORT")
