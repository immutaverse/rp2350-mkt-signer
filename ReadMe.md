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

** Broken Link (above and below) or private repository **

Sourced from [do-sign.yml](https://github.com/immutaverse/rp2350-ex-mkt-sign-via-action/blob/main/.github/do-sign.yml) Please look there for the most current version

<!-- TODO: Add a script to auto pull and update README when this file has changed https://github.com/immutaverse/rp2350-ex-mkt-sign-via-action/blob/main/.github/do-sign.yml -->


```
uses: actions/rp2350-firmware-signer@v0.004
  with:
    # Path to the previously generated uf2 firmware file  ** Are only uf2 files supported? **
    FIRMWARE: 'unsigned/blink_fast.uf2'

    # 'sign' to sign an existing firmware file.
    # 'build' to build the firmware from source and sign it.   ** Build option is not well explained **
    #   if the PRIVATE_KEY is provided.
    BUILD_ACTION: 'sign'
    
    #Base64 encoded private key normally loaded from
    #github secret but you can provide it from 
    #any source. 
    PRIVATE_KEY: ${{ secrets.RP2350_SAMPLE_PRIVATE_KEY }}
    
    # Path to otp firmare options file that will be 
    # updated with public key for signing.
    OTP_FILE: signed/blink_fast.otp.json          ** Is this required? What if this json file isn't created by the build? **

    #  this is the boardname passed into the build
    #  scripts.  normally only used when build_action
    #  is set to build.  May not be needed for 
    #  sign only events.
    BOARD_NAME: 'pico2'

    # source directory containing source code to build
    #  with the SDK file.  Mandatory when build_action 
    #  is set to build. This is the directory where 
    #  you have saved your CMakeLists.txt See and example    ** Are only CMake builds supported? **
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

  ** It is not clear what directories will be visible to the docker image **

### Outputs
* At same path and name as input firmware the signed
  firmware is written with base_name.uf2 converted to
  base_name.signed.uf2.
                       ** suggestion of an "immutaverse_outputs" directory to make it clear what is created.
                          makes it easier for developers to ensure that nothing changes outside of what is expected to **
* The OTP file specified in input is udpated with public key    ** What if not available?  **
* At same path and name as input firmware a script to 
  blow the fuses and force the cpu to only accept software
  singed with the private key is written.  base_name.uf2 
  is changed to base_name.sec-boot-blow-fuses.sh  this
  script will only run on machines where picotool has been
  successfully installed.                                       ** only supports picotool?  (that's fine, but suggest having a "supported platforms" section that can be referred to in the introduction) **


## One time steps for each Product or Model
A product (or model) is a unique piece of hardware that requires signed firmware for deployment. The best practice is to generate a new signing key for each major product release and approximately once a year. While many companies use a single signing key per model number, a more secure approach is to use distinct signing keys for each major update and annual refresh.

This strategy enhances security by limiting the scope of impact in the event of a key compromise. However, it also requires careful management of multiple signed firmware versions to ensure each device receives the correct update. Over time, the number of signed firmware versions grows, increasing the complexity of maintaining and distributing the right version to each device.

For many companies, managing this internally can be costly and operationally challenging. [Immutaverse](mailto:sales@immutaverse.com) offers enterprise-grade services to streamline this process, ensuring the correct signed firmware is delivered while reducing the key-tracking burden on internal teams.

These steps are as follows:
1.  You create signing keys in your secure environment.  (Immutaverse provides example commands)
1.  You save the private signing key as a GitHub secret.
1.  You back-up the private signing key in a HSM or encrypted on
   portable media in a physically secure location (e.g. safe deposit box).
   It is critical for security that this key never leaks and that you can not lose access 
   to it even under worst case natural disasters.
1.  You record the git variable to model # mapping in your master 
   keys spreadsheet.  This is a important audit and recovery 
   asset.            ** Is this something Immutaverse can provide?  Sounds like it in the previous paragraph about enterprise-grade services **
1.  You tell the your develpment teams what GitHub variable to reference 
   for signing.   ** Same as last question -- can Immutaverse help with this by just mapping based on a version number or name? **

## Steps for each new repository project 
*  You create your github.com repository with your firmware files
*  You update your GitHub Action (** Immutaverse only supports GH Actions, correct? **) to build the firmware file.  For pico2 this
   is a uf2 file. 
   * We also offer pre-built actions along with our pre-built toolchain
     and SDK files to greatly simplify the process of building your 
     source to produce the firmware file.                      ** Need more info - a separate section? **
*  You add the Immutaverse GH Action to call our firmware signer for your chipset.
   * Generate the starting OTP flash settings we will add 
     secure boot settings to this file.  ** See earlier notes about this question **
*  Add a step to your GitHub Action to save the Immutaverse directory ( ** see above note about the directory structure ** ) to a location where you can make it available for download to update your devices
*  Run your GitHub Action.  Immutaverse will automatically:
   * Generate a new signed firmware file.
   * Write a new otp file used to flash the public key to your hardware.
     This step also fuses the hardware into a mode where it will
     only run signed firmware.
   * Write a new script that will flash the public key to your hardware 
     and require secure boot.            ** It isn't immediately clear that this is different from the previous bullet **

** As a future step, may consider having automatic OTA as an Immutaverse offering -- in other words, the signed versions are saved on a server owned by Immutaverse -- Immutaverse can offer a script to add to the firmware to automatically get updates -- or perhaps a firmware wrapper that does so on boot (a lot more complex to develop but further simplifies the use case for customers) **

## Key preservation
* **Secure key storage recommendation**: While we suggest storing signing keys as GitHub private variables, we also recommend encrypting and backing them up on portable storage in a secure location (e.g., a safe deposit box) for worst-case recovery.   ** This duplicates information above -- maybe have that above reference refer to this section instead **

# Secure and Reproducible Firmware Builds

** This section is great for motivation as to why do this, but it's buried under the technical stuff that only the developers will read.  Maybe move it to the top, or put it in a linked .md file that is "stuff for fringe-technical people to read" **

Many companies rely on ad-hoc, desktop-based build environments tied to specific IDEs and local configurations. This approach introduces several risks:
* Fragile Build Environments – When a build environment breaks, diagnosing and fixing issues often requires the most senior (and expensive) engineers, leading to costly downtime.
* Unpredictable Toolchain Changes – Over time, variations in libraries, linkers, and compilers can introduce subtle, hard-to-track differences in firmware behavior.
* Security Vulnerabilities – A compromised developer machine could introduce malware-modified components into the firmware, creating an attack vector that is difficult to detect.  ** suggest using the words "supply side attacks" since this is buzzword-y and on people's minds **
* Dependency Conflicts & SDK Installation Issues – Installing SDKs and toolchains on a workstation can lead to dependency conflicts with other software, causing unexpected failures. Debugging these issues can take days and may require fully reinstalling the OS just to get a clean build environment.
### Best Practice: Containerized, Reproducible Builds
To mitigate these risks, Immutaverse uses clean, containerized build environments with well-defined and auditable toolchains. The Immutaverse approach leverages Docker-based builds triggered directly within GitHub Actions, ensuring:
* Consistent and Reproducible Builds – Each build runs in a fresh, isolated container with a locked-down toolchain, preventing unexpected drift.
* Increased Security – The entire build process occurs within GitHub’s infrastructure, eliminating reliance on potentially compromised developer workstations or long-lived build servers.
* Simplified CI/CD Integration – Automated builds ensure that every firmware version is compiled in a controlled, repeatable manner.
Elimination of SDK/Toolchain Conflicts – Every build starts from a known, clean state, ensuring that SDK installations and dependencies do not conflict with other software on a developer’s machine.

To simplify this process, [Immutaverse](mailto:sales@immutaverse.com) provides pre-built GitHub Actions, toolchains, and SDK files, allowing you to easily integrate a fully managed and secure build process into your CI/CD pipeline.

Complex SDK Dependencies – Many SDKs require dozens to hundreds of dependencies, making build environments large and difficult to manage. Setting up these dependencies directly within GitHub Actions on every build is slow and inefficient. By bundling everything into pre-built Docker images, we provide a complete, working toolchain that is frozen at a known version. At the same time, we regularly release new images with updated libraries, allowing teams to upgrade at their own pace—testing new versions safely without jeopardizing their existing build environments.
** This above is great, but doesn't fit here - integrate into the above section **

For enterprise-grade customers, we also offer custom-built images with pre-downloaded libraries tailored to their specific products, significantly reducing build times.
