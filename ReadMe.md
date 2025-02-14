# Firmware Signing for RP2350 and Pico2 Chips

Secure boot helps protect customers by ensuring that only approved code can run on devices, but it requires cryptographic firmware signing using private keys. We have streamlined the firmware signing process to make it secure and efficient. A critical risk is that every person with access to signing keys increases the likelihood of fraudulent software being deployed. Our solution allows individual developers to sign firmware in multiple modes **without ever having access to the signing keys**.

Our Docker-based approach integrates the chip vendor SDK and signing tools, enabling seamless CI/CD pipeline integration while maintaining rigorous security and approval processes. This saves you time and expense by eliminating the need to configure and maintain your own secure signing toolchain.

## Key Security Features:

* **Granular access control**: Developers can be restricted to signing with lower-environment keys (e.g., Dev, QA), while production-level signing is restricted to approved merges into the release branch.
* **Approval-controlled workflow**: Production firmware signing requires explicit approval, ensuring compliance with security and governance policies.
* **Signing keys remain secure**: Stored as GitHub secrets, signing keys are used only in-memory during the signing process.
* **Developer access control**: Developers can sign firmware without ever seeing the signing keys. Only the key generator needs access.

## How It Works:

* Our proprietary Docker images contain the necessary SDK, signing tools, and validation logic.
* The signing process runs entirely within your CI/CD pipeline and never expose private keys to external systems or our cloud.
* After signing, the container and its memory space are completely destroyed, ensuring no residual exposure of sensitive information.

This approach eliminates the complexity of firmware signing while keeping it safe, efficient, and fully controlled inside of a fully repeatable and auditable CICD pipeline. 

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
* Please note: The caller is responsible to copy any 
  files needed to a location accessible by the docker
  image and adjust the input parameters to point at 
  those locations.  By security principal of LEAST_ACCESS
  you should 
  never copy more than the singer / builder needs to 
  directories it can access.

### Outputs
* At same path and name as input firmware the signed
  firmware is written with base_name.uf2 converted to
  base_name.signed.uf2.
* The OTP file specified in input is udpated with public key 
* At same path and name as input firmware a script to 
  blow the fuses and force the cpu to only accept software
  singed with the private key is written.  base_name.uf2 
  is changed to base_name.sec-boot-blow-fuses.sh  this
  script will only run on machines where picotool has been
  successfully installed. 


## One time steps for each product or Model
A product is a unique piece of hardware that requires signed firmware for deployment. The best practice is to generate a new signing key for each major product release and approximately once a year. While many companies use a single signing key per model number, a more secure approach is to use distinct signing keys for each major update and annual refresh.

This strategy enhances security by limiting the scope of impact in the event of a key compromise. However, it also requires careful management of multiple signed firmware versions to ensure each device receives the correct update. Over time, the number of signed firmware versions grows, increasing the complexity of maintaining and distributing the right version to each device.

For many companies, managing this internally can be costly and operationally challenging. [Immutaverse](mailto:sales@immutaverse.com) offers enterprise-grade services to streamline this process, ensuring the correct signed firmware is delivered efficiently while reducing the burden on internal teams.

*  You create your signing keys.  We provide example commands for this.
*  You save the private signing key as a git secret.
*  You save the private signing key in a HSM or encrypted on
   portable media in a safe deposit box.  The key here is make 
   triple sure it never leaks and that you can not loose access 
   to it even under worst case natural disasters.
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

# Secure and Reproducible Firmware Builds
Many companies rely on ad-hoc, desktop-based build environments tied to specific IDEs and local configurations. This approach introduces several risks:
* Fragile Build Environments – When a build environment breaks, diagnosing and fixing issues often requires the most senior (and expensive) engineers, leading to costly downtime.
* Unpredictable Toolchain Changes – Over time, variations in libraries, linkers, and compilers can introduce subtle, hard-to-track differences in firmware behavior.
* Security Vulnerabilities – A compromised developer machine could introduce malware-modified components into the firmware, creating an attack vector that is difficult to detect.
* Dependency Conflicts & SDK Installation Issues – Installing SDKs and toolchains on a workstation can lead to dependency conflicts with other software, causing unexpected failures. Debugging these issues can take days and may require fully reinstalling the OS just to get a clean build environment.
### Best Practice: Containerized, Reproducible Builds
To mitigate these risks, we recommend using clean, containerized build environments with well-defined and auditable toolchains. Our approach leverages Docker-based builds triggered directly within GitHub Actions, ensuring:
* Consistent and Reproducible Builds – Each build runs in a fresh, isolated container with a locked-down toolchain, preventing unexpected drift.
* Increased Security – The entire build process occurs within GitHub’s infrastructure, eliminating reliance on potentially compromised developer workstations or long-lived build servers.
* Simplified CI/CD Integration – Automated builds ensure that every firmware version is compiled in a controlled, repeatable manner.
Elimination of SDK/Toolchain Conflicts – Every build starts from a known, clean state, ensuring that SDK installations and dependencies do not conflict with other software on a developer’s machine.

To simplify this process, [Immutaverse](mailto:sales@immutaverse.com) provides pre-built GitHub Actions, toolchains, and SDK files, allowing you to easily integrate a fully managed and secure build process into your CI/CD pipeline.

Complex SDK Dependencies – Many SDKs require dozens to hundreds of dependencies, making build environments large and difficult to manage. Setting up these dependencies directly within GitHub Actions on every build is slow and inefficient. By bundling everything into pre-built Docker images, we provide a complete, working toolchain that is frozen at a known version. At the same time, we regularly release new images with updated libraries, allowing teams to upgrade at their own pace—testing new versions safely without jeopardizing their existing build environments.

For enterprise-grade customers, we also offer custom-built images with pre-downloaded libraries tailored to their specific products, significantly reducing build times.