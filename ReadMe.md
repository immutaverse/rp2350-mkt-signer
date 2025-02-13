# Firmware Signing for RP2350 and Pico2 Chips

We have streamlined the firmware signing process so you don’t have to. Our solution allows individual developers to sign firmware in multiple modes **without ever accessing the development keys**.

Our Docker-based approach integrates the chip SDK and signing tools, enabling seamless CI/CD pipeline integration while maintaining rigorous security and approval processes.

## Key Security Features:

* **Granular access control**: Developers can be restricted to signing with lower-environment keys (e.g., Dev, QA), while production-level signing is restricted to approved merges into the release branch.
* **Approval-controlled workflow**: Production firmware signing requires explicit approval, ensuring compliance with security and governance policies.
* **Signing keys remain secure**: Stored as GitHub secrets, signing keys are used only in-memory during the signing process.
* **Developer access control**: Developers can sign firmware without ever seeing the signing keys. Only the key generator needs access.

## How It Works:

* Our proprietary Docker images contain the necessary SDK, signing tools, and validation logic.
* The signing process runs entirely within your CI/CD pipeline and never exposes private keys to external systems or our cloud.
* After signing, the container and its memory space are completely destroyed, ensuring no residual exposure of sensitive information.

This approach eliminates the complexity of firmware signing while keeping it safe, efficient, and fully controlled by you.name: 'rp2350-firmware-signer'

## Sample Use
### Sample Call from your CICD Workflow
This section shows you how to add a call to our pre-build
firmware signer from your code. For a complete sample project including a pre-built binary ready to sign 
see [rp2350-ex-mkt-sign-via-action](https://github.com/immutaverse/rp2350-ex-mkt-sign-via-action)

Sourced from [do-sign.yml](https://github.com/immutaverse/rp2350-ex-mkt-sign-via-action/blob/main/.github/do-sign.yml) Please look there for the most current version

<!-- TODO: Add a script to auto pull and update README when this file has changed https://github.com/immutaverse/rp2350-ex-mkt-sign-via-action/blob/main/.github/do-sign.yml -->


```
uses: actions/rp2350-firmware-signer@v0.004
  with:
    # Path to the previously generated uf2 firmware file
    FIRMWARE: 'unsigned/blink_fast.uf2'

    # 'sign' to sign an existing firmware file.
    # 'build' to build the firmware from source and sign it.
    #   if the PRIVATE_KEY is provided.
    BUILD_ACTION: 'sign'
    
    #Base64 encoded private key normally loaded from
    #github secret but you can provide it from 
    #any source. 
    PRIVATE_KEY: ${{ secrets.RP2350_SAMPLE_PRIVATE_KEY }}
    
    # Path to otp firmare options file that will be 
    # updated with public key for signing.
    OTP_FILE: signed/blink_fast.otp.json

    #  this is the boardname passed into the build
    #  scripts.  normally only used when build_action
    #  is set to build.  May not be needed for 
    #  sign only events.
    BOARD_NAME: 'pico2'

    # source directory containing source code to build
    #  with the SDK file.  Mandatory when build_action 
    #  is set to build. This is the directory where 
    #  you have saved your CMakeLists.txt See and example
    #  at https://github.com/immutaverse/rp2350-ex-blink-fast    
    #  ignored when build_action is set to sign.
    SOURCE_DIR: 'NOT SET'
```

## One time steps for each product or Model
A product is a unique piece of hardware where you need to deploy signed firmware. The best practice is to create a new signing key for each major release of your product and approximately once a year. Many companies create only one signing key per unique model number, but best practice is to use different signing keys for each major release and annual update. This means you need different signed versions of the firmware and must manage their deployment to matching units, but it improves security and reduces the scope of impact in the event of a security event. 
*  You create your signing keys.  We provide example commands for this.
*  You save the private signing key as a git secret.
*  You save the private signing key in a HSM or encrypted on
   portable media in a safe deposit box.
*  You record the git variable to model # mapping in your master 
   keys spreadsheet.  This is a important audit and recovery 
   asset.  
*  You tell the your develpment teams what git variable to reverence 
   for signing.

## Steps for each new repository project 
*  You create your github.com repository with your firmware files
*  You update your CICD to build the firmware file.  For pico2 this
   is a uf2 file. 
   * We also offer pre-built actions along with our pre-built toolchain
     and SDK files to greatly simplify the process of building your 
     source to produce the firmware file. 
*  You update your CICD to call our firmware signer for your chipset.
   * generate the starting OTP flash settings we will add 
     secure boot settings to this file.  
*  We sign the firmware:
   * Generate A new signed firmware file.
   * Write A new otp file used to flash the public key to your hardware.
     This step also forces the hardware into a mode where it will
     only run signed firmware.
   * Write A new script that will flash the public key to your hardware 
     and require secure boot.
*  You modify your CICD to save the saved firmware to a location where 
   you can make it avaialble for download to update your devices.

## Key preservation
* **Secure key storage recommendation**: While we suggest storing signing keys as GitHub private variables, we also recommend encrypting and backing them up on portable storage in a secure location (e.g., a safe deposit box) for worst-case recovery.

## Interfacing 



  ### Outputs


