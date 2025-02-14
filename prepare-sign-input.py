# Prepare to call the signing docker 
# by moving our named inputs to a directory
# we want to make available to docker. 

import os
import shutil
                              
build_action = os.getenv("BUILD_ACTION", "")  # Get the env var, default to empty if not set
otp_file = os.getenv("OTP_FILE", "")  # Get the env var, default to empty if not set
firmware = os.getenv("FIRMWARE", "")  # Get the env var, default to empty if not set
dwsd = os.getenv("DOCKER_WORKSPACE")  # Docker workspace directory
dw_firmware = os.getenv("DW_FIRMWARE")  
dw_otp = os.getenv("DW_OTP")

os.makedirs(dwsd, exist_ok=True)

if build_action != "sign":
    print(f"Not signing, action={build_action}")
    exit(0)

if not firmware or not os.path.isfile(firmware):
    print(f"Error: FIRMWARE is not set or does not exist! {firmware}")
    exit(1)

# Copy firmware to docker workspace
shutil.copy(firmware, dw_firmware)
print(f"Copied {firmware} to {dw_firmware}")

# Copy OTP file if it exists
if otp_file and os.path.isfile(otp_file):
    shutil.copy(otp_file, dw_otp)
    print(f"Copied {otp_file} to {dw_otp}")
else:
    print(f"OTP_FILE not found or not set ({otp_file}), will create from scratch.")
