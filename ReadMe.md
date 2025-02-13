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

This approach eliminates the complexity of firmware signing while keeping it safe, efficient, and fully controlled by you.

## Key preservation
* **Secure key storage recommendation**: While we suggest storing signing keys as GitHub private variables, we also recommend encrypting and backing them up on portable storage in a secure location (e.g., a safe deposit box) for worst-case recovery.
