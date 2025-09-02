function checkCryptoSupport(): void {
    let error = false;
    if (window.crypto?.subtle?.importKey == null) {
        console.log("ERROR: window.crypto.subtle.encrypt is missing");
        error = true;
    }
    if (window.crypto?.subtle?.deriveKey == null) {
        console.log("ERROR: window.crypto.subtle.deriveKey is missing");
        error = true;
    }
    if (window.crypto?.subtle?.encrypt == null) {
        console.log("ERROR: window.crypto.subtle.encrypt is missing");
        error = true;
    }

    if (error) {
        const msg =
            "UNSUPPORTED! - Peek requires a secure context (HTTPS or" +
            " localhost)" +
            " for the user plugin to work";
        // This is a deal-breaker, use alert which stops the app running
        alert(msg);
        throw new Error(msg);
    }
}

export class CryptoUtil {
    private static readonly PBKDF2_ITERATIONS = 100000;
    private static readonly SALT_LENGTH = 16;
    private static readonly IV_LENGTH = 12;

    /**
     * Encrypts a message using AES-256-GCM with PBKDF2 key derivation
     * @param message The message to encrypt
     * @param passphrase The passphrase to derive the key from
     * @returns Promise<string> The encrypted message in base64 format
     */
    static async encryptAES256GCM(
        message: string,
        passphrase: string,
    ): Promise<string> {
        const encoder = new TextEncoder();
        const passphraseKey = encoder.encode(passphrase);
        const messageBytes = encoder.encode(message);

        // Import passphrase for PBKDF2
        checkCryptoSupport();
        const importedKey = await window.crypto.subtle.importKey(
            "raw",
            passphraseKey,
            { name: "PBKDF2" },
            false,
            ["deriveKey"],
        );

        // Generate salt and derive key
        const salt = window.crypto.getRandomValues(
            new Uint8Array(this.SALT_LENGTH),
        );
        checkCryptoSupport();
        const derivedKey = await window.crypto.subtle.deriveKey(
            {
                name: "PBKDF2",
                salt,
                iterations: this.PBKDF2_ITERATIONS,
                hash: "SHA-256",
            },
            importedKey,
            { name: "AES-GCM", length: 256 },
            true,
            ["encrypt", "decrypt"],
        );

        // Generate IV and encrypt
        const iv = window.crypto.getRandomValues(
            new Uint8Array(this.IV_LENGTH),
        );
        checkCryptoSupport();
        const ciphertext = await window.crypto.subtle.encrypt(
            { name: "AES-GCM", iv: iv },
            derivedKey,
            messageBytes,
        );

        // Combine components: salt + iv + ciphertext(includes auth tag)
        const combined = new Uint8Array([
            ...salt,
            ...iv,
            ...new Uint8Array(ciphertext),
        ]);

        return this.convertUint8ArrayToBase64(combined);
    }

    /**
     * Decrypts a message encrypted with AES-256-GCM and PBKDF2
     * @param encodedMessage The base64 encoded encrypted message
     * @param passphrase The passphrase used for encryption
     * @returns Promise<string> The decrypted message
     */
    static async decryptAES256GCM(
        encodedMessage: string,
        passphrase: string,
    ): Promise<string> {
        const combined = this.convertBase64ToUint8Array(encodedMessage);

        // Extract components
        const salt = combined.slice(0, this.SALT_LENGTH);
        const iv = combined.slice(
            this.SALT_LENGTH,
            this.SALT_LENGTH + this.IV_LENGTH,
        );
        const ciphertext = combined.slice(this.SALT_LENGTH + this.IV_LENGTH);

        // Import passphrase for PBKDF2
        const encoder = new TextEncoder();
        const passphraseKey = encoder.encode(passphrase);
        checkCryptoSupport();
        const importedKey = await window.crypto.subtle.importKey(
            "raw",
            passphraseKey,
            { name: "PBKDF2" },
            false,
            ["deriveKey"],
        );

        // Derive key using same parameters
        checkCryptoSupport();
        const derivedKey = await window.crypto.subtle.deriveKey(
            {
                name: "PBKDF2",
                salt,
                iterations: this.PBKDF2_ITERATIONS,
                hash: "SHA-256",
            },
            importedKey,
            { name: "AES-GCM", length: 256 },
            true,
            ["encrypt", "decrypt"],
        );

        // Decrypt
        checkCryptoSupport();
        const decrypted = await window.crypto.subtle.decrypt(
            { name: "AES-GCM", iv },
            derivedKey,
            ciphertext,
        );

        return new TextDecoder().decode(new Uint8Array(decrypted));
    }

    /**
     * Converts a Uint8Array to a base64 string
     */
    private static convertUint8ArrayToBase64(data: Uint8Array): string {
        return window.btoa(String.fromCharCode(...data));
    }

    /**
     * Converts a base64 string to a Uint8Array
     */
    private static convertBase64ToUint8Array(b64String: string): Uint8Array {
        const binaryString = window.atob(b64String);
        const result = new Uint8Array(binaryString.length);

        for (let i = 0; i < binaryString.length; i++) {
            result[i] = binaryString.charCodeAt(i);
        }

        return result;
    }

    /**
     * Tests the encryption/decryption functionality
     */
    static async testAES(): Promise<void> {
        try {
            const originalText = "Hello, 世界";
            const passphrase = "my-secret-key";

            const encoded = await this.encryptAES256GCM(
                originalText,
                passphrase,
            );

            const decrypted = await this.decryptAES256GCM(encoded, passphrase);

            const result = originalText === decrypted ? "✅ PASS" : "❌ FAILED";

            console.debug(
                `AES-GCM-256 test ${result} - `,
                "original:",
                originalText,
                "decrypted:",
                decrypted,
                "\nencoded base64 text:",
                encoded,
            );
        } catch (e) {
            console.error("Error in testAES():", e);
        }
    }
}
